"""Extract Hudson .bin archives.

Format: u32 count, then count u32 offsets (big-endian). Each chunk at its
offset is: u32 size, u32 flags (7 = zlib), u32 size again, u32 ?, then data.
Chunks with flags==7 are zlib-compressed (magic 78 9C); others are raw.
"""
import struct, zlib, sys, os

def extract(path, out_dir):
    d = open(path, 'rb').read()
    count = struct.unpack('>I', d[:4])[0]
    offsets = struct.unpack(f'>{count}I', d[4:4 + count * 4])
    os.makedirs(out_dir, exist_ok=True)
    kinds = {}
    for i, a in enumerate(offsets):
        if a == 0 or a >= len(d):
            kinds['empty'] = kinds.get('empty', 0) + 1
            continue
        size, flags = struct.unpack('>II', d[a:a + 8])
        blob = d[a + 16:a + 16 + size]
        if flags == 7 and blob[:2] == b'\x78\x9c':
            raw = zlib.decompress(blob)
            kind = 'zlib'
        else:
            raw = blob
            kind = 'raw'
        kinds[kind] = kinds.get(kind, 0) + 1
        open(os.path.join(out_dir, f'chunk{i:03d}.bin'), 'wb').write(raw)
    print(f'{os.path.basename(path)}: {count} chunks -> {out_dir}  {kinds}')

if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])
