"""Parse HSFV037 (Hudson Soft File, Mario Party 4-8 / DDR Mario Mix) to OBJ.

On-disk layout (big-endian):
  header: char magic[8] + 20 sections {s32 ofs, s32 count}
  section order: scene, color, material, attribute, vertex, normal, st, face,
                 object, bitmap, palette, motion, cenv, skeleton, part,
                 cluster, shape, mapAttr, matrix, symbol, string
  buffers (color/vertex/normal/st/face): array of {u32 name_ofs, s32 count, u32 data_ofs}
    (12 bytes each); element data starts right after the array, data_ofs is
    relative to that base.
  face records: s16 type, s16 mat, then:
    type 2 (tri):  3x s16[4] inline (pos,normal,st,color per corner)
    type 3 (quad): 4x s16[4] inline
    type 4 (strip): 3x s16[4] inline + u32 count; extra rows after face array
Usage: hsf2obj.py <chunk.bin> [out.obj]
"""
import struct, sys, math

SEC_NAMES = ['scene','color','material','attribute','vertex','normal','st','face',
             'object','bitmap','palette','motion','cenv','skeleton','part',
             'cluster','shape','mapAttr','matrix','symbol','string']
HSF_FACE_MASK = 0x7

class HSF:
    def __init__(self, data):
        self.d = data
        assert data[:8] == b'HSFV037\x00', 'bad magic'
        self.sec = {}
        for i, name in enumerate(SEC_NAMES):
            ofs, count = struct.unpack('>2i', data[8 + i * 8:16 + i * 8])
            self.sec[name] = (ofs, count)
        self.strings = self.sec['string'][0]

    def name(self, ofs):
        if ofs in (0, -1, 0xFFFFFFFF):
            return ''
        base = self.strings + ofs
        end = self.d.index(b'\x00', base)
        return self.d[base:end].decode('ascii', 'replace')

    def buffers(self, sec_name):
        ofs, count = self.sec[sec_name]
        out = []
        base = ofs + count * 12
        for i in range(count):
            nofs, cnt, dofs = struct.unpack('>3i', self.d[ofs + i * 12:ofs + i * 12 + 12])
            out.append((self.name(nofs), cnt, base + dofs))
        return out

    def verts(self, buf):
        _, cnt, p = buf
        return [struct.unpack('>3f', self.d[p + i * 12:p + i * 12 + 12]) for i in range(cnt)]

    def uvs(self, buf):
        _, cnt, p = buf
        return [struct.unpack('>2f', self.d[p + i * 8:p + i * 8 + 8]) for i in range(cnt)]

    def strip_base(self):
        """End of the LAST face buffer's record array (loader uses one global)."""
        bufs = self.buffers('face')
        last = max(bufs, key=lambda b: b[2])
        return last[2] + last[1] * 48

    def faces(self, buf, strip_base=None):
        """Returns list of (type, mat, rows). Each row = 4 s16 (pos,nrm,st,clr).
        All records are 48 bytes: type(2) mat(2) union(32) nbt(12).
        type 2=tri (3 rows inline), 3=quad (4 rows inline), 4=strip
        (3 rows inline + u16... actually u32 rowcount + u32 ofs into
        extra rows stored after the face array, in units of 4 s16)."""
        _, cnt, p = buf
        if strip_base is None:
            strip_base = self.strip_base()
        extra_base = strip_base
        out = []
        for i in range(cnt):
            q = p + i * 48
            typ, mat = struct.unpack('>2h', self.d[q:q + 4])
            typ &= HSF_FACE_MASK
            mat &= 0x7FFF
            u = self.d[q + 4:q + 36]
            if typ == 2:
                idx = struct.unpack('>12h', u[:24])
                out.append((typ, mat, [idx[0:4], idx[4:8], idx[8:12]]))
            elif typ == 3:
                idx = struct.unpack('>16h', u)
                out.append((typ, mat, [idx[0:4], idx[4:8], idx[8:12], idx[12:16]]))
            elif typ == 4:
                idx = struct.unpack('>12h', u[:24])
                nrows, rofs = struct.unpack('>2I', u[24:32])
                rows = [idx[0:4], idx[4:8], idx[8:12]]
                b = extra_base + rofs * 8
                extra = struct.unpack(f'>{nrows * 4}h', self.d[b:b + nrows * 8])
                rows += [extra[j * 4:j * 4 + 4] for j in range(nrows)]
                out.append((typ, mat, rows))
            else:
                raise ValueError(f'unknown face type {typ} at {q:#x}')
        return out

def main():
    path = sys.argv[1]
    d = open(path, 'rb').read()
    h = HSF(d)
    print('sections:', {k: v for k, v in h.sec.items() if v[1]})
    vb = h.buffers('vertex')
    fb = h.buffers('face')
    sb = h.buffers('st')
    print(f'vertex buffers: {len(vb)}, face buffers: {len(fb)}, st buffers: {len(sb)}')
    for name, cnt, p in vb:
        vs = h.verts((name, cnt, p))
        xs = [v[0] for v in vs]; ys = [v[1] for v in vs]; zs = [v[2] for v in vs]
        print(f'  vbuf {name!r}: {cnt} verts, x[{min(xs):.1f},{max(xs):.1f}] '
              f'y[{min(ys):.1f},{max(ys):.1f}] z[{min(zs):.1f},{max(zs):.1f}]')
    for name, cnt, p in fb:
        try:
            faces = h.faces((name, cnt, p))
            tris = sum(len(r[2]) - 2 for r in faces if r)
            print(f'  fbuf {name!r}: {cnt} records -> {tris} tris')
        except Exception as e:
            print(f'  fbuf {name!r}: ERROR {e}')

if __name__ == '__main__':
    main()
