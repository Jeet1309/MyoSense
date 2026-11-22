"""Box + fin + strap plate on a neck -> binary STL (mm).

box   108 x 68 x 44 outer, cavity 100 x 60 x 40, wall 4, open top
fin   3 (X) x 3 (Y) x 17 (Z), 8 mm clear of the left inner face, on the front wall
neck  10 (X) x 50 (Y) x 7 (Z) at x 84-94, fills the gap under the box
plate 80 (X) x 50 (Y) x 5 (Z) at x 14-94, hanging 7 mm below the box bottom
"""
import struct

xs = [0, 4, 12, 14, 15, 84, 94, 104, 108]
ys = [0, 4, 7, 9, 59, 64, 68]
zs = [-12, -7, 0, 4, 21, 44]
NX, NY, NZ = len(xs) - 1, len(ys) - 1, len(zs) - 1
EPS = 1e-9


def within(v0, v1, a, b):
    return v0 >= a - EPS and v1 <= b + EPS


solid = [[[False] * NZ for _ in range(NY)] for _ in range(NX)]
for i in range(NX):
    for j in range(NY):
        for k in range(NZ):
            x0, x1, y0, y1, z0, z1 = xs[i], xs[i + 1], ys[j], ys[j + 1], zs[k], zs[k + 1]
            box = z0 >= -EPS and (
                z1 <= 4 + EPS or x0 < 4 or x1 > 104 or y0 < 4 or y1 > 64)
            fin = within(x0, x1, 12, 15) and within(y0, y1, 4, 7) and \
                  within(z0, z1, 4, 21)
            neck = within(x0, x1, 84, 94) and within(y0, y1, 9, 59) and \
                   within(z0, z1, -7, 0)
            plate = within(x0, x1, 14, 94) and within(y0, y1, 9, 59) and \
                    within(z0, z1, -12, -7)
            solid[i][j][k] = box or fin or neck or plate

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
print(f"volume: {vol / 1000:.3f} cm3  (expected 106.789)")
print(f"bbox: {max(xs) - min(xs)} x {max(ys) - min(ys)} x {max(zs) - min(zs)} mm"
      f"  (z {min(zs)}..{max(zs)})")
print(f"watertight: {len(bad) == 0}  (bad edges: {len(bad)})")

with open("box_with_plate.stl", "wb") as f:
    hdr = b"box 108x68x44, fin 3x3x17, plate 80x50x5 on 10x50x7 neck, 7mm belt slot"
    f.write(hdr.ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for a, b, c in tris:
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        L = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 or 1.0
        n = [q / L for q in n]
        f.write(struct.pack("<12fH", n[0], n[1], n[2],
                            a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2], 0))
print("wrote box_with_plate.stl (mm)")
