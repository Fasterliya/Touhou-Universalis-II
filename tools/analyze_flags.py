#!/usr/bin/env python3
"""Analyze DDS flag images: alpha coverage, bounding box, color stats (stdlib only)."""
import struct, os, sys

SRC = r"F:\SITU\东方风云设计理念\国家旗帜"
EMB = r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\gfx\coat_of_arms\textured_emblems"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\.tmp\flag_preview"

def load_rgba(path):
    with open(path, 'rb') as f:
        data = f.read()
    height, width = struct.unpack_from('<II', data, 12)
    fourcc = data[84:88]
    if fourcc in (b'DXT1', b'DXT5'):
        is_dxt5 = fourcc == b'DXT5'
        blocks_x = (width + 3) // 4
        blocks_y = (height + 3) // 4
        px = bytearray(width * height * 4)
        off = 128
        for by in range(blocks_y):
            for bx in range(blocks_x):
                if is_dxt5:
                    a0, a1 = data[off], data[off + 1]
                    alphas = data[off + 2:off + 8]
                    off += 8
                c0 = struct.unpack_from('<H', data, off)[0]
                c1 = struct.unpack_from('<H', data, off + 2)[0]
                idx = data[off + 4:off + 8]
                off += 8
                def rgb565(v):
                    return (((v >> 11) & 0x1f) * 255 // 31, ((v >> 5) & 0x3f) * 255 // 63, (v & 0x1f) * 255 // 31)
                c = [rgb565(c0), rgb565(c1)]
                alpha_mode = False
                if c0 > c1:
                    c += [tuple((2 * c[0][i] + c[1][i]) // 3 for i in range(3)),
                          tuple((c[0][i] + 2 * c[1][i]) // 3 for i in range(3))]
                else:
                    c += [tuple((c[0][i] + c[1][i]) // 2 for i in range(3)), (0, 0, 0)]
                    alpha_mode = True
                def alpha_for(code):
                    if is_dxt5:
                        if code == 0: return a0
                        if code == 1: return a1
                        if a0 > a1: return ((8 - code) * a0 + (code - 1) * a1) // 7
                        if code >= 6: return 0 if code == 7 else a0 // 2
                        return ((6 - code) * a0 + (code - 1) * a1) // 5
                    return 0 if (alpha_mode and code == 3) else 255
                for py in range(4):
                    for px_ in range(4):
                        code = (idx[py] >> (px_ * 2)) & 3
                        r, g, b = c[code]
                        a = alpha_for(code)
                        x, y = bx * 4 + px_, by * 4 + py
                        if x < width and y < height:
                            i = (y * width + x) * 4
                            px[i], px[i+1], px[i+2], px[i+3] = r, g, b, a
        return width, height, bytes(px)
    else:
        off = 128
        size = width * height * 4
        return width, height, bytes(data[off:off+size])

def analyze(path):
    w, h, px = load_rgba(path)
    total = w * h
    opaque = transparent = 0
    minx, miny, maxx, maxy = w, h, -1, -1
    rsum = gsum = bsum = 0
    lum_min = 255; lum_max = 0
    edges = 0
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            r, g, b, a = px[i], px[i+1], px[i+2], px[i+3]
            if a >= 250:
                opaque += 1
            elif a <= 5:
                transparent += 1
            if a > 5:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                rsum += r; gsum += g; bsum += b
            lum = (r * 77 + g * 150 + b * 29) >> 8
            if a > 5:
                if lum < lum_min: lum_min = lum
                if lum > lum_max: lum_max = lum
            # edge detection: compare with right neighbor
            if x < w - 1:
                i2 = i + 4
                d = abs(px[i] - px[i2]) + abs(px[i+1] - px[i2+1]) + abs(px[i+2] - px[i2+2])
                if d > 60: edges += 1
    n = opaque + transparent
    cov = total - transparent
    name = os.path.basename(path)
    print(f"{name:24s} {w}x{h} opaque={opaque*100//total:3d}% transparent={transparent*100//total:3d}% "
          f"content_bbox=({minx},{miny})-({maxx},{maxy}) fill={cov*100//total:3d}% "
          f"avgRGB=({rsum//max(cov,1)},{gsum//max(cov,1)},{bsum//max(cov,1)}) lumRange={lum_min}-{lum_max} edgesX={edges}")

files = sorted(os.listdir(SRC))
for f in files:
    if f.lower().endswith('.dds'):
        analyze(os.path.join(SRC, f))
print("--- existing emblems for comparison ---")
for f in ["T00_embleme_1.dds", "T05_embleme_1.dds", "T08_embleme_1.dds", "T14_embleme_1.dds", "T51_embleme_1.dds"]:
    p = os.path.join(EMB, f)
    if os.path.exists(p):
        analyze(p)
