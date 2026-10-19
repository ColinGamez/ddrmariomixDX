"""GX texture decoders (GameCube formats used in HSF bitmaps).
Formats: 0 I4, 1 I8, 2 IA4, 3 IA8, 4 RGB565, 5 RGB5A3, 6 RGBA8, 7 CMPR(DXT1),
9/10/11 = CI8/CI4 palette variants.
Tiles are 8x8 for I4/IA4/CI4? (GX tile sizes: I4/CI4 8x8, I8/IA4/CI8 8x4,
IA8/RGB565/RGB5A3 4x4, RGBA8 4x4 pairs, CMPR 8x8 blocks of two 4x4).
"""
import struct
from PIL import Image

def _rgb565(v):
    r = (v >> 11) & 31; g = (v >> 5) & 63; b = v & 31
    return (r * 255 // 31, g * 255 // 63, b * 255 // 31, 255)

def _rgb5a3(v):
    if v & 0x8000:
        r = (v >> 10) & 31; g = (v >> 5) & 31; b = v & 31
        return (r * 255 // 31, g * 255 // 31, b * 255 // 31, 255)
    a = (v >> 12) & 7
    r = (v >> 8) & 15; g = (v >> 4) & 15; b = v & 15
    return (r * 17, g * 17, b * 17, a * 255 // 7)

def decode(fmt, data, w, h, palette=None):
    img = Image.new('RGBA', (w, h))
    px = img.load()
    if fmt in (4, 5):  # RGB565 / RGB5A3: 4x4 tiles, 2 bpp
        conv = _rgb565 if fmt == 4 else _rgb5a3
        i = 0
        for ty in range(0, h, 4):
            for tx in range(0, w, 4):
                for y in range(4):
                    for x in range(4):
                        v = struct.unpack('>H', data[i:i + 2])[0]; i += 2
                        if tx + x < w and ty + y < h:
                            px[tx + x, ty + y] = conv(v)
    elif fmt == 7:  # CMPR: 8x8 supertiles of 4 4x4 BC1 blocks
        i = 0
        for ty in range(0, h, 8):
            for tx in range(0, w, 8):
                for b in range(4):
                    bx = tx + (b % 2) * 4; by = ty + (b // 2) * 4
                    c0, c1, bits = struct.unpack('>HHI', data[i:i + 8]); i += 8
                    pal = [_rgb565(c0), _rgb565(c1)]
                    if c0 > c1:
                        pal.append(tuple((2 * pal[0][k] + pal[1][k]) // 3 for k in range(3)) + (255,))
                        pal.append(tuple((pal[0][k] + 2 * pal[1][k]) // 3 for k in range(3)) + (255,))
                    else:
                        pal.append(tuple((pal[0][k] + pal[1][k]) // 2 for k in range(3)) + (255,))
                        pal.append((0, 0, 0, 0))
                    for y in range(4):
                        row = (bits >> (y * 8)) & 0xFF
                        for x in range(4):
                            ci = (row >> (x * 2)) & 3
                            if bx + x < w and by + y < h:
                                px[bx + x, by + y] = pal[ci]
    elif fmt == 6:  # RGBA8: 4x4 tiles, 64B/tile: 32B of A,R pairs then 32B of G,B pairs
        i = 0
        for ty in range(0, h, 4):
            for tx in range(0, w, 4):
                ar = data[i:i + 32]; gb = data[i + 32:i + 64]; i += 64
                for y in range(4):
                    for x in range(4):
                        j = (y * 4 + x) * 2
                        if tx + x < w and ty + y < h:
                            px[tx + x, ty + y] = (ar[j + 1], gb[j + 1], gb[j], ar[j])
    elif fmt in (9, 10) and palette is not None:  # CI8 -> RGB565 / RGB5A3 palette
        conv = _rgb565 if fmt == 9 else _rgb5a3
        i = 0
        for ty in range(0, h, 4):
            for tx in range(0, w, 8):
                for y in range(4):
                    for x in range(8):
                        ci = data[i]; i += 1
                        if tx + x < w and ty + y < h:
                            px[tx + x, ty + y] = conv(palette[ci]) if ci < len(palette) else (0, 0, 0, 255)
    else:
        raise ValueError(f'fmt {fmt} not implemented')
    return img
