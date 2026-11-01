#!/usr/bin/env python3
"""EU4 loading screens -> EU5 loading-screen scenes (pure stdlib, no deps).

EU4 side (source of truth):
    <src>/*.dds           2048x1536, DXT1 (mip0), artwork baked inside a gold
                          frame; inner art window = (47,228)-(2000,1306),
                          i.e. 1954x1079 = aspect 1.811.

EU5 side (target):
    <mod>/loading_screen/gfx/loading_screen_assets/th/images/loading_screen_th_NN.dds
    <mod>/loading_screen/gfx/images/00_loading_screen_th.txt
    <mod>/loading_screen/gfx/scenes/th_loading_screens.txt

Why the crop rectangle is block aligned (64,228,1920,1076):
    DXT1 is 4x4 blocks, so a 4-px aligned rectangle can be copied *verbatim*
    from the source mip0 - the base level loses nothing at all, and only the
    mip chain has to be re-encoded.  1920x1076 = 1.7846 vs 16:9 = 1.7778
    (0.4% off), which is well inside what the illustration quad tolerates.

Usage:
    python loading_screen_pipeline.py --src SRC --dst MODROOT
        [--only load_12] [--preview] [--no-defs]
"""
import argparse
import os
import struct
import sys
import zlib

# --- EU4 source geometry -----------------------------------------------------
SRC_W, SRC_H = 2048, 1536
# gold frame window measured on 46/47 files: (47,228)-(2000,1306)
ART_X0, ART_Y0, ART_X1, ART_Y1 = 47, 228, 2000, 1306

# --- EU5 target geometry ----------------------------------------------------
FRAME_CROP = (64, 228, 1920, 1076)     # x, y, w, h   (block aligned, 1.785:1)
FLAT_CROP = (0, 192, 2048, 1152)       # frameless cards -> 16:9 exact

DDS_HEADER_SIZE = 128


# ---------------------------------------------------------------------------
# DDS reading
# ---------------------------------------------------------------------------
def read_dds(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'DDS ':
        raise ValueError(f'not a DDS: {path}')
    h = struct.unpack_from('<I', data, 12)[0]
    w = struct.unpack_from('<I', data, 16)[0]
    mips = struct.unpack_from('<I', data, 28)[0]
    fourcc = data[84:88]
    return w, h, mips, fourcc, data


def block_palette(c0, c1):
    r0 = ((c0 >> 11) & 0x1F) * 255 // 31
    g0 = ((c0 >> 5) & 0x3F) * 255 // 63
    b0 = (c0 & 0x1F) * 255 // 31
    r1 = ((c1 >> 11) & 0x1F) * 255 // 31
    g1 = ((c1 >> 5) & 0x3F) * 255 // 63
    b1 = (c1 & 0x1F) * 255 // 31
    if c0 > c1:
        return (((r0 << 16) | (g0 << 8) | b0),
                ((r1 << 16) | (g1 << 8) | b1),
                (((2 * r0 + r1) // 3 << 16) | ((2 * g0 + g1) // 3 << 8) | ((2 * b0 + b1) // 3)),
                (((r0 + 2 * r1) // 3 << 16) | ((g0 + 2 * g1) // 3 << 8) | ((b0 + 2 * b1) // 3)))
    return (((r0 << 16) | (g0 << 8) | b0),
            ((r1 << 16) | (g1 << 8) | b1),
            (((r0 + r1) // 2 << 16) | ((g0 + g1) // 2 << 8) | ((b0 + b1) // 2)),
            0)


def decode_dxt1(data, w, h, off=0):
    """Decode a DXT1 surface to a w*h*3 RGB bytearray."""
    bx_n = (w + 3) // 4
    by_n = (h + 3) // 4
    out = bytearray(w * h * 3)
    p = off
    for by in range(by_n):
        y0 = by * 4
        for bx in range(bx_n):
            c0, c1 = struct.unpack_from('<HH', data, p)
            idx = struct.unpack_from('<I', data, p + 4)[0]
            p += 8
            pal = block_palette(c0, c1)
            x0 = bx * 4
            for py in range(4):
                y = y0 + py
                if y >= h:
                    break
                row = y * w
                base = 2 * (py * 4)
                for px in range(4):
                    x = x0 + px
                    if x >= w:
                        break
                    col = pal[(idx >> (base + 2 * px)) & 3]
                    j = (row + x) * 3
                    out[j] = (col >> 16) & 0xFF
                    out[j + 1] = (col >> 8) & 0xFF
                    out[j + 2] = col & 0xFF
    return out


# ---------------------------------------------------------------------------
# BC1 encoding (min/max endpoints, 4-colour block, always opaque)
# ---------------------------------------------------------------------------
def _to565(r, g, b):
    return (((r * 31 + 127) // 255) << 11) | (((g * 63 + 127) // 255) << 5) | ((b * 31 + 127) // 255)


def encode_bc1(rgb, w, h):
    bx_n = (w + 3) // 4
    by_n = (h + 3) // 4
    out = bytearray(bx_n * by_n * 8)
    p = 0
    for by in range(by_n):
        y0 = by * 4
        for bx in range(bx_n):
            x0 = bx * 4
            rmin, gmin, bmin = 255, 255, 255
            rmax, gmax, bmax = 0, 0, 0
            for py in range(4):
                y = y0 + py
                if y >= h:
                    y = h - 1
                row = y * w
                for px in range(4):
                    x = x0 + px
                    if x >= w:
                        x = w - 1
                    j = (row + x) * 3
                    r = rgb[j]; g = rgb[j + 1]; b = rgb[j + 2]
                    if r < rmin: rmin = r
                    if g < gmin: gmin = g
                    if b < bmin: bmin = b
                    if r > rmax: rmax = r
                    if g > gmax: gmax = g
                    if b > bmax: bmax = b
            c0 = _to565(rmax, gmax, bmax)
            c1 = _to565(rmin, gmin, bmin)
            if c0 < c1:
                c0, c1 = c1, c0
            if c0 == c1:
                # keep the 4-colour (opaque) mode: c0 must be > c1
                if c1 > 0:
                    c1 -= 1
                else:
                    c0 += 1
            pal = block_palette(c0, c1)
            p0 = pal[0]; p1 = pal[1]; p2 = pal[2]; p3 = pal[3]
            bits = 0
            shift = 0
            for py in range(4):
                y = y0 + py
                if y >= h:
                    y = h - 1
                row = y * w
                for px in range(4):
                    x = x0 + px
                    if x >= w:
                        x = w - 1
                    j = (row + x) * 3
                    r = rgb[j]; g = rgb[j + 1]; b = rgb[j + 2]
                    best = 1 << 30
                    bi = 0
                    for k, col in enumerate((p0, p1, p2, p3)):
                        dr = r - ((col >> 16) & 0xFF)
                        dg = g - ((col >> 8) & 0xFF)
                        db = b - (col & 0xFF)
                        d = dr * dr + dg * dg + db * db
                        if d < best:
                            best = d
                            bi = k
                    bits |= bi << shift
                    shift += 2
            struct.pack_into('<HHI', out, p, c0, c1, bits & 0xFFFFFFFF)
            p += 8
    return out


# ---------------------------------------------------------------------------
# DDS writing
# ---------------------------------------------------------------------------
def write_dds_dxt1(path, w, h, levels):
    """levels: list of (w, h, bytes) from mip0 upward."""
    flags = 0x000A1007           # CAPS|HEIGHT|WIDTH|PIXELFORMAT|LINEARSIZE|MIPMAPCOUNT
    hdr = bytearray(DDS_HEADER_SIZE)
    hdr[0:4] = b'DDS '
    struct.pack_into('<I', hdr, 4, 124)
    struct.pack_into('<I', hdr, 8, flags)
    struct.pack_into('<I', hdr, 12, h)
    struct.pack_into('<I', hdr, 16, w)
    struct.pack_into('<I', hdr, 20, levels[0][2].__len__())   # linear size of mip0
    struct.pack_into('<I', hdr, 28, len(levels))              # mip count
    struct.pack_into('<I', hdr, 76, 32)                       # pixel format size
    struct.pack_into('<I', hdr, 80, 0x4)                      # DDPF_FOURCC
    hdr[84:88] = b'DXT1'
    struct.pack_into('<I', hdr, 108, 0x401008)                # TEXTURE|MIPMAP|COMPLEX
    with open(path, 'wb') as f:
        f.write(hdr)
        for _w, _h, buf in levels:
            f.write(buf)


def mip_dim(w, h, level):
    return max(1, w >> level), max(1, h >> level)


def box_downsample(rgb, w, h):
    """2x2 box average -> (w//2ish, h//2ish)."""
    nw = max(1, w // 2)
    nh = max(1, h // 2)
    out = bytearray(nw * nh * 3)
    for y in range(nh):
        y0 = min(2 * y, h - 1) * w
        y1 = min(2 * y + 1, h - 1) * w
        for x in range(nw):
            x0 = min(2 * x, w - 1)
            x1 = min(2 * x + 1, w - 1)
            a = (y0 + x0) * 3; b = (y0 + x1) * 3
            c = (y1 + x0) * 3; d = (y1 + x1) * 3
            out[(y * nw + x) * 3] = (rgb[a] + rgb[b] + rgb[c] + rgb[d] + 2) >> 2
            out[(y * nw + x) * 3 + 1] = (rgb[a + 1] + rgb[b + 1] + rgb[c + 1] + rgb[d + 1] + 2) >> 2
            out[(y * nw + x) * 3 + 2] = (rgb[a + 2] + rgb[b + 2] + rgb[c + 2] + rgb[d + 2] + 2) >> 2
    return out, nw, nh


# ---------------------------------------------------------------------------
# conversion
# ---------------------------------------------------------------------------
def crop_blocks(data, crop):
    """Copy a 4-px aligned rectangle out of a DXT1 mip0, block by block."""
    x, y, w, h = crop
    if x % 4 or y % 4 or w % 4 or h % 4:
        raise ValueError(f'crop {crop} is not 4-px aligned')
    src_bx = (SRC_W + 3) // 4
    bx0, by0 = x // 4, y // 4
    bx_n, by_n = w // 4, h // 4
    out = bytearray(bx_n * by_n * 8)
    p = 0
    for row in range(by_n):
        src_off = DDS_HEADER_SIZE + ((by0 + row) * src_bx + bx0) * 8
        out[p:p + bx_n * 8] = data[src_off:src_off + bx_n * 8]
        p += bx_n * 8
    return out


def is_framed(data):
    """Sample the middle row: a framed card starts with the patterned border
    then a gold band; a full-bleed card has no wide gold band at x<47."""
    w, h = SRC_W, SRC_H
    bx_n = (w + 3) // 4
    by = (h // 2) // 4
    off = DDS_HEADER_SIZE + by * bx_n * 8
    gold = 0
    for bx in range(2):                       # first 8 px of the middle row
        c0, c1 = struct.unpack_from('<HH', data, off + bx * 8)
        idx = struct.unpack_from('<I', data, off + bx * 8 + 4)[0]
        pal = block_palette(c0, c1)
        for px in range(4):
            col = pal[idx & 3]
            idx >>= 2
            r = (col >> 16) & 0xFF; g = (col >> 8) & 0xFF; b = col & 0xFF
            if r >= 120 and g >= 90 and b <= 70 and (r - b) >= 45:
                gold += 1
    return gold >= 5


def convert_one(src_path, out_path, preview=None):
    w, h, mips, fourcc, data = read_dds(src_path)
    if (w, h) != (SRC_W, SRC_H):
        raise ValueError(f'unexpected size {w}x{h} (expected {SRC_W}x{SRC_H})')
    if fourcc != b'DXT1':
        raise ValueError(f'unsupported fourCC {fourcc!r}')

    framed = is_framed(data)
    crop = FRAME_CROP if framed else FLAT_CROP
    cw, ch = crop[2], crop[3]

    levels = [(cw, ch, crop_blocks(data, crop))]
    rgb = decode_dxt1(levels[0][2], cw, ch)
    if preview:
        write_png(preview, cw, ch, rgb)

    cw2, ch2 = cw, ch
    level = 0
    while cw2 > 1 or ch2 > 1:
        rgb, cw2, ch2 = box_downsample(rgb, cw2, ch2)
        levels.append((cw2, ch2, encode_bc1(rgb, cw2, ch2)))
        level += 1

    write_dds_dxt1(out_path, cw, ch, levels)
    return framed, crop, len(levels), os.path.getsize(out_path)


def write_png(path, w, h, rgb):
    def chunk(tag, payload):
        return (struct.pack('>I', len(payload)) + tag + payload +
                struct.pack('>I', zlib.crc32(tag + payload) & 0xFFFFFFFF))
    raw = b''.join(b'\x00' + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


# ---------------------------------------------------------------------------
# definition files
# ---------------------------------------------------------------------------
IMAGES_HEADER = """## Touhou Universalis II - loading screen textures (EU5)
## generated by tools/loading_screen_pipeline.py
## source: Touhou Universalis Updated (CN) 3.4.2 (Steam workshop 1635373831, EU4)
## one flat 16:9 texture per scene - single layer, camera untouched.

"""

SCENES_HEADER = """## Touhou Universalis II - loading screen scenes (EU5)
## generated by tools/loading_screen_pipeline.py
##
## FILENAME IS THE SWITCH:
##   00_loading_screens.txt  -> same path as vanilla, so the mod file REPLACES
##                              vanilla's scene list: only TH scenes remain.
##   th_loading_screens.txt  -> additive: vanilla's 11 scenes stay in the pool.
## A loading-screen module file at the same path as a game file overrides it
## (that is how loading_screen/common/defines/00_defines.txt already works).
##
## Each scene uses only layer_1_mesh (frontmost plane) + illustration_override_anims,
## so the texture is drawn 1:1 onto a 16:9 quad.
## camera_near_far is kept at the vanilla value: layer_1 sits at z=+1.225 while
## the camera looks from z=-125, so a near plane of 1000 (the value the ACGV mod
## uses) would clip it.  If a scene renders black/bg-only, try
## {1000 10000} or {1000 5000} instead.

"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', help='EU4 gfx/loadingscreens directory (required unless --defs-only)')
    ap.add_argument('--dst', required=True, help='mod root (contains loading_screen/)')
    ap.add_argument('--only', default=None, help='only convert one source basename')
    ap.add_argument('--limit', type=int, default=0, help='convert at most N files')
    ap.add_argument('--preview', action='store_true', help='also write PNG previews')
    ap.add_argument('--out-subdir', default='th', help='asset subfolder under loading_screen_assets')
    ap.add_argument('--defs-only', action='store_true',
                    help='only rewrite the definition files from the already converted DDS set')
    args = ap.parse_args()

    asset_dir = os.path.join(args.dst, 'loading_screen', 'gfx', 'loading_screen_assets',
                             args.out_subdir, 'images')
    prev_dir = os.path.join(args.dst, '.tmp', 'ls_preview')
    os.makedirs(asset_dir, exist_ok=True)

    if args.defs_only:
        found = sorted(f for f in os.listdir(asset_dir) if f.lower().endswith('.dds'))
        entries = []
        for name in found:
            scene = os.path.splitext(name)[0].replace('loading_screen_', '')
            entries.append((f'loading_screen_{scene}_layer1', scene))
        emit_defs_2(entries, os.path.join(args.dst, 'loading_screen'))
        print(f'[defs] {len(entries)} scenes rewritten from {asset_dir}')
        return 0

    if args.preview:
        os.makedirs(prev_dir, exist_ok=True)

    files = sorted(f for f in os.listdir(args.src) if f.lower().endswith('.dds'))
    if args.only:
        files = [f for f in files if os.path.splitext(f)[0] == args.only]
    if args.limit:
        files = files[:args.limit]

    def sort_key(name):
        stem = os.path.splitext(name)[0]
        try:
            return (0, int(stem.split('_')[-1]))
        except ValueError:
            return (1, 0)

    files.sort(key=sort_key)

    entries = []
    for name in files:
        stem = os.path.splitext(name)[0]
        try:
            idx = int(stem.split('_')[-1])
        except ValueError:
            idx = 0
        scene = f'th_{idx:02d}'
        img_key = f'loading_screen_{scene}_layer1'
        tex = f'gfx/loading_screen_assets/{args.out_subdir}/images/loading_screen_{scene}.dds'
        out = os.path.join(asset_dir, f'loading_screen_{scene}.dds')
        prev = os.path.join(prev_dir, f'loading_screen_{scene}.png') if args.preview else None
        framed, crop, nlev, size = convert_one(os.path.join(args.src, name),
                                               out, preview=prev)
        print(f'{name:14s} -> loading_screen_{scene}.dds  framed={int(framed)} '
              f'crop={crop} mips={nlev} {size/1048576:.2f} MB')
        entries.append((img_key, scene))

    if not args.only:
        emit_defs_2(entries, os.path.join(args.dst, 'loading_screen'))
        print(f'\n[defs] {len(entries)} scenes written to loading_screen/gfx/{{images,scenes}}')
    else:
        print('\n[defs] --only given, definition files not rewritten')


def emit_defs_2(entries, ls_root):
    img_dir = os.path.join(ls_root, 'gfx', 'images')
    scn_dir = os.path.join(ls_root, 'gfx', 'scenes')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(scn_dir, exist_ok=True)
    with open(os.path.join(img_dir, '00_loading_screen_th.txt'), 'w',
              encoding='utf-8', newline='\n') as f:
        f.write(IMAGES_HEADER)
        for img_key, scene in entries:
            f.write(f'{img_key} = {{\n')
            f.write('\tillustration_image = {\n')
            f.write(f'\t\ttexture_file = "gfx/loading_screen_assets/th/images/loading_screen_{scene}.dds"\n')
            f.write('\t\tpriority = 1\n\t\tweight = 1\n\t}\n')
            f.write(f'\ttag = "{img_key}"\n')
            f.write('}\n')
    with open(os.path.join(scn_dir, '00_loading_screens.txt'), 'w',
              encoding='utf-8', newline='\n') as f:
        f.write(SCENES_HEADER)
        for img_key, scene in entries:
            f.write(f'\nloading_screen_scene_{scene} = {{\n')
            f.write('\tecs_illustration_image = {\n')
            f.write(f'\t\tlist = "{img_key}"\n')
            f.write('\t\tpdxmesh = "layer_1_mesh"\n')
            f.write('\t\tname = "illustration_override_anims" #schematic\n')
            f.write('\t}\n\n')
            f.write('\tgfx_environment_file = "gfx/illustrations/environment2.txt"\n\n')
            f.write('\tcamera = {\n')
            f.write('\t\tcamera_near_far = {0.11 100000}\n')
            f.write('\t\tcamera_fov_y_degrees = 37.5\n')
            f.write('\t\tcamera_position = {0 0 -125}\n')
            f.write('\t\tcamera_look_at = {0 0 1000}\n')
            f.write('\t}\n')
            f.write('}\n')


if __name__ == '__main__':
    sys.exit(main())
