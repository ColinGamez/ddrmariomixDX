"""Dump all bitmap textures from an HSFV037 chunk to PNGs.
Usage: hsf_dump_textures.py <chunk.bin> <outdir>
"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsf2obj import HSF
import gxtexture
from PIL import Image

def main(path, outdir):
    hsf = HSF(open(path, 'rb').read())
    d = hsf.d
    bosfs, bcnt = hsf.sec['bitmap']
    if bcnt <= 0:
        print('no bitmaps')
        return
    os.makedirs(outdir, exist_ok=True)

    # palettes: records of {u32 name, u32 unk, u32 palSize, u32 data_ofs}, data after array
    pals = {}
    posfs, pcnt = hsf.sec['palette']
    if pcnt > 0:
        pbase = posfs + pcnt * 16
        for i in range(pcnt):
            nofs, unk, psz, dofs = struct.unpack('>4I', d[posfs + i * 16: posfs + i * 16 + 16])
            pals[hsf.name(nofs)] = (psz, pbase + dofs)

    data_base = bosfs + bcnt * 32
    for i in range(bcnt):
        r = d[bosfs + i * 32: bosfs + i * 32 + 32]
        nofs, maxlod = struct.unpack('>2I', r[:8])
        fmt, pix = r[8], r[9]
        sx, sy, pal_sz = struct.unpack('>3H', r[10:16])
        tint, pal_data, unk, data_ofs = struct.unpack('>4I', r[16:32])
        name = hsf.name(nofs) or f'tex{i:03d}'
        pdata = d[data_base + data_ofs: data_base + data_ofs + sx * sy * 4]
        palette = None
        if fmt in (9, 10, 11):  # CI8, find palette by matching name or first
            for pname, (psz, pofs) in pals.items():
                palette = [struct.unpack('>H', d[pofs + j * 2: pofs + j * 2 + 2])[0]
                           for j in range(psz)]
                break
        try:
            px = gxtexture.decode(fmt, pdata, sx, sy, palette)
        except Exception as e:
            print(f'{name}: decode failed ({e})')
            continue
        img = px
        img.save(os.path.join(outdir, name + '.png'))
        print(f'{name}: fmt {fmt} {sx}x{sy} -> {outdir}/{name}.png')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
