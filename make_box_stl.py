"""Open-top box with an internal fin -> binary STL (mm).

Geometry (cm, then x10 -> mm):
  inner cavity 10 x 6 x 4, wall/bottom 0.4, open top, outer height 4.4
  fin: 0.2 thick (X) x 0.3 deep (Y) x 1.7 tall (Z), 0.8 clear of the 6x4 end wall
"""
import struct

T = 10.0

# grid planes (cm)
xs = [0.0, 0.4, 1.2, 1.5, 10.4, 10.8]
ys = [0.0, 0.4, 0.7, 6.4, 6.8]
zs = [0.0, 0.4, 2.1, 4.4]

NX, NY, NZ = len(xs) - 1, len(ys) - 1, len(zs) - 1
solid = [[[False] * NZ for _ in range(NY)] for _ in range(NX)]

for i in range(NX):
    for j in range(NY):
        for k in range(NZ):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            z0, z1 = zs[k], zs[k + 1]
            floor = z1 <= 0.4                                        # bottom slab
            sidewall = x0 < 0.4 or x1 > 10.4 or y0 < 0.4 or y1 > 6.4  # 4 walls
            fin = (x0 >= 1.2 - 1e-9 and x1 <= 1.5 + 1e-9 and
                   y0 >= 0.4 - 1e-9 and y1 <= 0.7 + 1e-9 and
                   z1 <= 2.1 + 1e-9)
            solid[i][j][k] = floor or sidewall or fin

tris = []


def quad(a, b, c, d):
    tris.append((a, b, c))
    tris.append((a, c, d))


for i in range(NX):
    for j in range(NY):
        for k in range(NZ):
            if not solid[i][j][k]:
                continue
            x0, x1, y0, y1, z0, z1 = xs[i], xs[i + 1], ys[j], ys[j + 1], zs[k], zs[k + 1]
            if i == 0 or not solid[i - 1][j][k]:
                quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0))
            if i == NX - 1 or not solid[i + 1][j][k]:
                quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1))
            if j == 0 or not solid[i][j - 1][k]:
                quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1))
            if j == NY - 1 or not solid[i][j + 1][k]:
                quad((x0, y1, z0), (x0, y1, z1), (x1, y1, z1), (x1, y1, z0))
            if k == 0 or not solid[i][j][k - 1]:
                quad((x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0))
            if k == NZ - 1 or not solid[i][j][k + 1]:
                quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))

# ---- validation ----
vol = 0.0
for a, b, c in tris:
    vol += (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0

edges = {}
for t in tris:
    for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        key = tuple(sorted((u, v)))
        edges[key] = edges.get(key, 0) + 1
bad = [e for e, n in edges.items() if n != 2]

print(f"triangles: {len(tris)}")
print(f"volume: {vol:.4f} cm3  (expected 83.2890)")
print(f"bbox: {max(xs)} x {max(ys)} x {max(zs)} cm")
print(f"watertight: {len(bad) == 0}  (bad edges: {len(bad)})")

with open("box_with_fin.stl", "wb") as f:
    hdr = b"open box 10x6x4 cm inner, wall 0.4, fin 0.3x0.3x1.7 at 0.8 from end"
    f.write(hdr.ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for a, b, c in tris:
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        L = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 or 1.0
        n = [q / L for q in n]
        f.write(struct.pack("<12fH", n[0], n[1], n[2],
                            a[0] * T, a[1] * T, a[2] * T,
                            b[0] * T, b[1] * T, b[2] * T,
                            c[0] * T, c[1] * T, c[2] * T, 0))
print("wrote box_with_fin.stl (mm)")
