"""Open-top box + fin + two wall windows -> binary STL (mm).

inner cavity 100 x 60 x 40, wall 4, open top, outer 108 x 68 x 44
fin : 3 thick (X) x 3 deep (Y) x 17 tall, 8 mm clear of the left end wall
hole A: 9 x 4 mm through the FRONT long wall, centred on the fin (z 10.5-14.5)
hole B: 10 x 5 mm through the BACK long wall, same centre (z 10-15)
"""
import struct

T = 10.0
xs = [0.0, 0.4, 0.85, 0.9, 1.2, 1.5, 1.8, 1.85, 10.4, 10.8]
ys = [0.0, 0.4, 0.7, 6.4, 6.8]
zs = [0.0, 0.4, 1.0, 1.05, 1.45, 1.5, 2.1, 4.4]
NX, NY, NZ = len(xs) - 1, len(ys) - 1, len(zs) - 1
EPS = 1e-9
solid = [[[False] * NZ for _ in range(NY)] for _ in range(NX)]

def inside(v0, v1, a, b):
    return v0 >= a - EPS and v1 <= b + EPS

for i in range(NX):
    for j in range(NY):
        for k in range(NZ):
            x0, x1 = xs[i], xs[i + 1]
            y0, y1 = ys[j], ys[j + 1]
            z0, z1 = zs[k], zs[k + 1]
            floor = z1 <= 0.4 + EPS
            sidewall = x0 < 0.4 or x1 > 10.4 or y0 < 0.4 or y1 > 6.4
            fin = inside(x0, x1, 1.2, 1.5) and inside(y0, y1, 0.4, 0.7) and z1 <= 2.1 + EPS
            holeA = inside(x0, x1, 0.9, 1.8) and y1 <= 0.4 + EPS and inside(z0, z1, 1.05, 1.45)
            holeB = inside(x0, x1, 0.85, 1.85) and y0 >= 6.4 - EPS and inside(z0, z1, 1.0, 1.5)
            solid[i][j][k] = (floor or sidewall or fin) and not (holeA or holeB)

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
print(f"volume: {vol:.4f} cm3  (expected 82.9450)")
print(f"bbox: {max(xs)} x {max(ys)} x {max(zs)} cm")
print(f"watertight: {len(bad) == 0}  (bad edges: {len(bad)})")

with open("box_with_fin_holes.stl", "wb") as f:
    hdr = b"open box 108x68x44, fin 3x3x17, windows 9x4 front / 10x5 back"
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
print("wrote box_with_fin_holes.stl (mm)")
