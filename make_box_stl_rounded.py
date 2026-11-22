"""Box + fin + strap plate with r = 2 mm fillets -> watertight STL.

Signed-distance model (mm):
  box   108 x 68 x 44, bottom perimeter edges filleted r2, cavity 100 x 60 x 40 open top
  fin   3 x 3 x 17 at x 12-15, y 4-7, z 4-21
  neck  rounded box 10 x 50 x 7 at x 84-94, z -7..0
  plate rounded box 80 x 50 x 5 at x 14-94, z -12..-7
  parts blended with a smooth union (k = 2) so junctions are filleted too
"""
import sys
import struct
import numpy as np
from skimage import measure

R = 2.0
K = 2.0


def smin(a, b, k=K):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def rbox(px, py, pz, x0, x1, y0, y1, z0, z1, r=R):
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    qx = np.abs(px - cx) - ((x1 - x0) / 2 - r)
    qy = np.abs(py - cy) - ((y1 - y0) / 2 - r)
    qz = np.abs(pz - cz) - ((z1 - z0) / 2 - r)
    return (np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
            + np.minimum(np.maximum(np.maximum(qx, qy), qz), 0) - r)


def build(h=0.5, pad=2.5):
    xs = np.arange(-pad, 108 + pad + h, h)
    ys = np.arange(-pad, 68 + pad + h, h)
    zs = np.arange(-12 - pad, 44 + pad + h, h)
    nx, ny, nz = len(xs), len(ys), len(zs)
    X, Y = np.meshgrid(xs, ys)          # (ny, nx)
    vol = np.empty((nz, ny, nx), np.float32)
    hx, hy = 54.0, 34.0
    for k, z in enumerate(zs):
        t = np.clip(z, 0, R)
        delta = R - np.sqrt(np.maximum(R * R - (R - t) ** 2, 0))
        dxy = np.maximum(np.abs(X - 54) - (hx - delta), np.abs(Y - 34) - (hy - delta))
        d_shell = np.maximum(dxy, max(-z, z - 44))
        qx = np.abs(X - 54) - 50
        qy = np.abs(Y - 34) - 30
        qz = abs(z - 52) - 48
        d_cav = (np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + max(qz, 0) ** 2)
                 + min(max(qx, qy, qz), 0))
        d_box = np.maximum(d_shell, -d_cav)
        d_neck = rbox(X, Y, z, 84, 94, 9, 59, -7, 0)
        d_plate = rbox(X, Y, z, 14, 94, 9, 59, -12, -7)
        d = smin(smin(d_box, d_neck), d_plate)
        vol[k] = d.astype(np.float32)
    # fin as a sharp box, unioned (it is inside the cavity, edges stay sharp)
    fin = rbox(X[:, :, None], Y[:, :, None], zs[None, None, :], 12, 15, 4, 7, 4, 21, r=0.001)
    fin = np.transpose(np.minimum(fin, 0), (2, 1, 0))
    vol = smin(vol, fin, k=0.2)
    return xs, ys, zs, vol


def main(h=0.5, out="box_with_plate_rounded.stl"):
    xs, ys, zs, vol = build(h)
    print(f"grid {len(xs)}x{len(ys)}x{len(zs)} = {vol.size / 1e6:.2f} M samples @ {h} mm")
    if vol.min() > 0 or vol.max() < 0:
        raise SystemExit("SDF does not cross zero - check domain")
    edge = min(vol[0].min(), vol[-1].min(), vol[:, 0].min(), vol[:, -1].min(),
               vol[:, :, 0].min(), vol[:, :, -1].min())
    print(f"min SDF on domain boundary: {edge:.2f} mm (must be > 0)")

    verts, faces, _, _ = measure.marching_cubes(vol, level=0.0, spacing=(h, h, h))
    v = np.column_stack([xs[0] + verts[:, 2], ys[0] + verts[:, 1], zs[0] + verts[:, 0]])
    f = faces
    tri = v[f]
    vol_ = np.einsum("ij,ij->i",
                     tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0
    if vol_ < 0:
        f = f[:, ::-1]
        tri = v[f]
        vol_ = -vol_
    print(f"triangles: {len(f)}   volume: {vol_ / 1000:.3f} cm3")

    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-12)
    with open(out, "wb") as fh:
        hdr = b"box+fin+plate r2 fillets, marching cubes"
        fh.write(hdr.ljust(80, b" "))
        fh.write(struct.pack("<I", len(f)))
        rec = np.empty(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec["n"] = n
        rec["v"] = tri
        rec["a"] = 0
        fh.write(rec.tobytes())
    print(f"wrote {out}  ({len(f) * 50 / 1e6:.1f} MB)")


if __name__ == "__main__":
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    out = sys.argv[2] if len(sys.argv) > 2 else "box_with_plate_rounded.stl"
    main(h, out)
