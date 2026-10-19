"""GameCube ISO extractor — dumps boot.bin, bi2.bin, apploader, main.dol and full FST file tree."""
import struct, sys, os

def main(iso_path, out_dir):
    iso = open(iso_path, "rb")
    hdr = iso.read(0x2440)
    game_id = hdr[0:6].decode()
    dol_off, fst_off = struct.unpack(">II", hdr[0x420:0x428])
    fst_len = struct.unpack(">I", hdr[0x428:0x42C])[0]
    os.makedirs(out_dir, exist_ok=True)

    # Boot files
    open(os.path.join(out_dir, "boot.bin"), "wb").write(hdr[:0x440])
    iso.seek(0x440); open(os.path.join(out_dir, "bi2.bin"), "wb").write(iso.read(0x2000))
    iso.seek(0x2440); open(os.path.join(out_dir, "apploader.img"), "wb").write(iso.read(dol_off - 0x2440))
    iso.seek(dol_off)
    # DOL size = sum of sections via header
    dol_hdr = iso.read(0x100)
    offs = struct.unpack(">18I", dol_hdr[:72])
    loads = struct.unpack(">18I", dol_hdr[72:144])
    sizes = struct.unpack(">18I", dol_hdr[144:216])
    bss_addr, bss_size, entry = struct.unpack(">III", dol_hdr[216:228])
    dol_end = max(o + s for o, s in zip(offs, sizes) if s)
    iso.seek(dol_off)
    open(os.path.join(out_dir, "main.dol"), "wb").write(iso.read(dol_end))
    print(f"[+] {game_id}: entry={entry:#010x} bss={bss_size:#x} dol_size={dol_end:#x}")

    # FST
    iso.seek(fst_off); fst = iso.read(fst_len)
    count = struct.unpack(">I", fst[8:12])[0]
    strtab_off = count * 12
    files_dir = os.path.join(out_dir, "files")
    os.makedirs(files_dir, exist_ok=True)
    names = []
    def name_at(o):
        e = fst.index(b"\0", strtab_off + o)
        return fst[strtab_off + o:e].decode("shift_jis", "replace")
    # recursive walk
    sys.setrecursionlimit(10000)
    def walk(i, path):
        noff = struct.unpack(">I", fst[i*12:i*12+4])[0] & 0xFFFFFF
        is_dir = fst[i*12] != 0
        off, size = struct.unpack(">II", fst[i*12+4:i*12+12])
        nm = name_at(noff)
        p = os.path.join(path, nm)
        if is_dir:
            os.makedirs(p, exist_ok=True)
            j = i + 1
            while j < size:  # dir 'size' field = next sibling index
                j = walk(j, p)
            return size
        else:
            iso.seek(off)
            open(p, "wb").write(iso.read(size))
            names.append((p, size))
            return i + 1
    walk(0, files_dir)
    print(f"[+] extracted {len(names)} files -> {files_dir}")
    for p, s in names:
        print(f"    {s:>12,}  {os.path.relpath(p, files_dir)}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
