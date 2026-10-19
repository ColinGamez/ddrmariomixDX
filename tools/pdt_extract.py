# PDT extractor - Mario Party 4-7 / DDR Mario Mix streamed music (DSP bank)
# Ported from Yoshimaster96/mpgc-sound-tools dump_pdt.c (stereo channel bug fixed)
# Usage: python pdt_extract.py <file.pdt> <outdir>
import sys, os, struct

def u16be(b, o): return struct.unpack_from(">H", b, o)[0]
def u32be(b, o): return struct.unpack_from(">I", b, o)[0]

def nibbles_to_samples(n):
    whole, frac = n >> 4, n & 0xF
    return whole * 14 + (frac - 2 if frac > 0 else 0)

def main():
    pdt_path, outdir = sys.argv[1], sys.argv[2]
    data = open(pdt_path, "rb").read()

    unk00      = u16be(data, 0x00)
    numFiles   = u16be(data, 0x02)
    unk04      = u32be(data, 0x04)
    sampleRate0= u32be(data, 0x08)
    unk0C      = u32be(data, 0x0C)
    entryOffs  = u32be(data, 0x10)
    coeffOffs  = u32be(data, 0x14)
    headerOffs = u32be(data, 0x18)
    streamOffs = u32be(data, 0x1C)
    print(f"PDT: {numFiles} streams, default rate {sampleRate0}, "
          f"entries @{entryOffs:#x} coeffs @{coeffOffs:#x} "
          f"headers @{headerOffs:#x} streams @{streamOffs:#x}")

    os.makedirs(outdir, exist_ok=True)
    for i in range(numFiles):
        thisHeaderOffs = u32be(data, entryOffs + (i << 2))
        if thisHeaderOffs == 0:
            continue
        h = thisHeaderOffs
        flags       = u32be(data, h)
        sampleRate  = u32be(data, h + 4)
        nibbleCount = u32be(data, h + 8)
        loopStart   = u32be(data, h + 0x0C)
        ch1Start    = u32be(data, h + 0x10)
        ch1CoefEntry= u16be(data, h + 0x14)

        chans = [(ch1Start, ch1CoefEntry)]
        if flags & 0x01000000:
            ch2Start     = u32be(data, h + 0x18)
            ch2CoefEntry = u16be(data, h + 0x1C)
            chans.append((ch2Start, ch2CoefEntry))
        loopFlag = 1 if flags & 0x02000000 else 0

        for j, (chStart, coefEntry) in enumerate(chans):
            coefOffs = coeffOffs + (coefEntry << 5)
            fname = f"{i:04X}{'_L' if len(chans)==2 and j==0 else '_R' if len(chans)==2 else ''}.dsp"
            hdr = struct.pack(">IIIHHIIII",
                nibbles_to_samples(nibbleCount), nibbleCount, sampleRate,
                loopFlag, 0, loopStart, nibbleCount - 1, 0, 0)
            coefs = data[coefOffs:coefOffs + 32]
            hdr += coefs
            hdr += struct.pack(">H", u16be(data, chStart))  # initial predictor/scale
            hdr += b"\x00" * (0x60 - len(hdr))              # rest of 0x60-byte header
            body = data[chStart: chStart + (nibbleCount + 1) // 2]
            with open(os.path.join(outdir, fname), "wb") as f:
                f.write(hdr + body)
        print(f"stream {i:04X}: rate {sampleRate} nibbles {nibbleCount:#x} "
              f"chans {len(chans)} loop {loopFlag}")

if __name__ == "__main__":
    main()
