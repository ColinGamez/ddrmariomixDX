"""Smoke tests for the ddrmariomixDX toolchain - runs in CI without game assets.

Builds tiny synthetic fixtures and verifies each parser handles them:
- gxtexture: decode a 4x4 RGB565 tile
- dsp2wav: decode a minimal valid DSP file
- ssq_parse: parse a synthetic 1-section chart chunk
- msm_extract: split a minimal GSND archive
- pdt_extract: extract a minimal PDT stream
"""
import os, struct, sys, tempfile, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

failures = []

def check(name, fn):
    try:
        fn()
        print(f"PASS {name}")
    except Exception as e:
        failures.append(name)
        print(f"FAIL {name}: {e}")

def t_gxtexture():
    import gxtexture
    # 4x4 red RGB565 tile
    data = struct.pack('>16H', *([0xF800] * 16))
    img = gxtexture.decode(4, data, 4, 4)
    assert img.size == (4, 4)
    px = img.convert('RGBA').load()
    assert px[0, 0][:3] == (255, 0, 0), px[0, 0]
    # CMPR: single 8x8 supertile, solid green (c0=c1 -> index 0)
    blk = struct.pack('>HHI', 0x07E0, 0x07E0, 0)
    img = gxtexture.decode(7, blk * 4, 8, 8)
    assert img.convert('RGBA').load()[0, 0][:3] == (0, 255, 0)

def t_dsp2wav():
    import dsp2wav
    # minimal DSP: 14 samples = 16 nibbles = 1 frame; zero coefs -> silence-ish
    hdr = struct.pack('>IIIHHIIII', 14, 16, 32000, 0, 0, 0, 15, 0, 0)
    hdr += b'\x00' * 32          # coefficients
    hdr += struct.pack('>H', 0)    # initial predictor/scale
    hdr += b'\x00' * (0x60 - len(hdr))
    frame = bytes([0x00]) + b'\x00' * 7  # predictor 0, scale 0, all nibbles 0
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 't.dsp')
        open(p, 'wb').write(hdr + frame)
        pcm, rate = dsp2wav.decode_dsp(p)
        assert rate == 32000 and len(pcm) == 14
        assert all(v == 0 for v in pcm)
        out = dsp2wav.process(p, td)
        w = wave.open(out, 'rb')
        assert w.getframerate() == 32000 and w.getnframes() == 14
        w.close()

def t_ssq():
    import ssq_parse
    # synthetic chunk: header + one diff-1 section with 2 notes (L then R)
    hdr = bytearray(0x24)
    struct.pack_into('<I', hdr, 0, 0x24)
    struct.pack_into('<I', hdr, 0x1C, 150)          # BPM
    ts = [0x400, 0x800]
    arrows = [0x0100, 0x0800]                        # L, R (mask in high byte)
    sec_size = 16 + len(ts) * 4 + 4 + len(arrows) * 2
    sec = struct.pack('<I', sec_size) + b'\x09\x00\x14\x01'
    sec += struct.pack('<2I', len(ts), 0)
    sec += b''.join(struct.pack('<I', t) for t in ts)
    sec += b'\x00\x08\x00\x08'
    sec += b''.join(struct.pack('>H', a) for a in arrows)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'chunk999.bin')
        open(p, 'wb').write(bytes(hdr) + sec)
        r = ssq_parse.parse(p)
        assert r['bpm'] == 150, r['bpm']
        s = r['sections'][0]
        assert s['diff'] == 1 and s['notes'] == 2, s
        assert s['arrows'] == [0x0100, 0x0800]
        assert s['last_tick'] == 0x800

def t_msm():
    import msm_extract
    with tempfile.TemporaryDirectory() as td:
        msm = bytearray(0x200)
        msm[0:4] = b'GSND'
        struct.pack_into('>I', msm, 4, 2)
        # chunk table: 2 entries (entry 0 dummy)
        struct.pack_into('>2I', msm, 0x20, 0x100, 0x40)
        struct.pack_into('>2I', msm, 0x38, 0x140, 0x40)
        struct.pack_into('>2I', msm, 0x40, 0x180, 0x20)
        # group entry 1 at 0x100+32
        e = 0x100 + 32
        struct.pack_into('>H', msm, e, 0x1234)       # group id
        struct.pack_into('>2I', msm, e + 4, 0, 0x40) # group data rel + size
        struct.pack_into('>2I', msm, e + 12, 0, 0x20)# samp rel + size
        # group data at 0x140: pool=0 proj=0x10 sdir=0x20 sng=0x30
        struct.pack_into('>4I', msm, 0x140, 0, 0x10, 0x20, 0x30)
        p = os.path.join(td, 't.msm')
        open(p, 'wb').write(bytes(msm))
        out = os.path.join(td, 'out')
        sys.argv = ['x', p, out]
        msm_extract.main()
        assert os.path.getsize(os.path.join(out, '1234.pool')) == 0x10
        assert os.path.getsize(os.path.join(out, '1234.proj')) == 0x10
        assert os.path.getsize(os.path.join(out, '1234.sdir')) == 0x10
        assert os.path.getsize(os.path.join(out, '1234.samp')) == 0x20

def t_pdt():
    import pdt_extract
    with tempfile.TemporaryDirectory() as td:
        pdt = bytearray(0x400)
        struct.pack_into('>H', pdt, 0, 1)            # unk
        struct.pack_into('>H', pdt, 2, 1)            # 1 stream
        struct.pack_into('>I', pdt, 8, 32000)        # rate
        struct.pack_into('>4I', pdt, 0x10, 0x40, 0x100, 0x140, 0x200)
        struct.pack_into('>I', pdt, 0x40, 0x140)     # entry 0 -> header 0x140
        # header: mono, 16 nibbles, data at 0x200
        struct.pack_into('>4I', pdt, 0x140, 0, 32000, 16, 0)
        struct.pack_into('>I', pdt, 0x150, 0x200)
        struct.pack_into('>H', pdt, 0x154, 0)        # coef entry 0
        p = os.path.join(td, 't.pdt')
        open(p, 'wb').write(bytes(pdt))
        out = os.path.join(td, 'out')
        sys.argv = ['x', p, out]
        pdt_extract.main()
        dsp = open(os.path.join(out, '0000.dsp'), 'rb').read()
        assert len(dsp) == 0x60 + 8, len(dsp)
        n, nib, rate = struct.unpack_from('>III', dsp, 0)
        assert nib == 16 and rate == 32000

check('gxtexture', t_gxtexture)
check('dsp2wav', t_dsp2wav)
check('ssq_parse', t_ssq)
check('msm_extract', t_msm)
check('pdt_extract', t_pdt)

if failures:
    print(f'\n{len(failures)} FAILURES: {failures}')
    sys.exit(1)
print('\nall smoke tests passed')
