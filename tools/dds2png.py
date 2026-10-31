#!/usr/bin/env python3
"""Convert DDS (RGBA32 / DXT1 / DXT5) to PNG using only stdlib (zlib)."""
import struct, sys, zlib, os, math

def read_dds(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'DDS ', f"not a DDS: {path}"
    height, width = struct.unpack_from('<II', data, 12)
    pitch = struct.unpack_from('<I', data, 20)[0]
    mips = struct.unpack_from('<I', data, 28)[0]
    pf_flags = struct.unpack_from('<I', data, 80)[0]
    fourcc = data[84:88]
    bpp = struct.unpack_from('<I', data, 88)[0]
    return width, height, pitch, mips, pf_flags, fourcc, bpp, data

def rgba_to_png(width, height, pixels):
    def chunk(tag, payload):
        c = struct.pack('>I', len(payload)) + tag + payload
        return c + struct.pack('>I', zlib.crc32(tag + payload) & 0xffffffff)
    raw = b''
    for y in range(height):
        row = bytes(pixels[y * width * 4:(y + 1) * width * 4])
        raw += b'\x00' + row
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
            chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

def decode_rgba(width, height, mips, data):
    # use only the largest mip level
    level_size = width * height * 4
    off = 128
    px = bytearray(data[off:off + level_size])
    return px

def decode_dxt(width, height, fourcc, data, pitch):
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
                r = ((v >> 11) & 0x1f) * 255 // 31
                g = ((v >> 5) & 0x3f) * 255 // 63
                b = (v & 0x1f) * 255 // 31
                return (r, g, b)
            c = [rgb565(c0), rgb565(c1)]
            if c0 > c1:
                c += [tuple((2 * c[0][i] + c[1][i]) // 3 for i in range(3)),
                      tuple((c[0][i] + 2 * c[1][i]) // 3 for i in range(3))]
                alpha_mode = False
            else:
                c += [tuple((c[0][i] + c[1][i]) // 2 for i in range(3)), (0, 0, 0)]
                alpha_mode = True
            def alpha_for(code):
                if is_dxt5:
                    if code == 0: return a0
                    if code == 1: return a1
                    if a0 > a1:
                        return ((8 - code) * a0 + (code - 1) * a1) // 7
                    if code >= 6: return 0 if code == 7 else a0 // 2
                    return ((6 - code) * a0 + (code - 1) * a1) // 5
                else:
                    if alpha_mode and code == 3: return 0
                    return 255
            for py in range(4):
                for px_ in range(4):
                    code = (idx[py] >> (px_ * 2)) & 3
                    r, g, b = c[code]
                    a = alpha_for(code)
                    x = bx * 4 + px_
                    y = by * 4 + py
                    if x < width and y < height:
                        i = (y * width + x) * 4
                        px[i], px[i + 1], px[i + 2], px[i + 3] = r, g, b, a
    return px

def main():
    src_dir = r"F:\SITU\东方风云设计理念\国家旗帜"
    out_dir = sys.argv[1] if len(sys.argv) > 1 else r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\.tmp\flag_preview"
    os.makedirs(out_dir, exist_ok=True)
    files = [os.path.join(src_dir, n) for n in os.listdir(src_dir) if n.lower().endswith('.dds')]
    files += [
        r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\gfx\coat_of_arms\textured_emblems\T00_embleme_1.dds",
        r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\gfx\coat_of_arms\textured_emblems\T05_embleme_1.dds",
        r"F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\main_menu\gfx\coat_of_arms\textured_emblems\T08_embleme_1.dds",
    ]
    for f in files:
        try:
            width, height, pitch, mips, pf_flags, fourcc, bpp, data = read_dds(f)
            if fourcc in (b'DXT1', b'DXT5'):
                px = decode_dxt(width, height, fourcc, data, pitch)
            else:
                px = decode_rgba(width, height, mips, data)
            png = rgba_to_png(width, height, px)
            out = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0] + '.png')
            with open(out, 'wb') as fh:
                fh.write(png)
            print(f"OK  {os.path.basename(f):30s} -> {os.path.basename(out)}  ({width}x{height} {fourcc.decode() or 'RGBA'})")
        except Exception as e:
            print(f"ERR {os.path.basename(f)}: {e}")

if __name__ == '__main__':
    main()
