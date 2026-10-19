"""DDR Mario Mix chart parser - walks section size fields (replaces naive scanning).

Chunk layout (little-endian data):
  0x00: u32 headerSize = 0x24
  0x04: u16 version (1), u16 ? (0x4B)
  0x18: u32 BPM
  0x24: 5 difficulty sections back to back (order observed: 1,2,3,6,4)

Section:
  +0x00 u32 sectionSize (offset to next section)
  +0x04 tag "09 00 14 XX"  XX = difficulty id
  +0x08 u32 tsCount (timestamp count)
  +0x0C u32 ? (not arrow offset; arrows follow ts array + 4-byte sentinel)
  +0x10 u32 ts[tsCount]  (1024 ticks/beat; first note usually 0x400 = beat 1.0; verified via BPM analysis)
        sentinel 0x08000800 follows
  arrows: BE u16 entries, count = tsCount (+padding)
        HIGH byte = arrow bitmask L=1 D=2 U=4 R=8; LOW byte = Mush Mode gimmick type
"""
import struct, sys, os, glob, json

def parse(path):
    d = open(path, 'rb').read()
    bpm = struct.unpack('<I', d[0x1C:0x20])[0]
    secs = []
    pos = 0x24
    while pos < len(d) - 8:
        sz = struct.unpack('<I', d[pos:pos + 4])[0]
        if sz < 0x14 or pos + sz > len(d) + 16:
            break
        diff = d[pos + 7]
        tscnt = struct.unpack('<I', d[pos + 8:pos + 12])[0]
        aofs = 16 + tscnt * 4 + 4  # arrows follow timestamps + sentinel
        ts = [struct.unpack('<I', d[pos + 16 + i * 4:pos + 20 + i * 4])[0]
              for i in range(tscnt)]
        arrows = []
        for i in range(tscnt):
            o = pos + aofs + i * 2
            if o + 2 > len(d):
                break
            arrows.append(struct.unpack('>H', d[o:o + 2])[0])
        last = max(ts) if ts else 0
        dur = last / 16384 / bpm * 60 if bpm else 0
        secs.append({'diff': diff, 'notes': len(arrows), 'arrows': arrows,
                     'ts': ts, 'last_tick': last, 'dur': round(dur, 2)})
        pos += sz
    return {'bpm': bpm, 'sections': secs}

if __name__ == '__main__':
    paths = sys.argv[1:] or sorted(glob.glob('assets/ssq/chunk*.bin'))
    out = {}
    for f in paths:
        r = parse(f)
        name = os.path.basename(f).replace('.bin', '')
        out[name] = r
        line = ' '.join(f"d{s['diff']}:{s['notes']}n/{s['dur']}s" for s in r['sections'])
        print(f"{name} bpm={r['bpm']:3d}  {line}")
    json.dump(out, open('assets/ssq/parsed.json', 'w'))
