# GameCube DSP ADPCM -> WAV decoder (pure python)
# Usage: python dsp2wav.py <infile-or-dir> [outdir]
# Stereo pairs named XXXX_L.dsp / XXXX_R.dsp are merged automatically.
import sys, os, struct, wave

def s4(v):
    return v - 16 if v >= 8 else v

def clamp16(v):
    return max(-32768, min(32767, v))

def decode_dsp(path):
    d = open(path, "rb").read()
    num_samples, num_nibbles, rate = struct.unpack_from(">III", d, 0)
    loop_flag = struct.unpack_from(">H", d, 0x0C)[0]
    loop_start = struct.unpack_from(">I", d, 0x10)[0]
    coefs = struct.unpack_from(">16h", d, 0x1C)
    hist1, hist2 = 0, 0
    pcm = []
    pos = 0x60
    nib_idx = 0
    while nib_idx < num_nibbles:
        header = d[pos]; pos += 1
        predictor = header >> 4
        scale = 1 << (header & 0xF)
        c1, c2 = coefs[predictor * 2], coefs[predictor * 2 + 1]
        nib_idx += 2
        for i in range(7):
            if nib_idx >= num_nibbles:
                break
            byte = d[pos]; pos += 1
            for nib in (byte >> 4, byte & 0xF):
                sample = (s4(nib) * scale * 2048 + 0x400 + c1 * hist1 + c2 * hist2) >> 11
                sample = clamp16(sample)
                hist2, hist1 = hist1, sample
                pcm.append(sample)
                nib_idx += 1
                if len(pcm) >= num_samples:
                    break
    return pcm[:num_samples], rate

def write_wav(path, channels, rate):
    w = wave.open(path, "wb")
    w.setnchannels(len(channels))
    w.setsampwidth(2)
    w.setframerate(rate)
    n = min(len(c) for c in channels)
    frames = bytearray()
    for i in range(n):
        for c in channels:
            frames += struct.pack("<h", c[i])
    w.writeframes(bytes(frames))
    w.close()

def process(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    base = os.path.basename(path)
    stem, ext = os.path.splitext(base)
    if ext.lower() != ".dsp" or stem.endswith("_R"):
        return None
    if stem.endswith("_L"):
        right = os.path.join(os.path.dirname(path), stem[:-2] + "_R.dsp")
        if os.path.exists(right):
            l, rate = decode_dsp(path)
            r, _ = decode_dsp(right)
            out = os.path.join(outdir, stem[:-2] + ".wav")
            write_wav(out, [l, r], rate)
            return out
    pcm, rate = decode_dsp(path)
    out = os.path.join(outdir, stem + ".wav")
    write_wav(out, [pcm], rate)
    return out

if __name__ == "__main__":
    src = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else None
    if os.path.isdir(src):
        outdir = outdir or src + "_wav"
        os.makedirs(outdir, exist_ok=True)
        count = 0
        for root, _, files in os.walk(src):
            rel = os.path.relpath(root, src)
            od = os.path.join(outdir, rel) if rel != "." else outdir
            os.makedirs(od, exist_ok=True)
            for f in sorted(files):
                r = process(os.path.join(root, f), od)
                if r:
                    count += 1
        print(f"decoded {count} wav files -> {outdir}")
    else:
        outdir = outdir or os.path.dirname(src) or "."
        print(process(src, outdir))
