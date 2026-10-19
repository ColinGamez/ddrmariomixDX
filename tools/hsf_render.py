"""Render an HSFV037 model with per-face texture colors, correct up-axis.
Usage: hsf_render.py <chunk.bin> <tex.png> <out.png> [elev azim]
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsf2obj import HSF

path, texpath, out = sys.argv[1], sys.argv[2], sys.argv[3]
elev = float(sys.argv[4]) if len(sys.argv) > 4 else 8
azim = float(sys.argv[5]) if len(sys.argv) > 5 else -90

h = HSF(open(path, 'rb').read())
vb = h.buffers('vertex')
fb = h.buffers('face')
sb = h.buffers('st')

tex = np.array(Image.open(texpath).convert('RGBA'), dtype=float) / 255.0
th, tw = tex.shape[:2]

tris, colors = [], []
sbm = h.strip_base()
for fi, (fname, fcnt, fp) in enumerate(fb):
    # match vertex/st buffers by index
    if fi >= len(vb):
        break
    _, vcnt, vp = vb[fi]
    vs = h.verts(vb[fi])
    uvs = h.uvs(sb[fi]) if fi < len(sb) else None
    for typ, mat, rows in h.faces((fname, fcnt, fp), sbm):
        # fan-triangulate rows (strip: consecutive triples)
        for k in range(len(rows) - 2):
            r = rows[k:k + 3] if typ != 4 else rows[k:k + 3]
            if len(r) < 3:
                break
            tri = []
            uv = []
            ok = True
            for row in r:
                pi, ni, ci, si = row[0], row[1], row[2], row[3]
                if pi < 0 or pi >= len(vs):
                    ok = False
                    break
                tri.append(vs[pi])
                uv.append(uvs[si] if (uvs and 0 <= si < len(uvs)) else None)
            if not ok:
                continue
            tris.append(tri)
            us = [u for u in uv if u]
            if us:
                u = np.mean([p[0] for p in us]) % 1.0
                v = np.mean([p[1] for p in us]) % 1.0
                x = min(int(u * tw), tw - 1)
                y = min(int(v * th), th - 1)
                c = tex[y, x]
                colors.append(c if c[3] > 0.1 else (0.85, 0.15, 0.15, 1.0))
            else:
                colors.append((0.85, 0.15, 0.15, 1.0))

V = np.array(tris)  # (n,3,3), model is Y-up
# matplotlib wants Z-up: swap y/z
P = V[:, :, [0, 2, 1]].copy()
fig = plt.figure(figsize=(8, 8), dpi=150)
ax = fig.add_subplot(111, projection='3d')
pc = art3d.Poly3DCollection(P, facecolors=colors, edgecolors='none')
ax.add_collection3d(pc)
flat = P.reshape(-1, 3)
ax.auto_scale_xyz(flat[:, 0], flat[:, 1], flat[:, 2])
ax.set_box_aspect(np.ptp(flat, axis=0))
ax.view_init(elev=elev, azim=azim)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(out, transparent=True)
print(f'{len(tris)} tris -> {out}')
