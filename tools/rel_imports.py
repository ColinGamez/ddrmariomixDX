"""Parse a REL's import relocation lists.
Usage: rel_imports.py <file.rel> [--calls]
Prints DOL (module 0) call targets with counts."""
import struct, sys, collections

path = sys.argv[1]
d = open(path, 'rb').read()
(modid, next_, prev, nsec, secOff, nameOff, nameSz, ver,
 bss, relOff, impOff, impSize) = struct.unpack('>12I', d[:48])
imps = []
for i in range(impSize // 8):
    m, off = struct.unpack('>II', d[impOff + i * 8:impOff + i * 8 + 8])
    imps.append((m, off))

def walk(off):
    cur = 0
    out = []
    while off + 8 <= len(d):
        delta, typ, sec, add = struct.unpack('>HBBI', d[off:off + 8])
        off += 8
        cur = (cur + delta) & 0xFFFFFFFF
        if typ == 201:  # R_REL_STOP
            break
        out.append((cur, typ, sec, add))
    return out

for m, off in imps:
    entries = walk(off)
    print(f'module {m}: {len(entries)} relocs')
    if m == 0:
        calls = collections.Counter(add for _, t, _, add in entries if t == 10)
        if '--calls' in sys.argv:
            for a, n in sorted(calls.items()):
                print(f'  {a:#010x} x{n}')
        else:
            for a, n in calls.most_common(30):
                print(f'  {a:#010x} x{n}')
