"""Render mario_full.obj front view, textured by sampling the body atlas at UV centroids."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from PIL import Image

OBJ = 'assets/mario/mario_full.obj'
TEX = 'assets/mario/s3_c000m1_A0.png'
import sys; ELEV=float(sys.argv[1]); AZIM=float(sys.argv[2]); OUT=sys.argv[3]

vs, vts, faces, face_uvs = [], [], [], []
for line in open(OBJ):
    if line.startswith('v '):
        vs.append([float(x) for x in line.split()[1:4]])
    elif line.startswith('vt '):
        vts.append([float(x) for x in line.split()[1:3]])
    elif line.startswith('f '):
        idx = [p.split('/') for p in line.split()[1:]]
        faces.append([int(p[0]) - 1 for p in idx])
        face_uvs.append([int(p[1]) - 1 if len(p) > 1 and p[1] else -1 for p in idx])

V = np.array(vs)
tex = np.array(Image.open(TEX).convert('RGBA'), dtype=float) / 255.0
th, tw = tex.shape[:2]

colors = []
for f, fu in zip(faces, face_uvs):
    uv = [vts[i] for i in fu if i >= 0]
    if uv:
        u = np.mean([p[0] for p in uv]) % 1.0
        v = np.mean([p[1] for p in uv]) % 1.0
        x = min(int(u * tw), tw - 1); y = min(int(v * th), th - 1)
        colors.append(tex[y, x])
    else:
        colors.append((0.8, 0.1, 0.1, 1.0))

fig = plt.figure(figsize=(8, 10), dpi=150)
ax = fig.add_subplot(111, projection='3d')
pc = art3d.Poly3DCollection(V[faces], facecolors=colors, edgecolors='none')
ax.add_collection3d(pc)
ax.auto_scale_xyz(V[:, 0], V[:, 1], V[:, 2])
ax.set_box_aspect((np.ptp(V[:, 0]), np.ptp(V[:, 1]), np.ptp(V[:, 2])))
ax.view_init(elev=ELEV, azim=AZIM)
ax.set_axis_off()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(OUT, transparent=True)
print('saved', OUT)
