import struct, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

d = open("box_with_fin.stl","rb").read()
n = struct.unpack("<I", d[80:84])[0]
tris = np.frombuffer(d[84:], dtype=np.uint8).reshape(n,50)
v = tris[:,12:48].copy().view("<f4").reshape(n,3,3).astype(float)/10.0
nrm = tris[:,0:12].copy().view("<f4").reshape(n,3).astype(float)

fig = plt.figure(figsize=(14,6.5))
for idx,(elev,azim,t) in enumerate([(24,-58,"isometric"),(24,-128,"rear")]):
    ax = fig.add_subplot(1,2,idx+1, projection="3d")
    lum = 0.45+0.55*np.clip(nrm@np.array([0.35,-0.5,0.8]),0,1)
    cols = np.stack([lum*0.75, lum*0.82, lum*0.95, np.ones_like(lum)],1)
    ax.add_collection3d(Poly3DCollection(v, facecolors=cols, edgecolors=(0.1,0.2,0.35,0.35), linewidths=0.4))
    ax.set_xlim(0,10.8); ax.set_ylim(0,6.8); ax.set_zlim(0,4.4)
    ax.set_box_aspect((10.8,6.8,4.4)); ax.view_init(elev,azim)
    ax.set_xlabel("X 10.8 cm"); ax.set_ylabel("Y 6.8 cm"); ax.set_zlabel("Z 4.4 cm")
    ax.set_title(t); ax.grid(False)
plt.tight_layout(); plt.savefig("box_preview.png", dpi=130)
print("ok")
