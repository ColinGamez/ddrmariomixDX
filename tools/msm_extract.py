# MSM (GSND) extractor - Mario Party 4-7 / DDR Mario Mix sound archive
# Ported from Yoshimaster96/mpgc-sound-tools dump_msm.c (with sdir size bug fixed)
# Usage: python msm_extract.py <file.msm> <outdir>
import sys, os, struct

def u16be(b, o): return struct.unpack_from(">H", b, o)[0]
def u32be(b, o): return struct.unpack_from(">I", b, o)[0]

def main():
    msm_path, outdir = sys.argv[1], sys.argv[2]
    data = open(msm_path, "rb").read()
    assert data[:4] == b"GSND", "not a GSND/MSM file"
    version = u32be(data, 4)
    print(f"GSND version {version}, file size {len(data)}")

    chk2Offs = u32be(data, 0x20)
    chk2Size = u32be(data, 0x24)
    chk5Offs = u32be(data, 0x38)
    chk5Size = u32be(data, 0x3C)
    chk6Offs = u32be(data, 0x40)
    chk6Size = u32be(data, 0x44)
    print(f"group table @ {chk2Offs:#x} ({chk2Size>>5} entries), "
          f"group data @ {chk5Offs:#x} size {chk5Size:#x}, "
          f"sample data @ {chk6Offs:#x} size {chk6Size:#x}")

    os.makedirs(outdir, exist_ok=True)
    for i in range(1, chk2Size >> 5):
        e = chk2Offs + (i << 5)
        groupId       = u16be(data, e)
        groupDataOffs = u32be(data, e + 4) + chk5Offs
        groupDataSize = u32be(data, e + 8)
        sampOffs      = u32be(data, e + 12) + chk6Offs
        sampSize      = u32be(data, e + 16)

        poolOffs = u32be(data, groupDataOffs)
        projOffs = u32be(data, groupDataOffs + 4)
        sdirOffs = u32be(data, groupDataOffs + 8)
        sngOffs  = u32be(data, groupDataOffs + 12)
        poolSize = projOffs - poolOffs
        projSize = sdirOffs - projOffs
        sdirSize = sngOffs - sdirOffs

        name = f"{groupId:04X}"
        # write pool/proj/sdir (offsets relative to groupDataOffs)
        for ext, rel, size in (("pool", poolOffs, poolSize),
                               ("proj", projOffs, projSize),
                               ("sdir", sdirOffs, sdirSize)):
            if size <= 0:
                continue
            with open(os.path.join(outdir, f"{name}.{ext}"), "wb") as f:
                f.write(data[groupDataOffs + rel: groupDataOffs + rel + size])
        # samp is absolute from chk6
        if sampSize > 0:
            with open(os.path.join(outdir, f"{name}.samp"), "wb") as f:
                f.write(data[sampOffs: sampOffs + sampSize])
        print(f"group {name}: pool {poolSize:#x} proj {projSize:#x} "
              f"sdir {sdirSize:#x} samp {sampSize:#x}")

if __name__ == "__main__":
    main()
