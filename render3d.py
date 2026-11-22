"""Software-render an STL to a shaded PNG sheet (z-buffered, orthographic).

usage: python render3d.py [stl] [out.png] [plain|holes]
"""
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def load_stl(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[80:84])[0]
    a = np.frombuffer(d[84:84 + 50 * n], dtype=np.uint8).reshape(n, 50)
    return a[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)


def basis(az, el):
    az, el = np.radians(az), np.radians(el)
    up = np.array([0.0, 0.0, 1.0])
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    r = np.cross(up, d); r /= np.linalg.norm(r)
    u = np.cross(d, r)
    return d, r, u


class Cam:
    def __init__(self, tris, az, el, W, H, focus=None, zoom=1.0):
        self.d, self.r, self.u = basis(az, el)
        self.W, self.H = W, H
        c = tris.reshape(-1, 3)
        self.f = np.array(focus, float) if focus is not None else (c.min(0) + c.max(0)) / 2
        P = c - self.f
        sx, sy = P @ self.r, P @ self.u
        self.scale = 0.86 * min(W / np.ptp(sx), H / np.ptp(sy)) * zoom

    def proj(self, pts):
        P = np.asarray(pts, float) - self.f
        return P @ self.r * self.scale + self.W / 2, self.H / 2 - P @ self.u * self.scale, P @ self.d


def render(tris, cam, ss=3):
    W, H = cam.W, cam.H
    d = cam.d
    X, Y, dep = cam.proj(tris.reshape(-1, 3))
    X = X.reshape(-1, 3); Y = Y.reshape(-1, 3); dep = dep.reshape(-1, 3)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1)[:, None]

    key = np.array([-0.42, 0.50, 0.76]); key /= np.linalg.norm(key)
    hv = key + d; hv /= np.linalg.norm(hv)
    front = n @ d > 1e-9
    diff = np.clip(n @ key, 0, 1)
    head = np.clip(n @ d, 0, 1)
    spec = np.clip(n @ hv, 0, 1) ** 32
    base = np.array([0.66, 0.72, 0.83])
    col = (base[None, :] * (0.42 + 0.46 * diff + 0.38 * head)[:, None]
           + 0.26 * spec[:, None] + 0.09 * np.clip(n[:, 2:3], 0, 1))

    Wb, Hb = W * ss, H * ss
    img = np.ones((Hb, Wb, 3), np.float32)
    zb = np.full((Hb, Wb), -1e9, np.float32)
    Xs, Ys = X * ss, Y * ss
    for t in np.nonzero(front)[0]:
        xs_, ys_, zs_ = Xs[t], Ys[t], dep[t]
        x0, x1 = int(max(0, np.floor(xs_.min()))), int(min(Wb - 1, np.ceil(xs_.max())))
        y0, y1 = int(max(0, np.floor(ys_.min()))), int(min(Hb - 1, np.ceil(ys_.max())))
        if x1 < x0 or y1 < y0:
            continue
        px, py = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
        den = (ys_[1] - ys_[2]) * (xs_[0] - xs_[2]) + (xs_[2] - xs_[1]) * (ys_[0] - ys_[2])
        if abs(den) < 1e-12:
            continue
        l0 = ((ys_[1] - ys_[2]) * (px - xs_[2]) + (xs_[2] - xs_[1]) * (py - ys_[2])) / den
        l1 = ((ys_[2] - ys_[0]) * (px - xs_[2]) + (xs_[0] - xs_[2]) * (py - ys_[2])) / den
        l2 = 1 - l0 - l1
        m = (l0 >= -.002) & (l1 >= -.002) & (l2 >= -.002)
        if not m.any():
            continue
        z = l0 * zs_[0] + l1 * zs_[1] + l2 * zs_[2]
        sub_z = zb[y0:y1 + 1, x0:x1 + 1]
        w = m & (z > sub_z)
        if not w.any():
            continue
        sub_z[w] = z[w]
        img[y0:y1 + 1, x0:x1 + 1][w] = col[t]

    im = Image.fromarray((np.clip(img, 0, 1) ** (1 / 1.06) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS), zb, front, n


def draw_edges(im, tris, zb, ss, cam, front, n):
    verts, vid, faces = [], {}, []
    for t in range(len(tris)):
        ids = []
        for k in range(3):
            key = tuple(np.round(tris[t][k], 6))
            if key not in vid:
                vid[key] = len(verts); verts.append(key)
            ids.append(vid[key])
        faces.append(ids)
    edges = {}
    for fi, ids in enumerate(faces):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edges.setdefault(tuple(sorted((ids[a], ids[b]))), []).append(fi)

    VX, VY, VD = cam.proj(np.array(verts))
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    H, W = im.size[1], im.size[0]
    for (a, b), fl in edges.items():
        keep = len(fl) == 1 or abs(float(n[fl[0]] @ n[fl[1]])) < 0.95 or \
               (len(fl) == 2 and front[fl[0]] != front[fl[1]])
        if not keep:
            continue
        pa = None
        for tt in np.linspace(0.02, 0.98, 34):
            x = (1 - tt) * VX[a] + tt * VX[b]
            y = (1 - tt) * VY[a] + tt * VY[b]
            if not (-1 < x < W and -1 < y < H):
                pa = None
                continue
            d_ = (1 - tt) * VD[a] + tt * VD[b]
            zi = int(np.clip(y * ss, 0, zb.shape[0] - 1))
            xi = int(np.clip(x * ss, 0, zb.shape[1] - 1))
            if d_ >= zb[zi, xi] - 0.4:
                if pa is not None:
                    dr.line([pa, (x, y)], fill=(26, 38, 54, 170), width=2)
                pa = (x, y)
            else:
                pa = None
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def annotate(im, cam, A, B, txt):
    X, Y, _ = cam.proj([A, B])
    (x1, y1), (x2, y2) = (X[0], Y[0]), (X[1], Y[1])
    dr = ImageDraw.Draw(im)
    red = (198, 36, 64)
    dr.line([(x1, y1), (x2, y2)], fill=red, width=3)
    ang = np.arctan2(y2 - y1, x2 - x1)
    for x, y, a in ((x2, y2, ang), (x1, y1, ang + np.pi)):
        for s in (-0.42, 0.42):
            dr.line([(x, y), (x - 15 * np.cos(a + s), y - 15 * np.sin(a + s))], fill=red, width=3)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    except OSError:
        f = ImageFont.load_default()
    w = dr.textlength(txt, font=f)
    dr.rounded_rectangle([mx - w / 2 - 7, my - 15, mx + w / 2 + 7, my + 15], 7, fill=(255, 255, 255))
    dr.text((mx - w / 2, my - 13), txt, font=f, fill=red)


def label(im, text, sub=""):
    dr = ImageDraw.Draw(im)
    try:
        f1 = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 25)
        f2 = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    dr.rectangle([0, 0, im.width, 62], fill=(255, 255, 255))
    dr.text((20, 12), text, font=f1, fill=(25, 38, 56))
    if sub:
        dr.text((20, 41), sub, font=f2, fill=(92, 106, 126))
    return im


PLAIN = [
    (-58, 34, None, 1.0, "Isometric", "open top, fin on the front long wall, 8 mm from the left end", []),
    (-92, 50, None, 1.0, "Looking into the box", "cavity 100 x 60 x 40 mm, rim 4 mm", []),
    (-152, 22, None, 1.0, "Rear / outside", "outer 108 x 68 x 44 mm, wall 4 mm", []),
    (90, 14, (13.5, 7.0, 12.5), 4.2, "Close-up: the fin",
     "3 mm thick x 3 mm deep x 17 mm tall, on the floor",
     [((18.6, 7.05, 4.0), (18.6, 7.05, 21.0), "17 mm"),
      ((12.0, 7.05, 22.2), (15.0, 7.05, 22.2), "3 mm")]),
]

HOLES = [
    (-58, 34, None, 1.0, "Isometric",
     "front window 9 x 4 mm at the fin, back window 10 x 5 mm opposite it", []),
    (-90, 6, (13.5, 0.0, 12.5), 3.2, "Front window - outside face",
     "9 x 4 mm, cut through the 4 mm wall, fin visible through it",
     [((9.0, -0.1, 8.4), (18.0, -0.1, 8.4), "9 mm"),
      ((21.0, -0.1, 10.5), (21.0, -0.1, 14.5), "4 mm")]),
    (-90, 56, None, 1.0, "Looking inside",
     "back window 10 x 5 mm on the same centre line as the front one", []),
    (90, 8, (13.5, 68.0, 12.5), 3.2, "Back window - outside face",
     "10 x 5 mm, centred on the same axis as the front window",
     [((8.5, 68.1, 7.6), (18.5, 68.1, 7.6), "10 mm"),
      ((21.5, 68.1, 10.0), (21.5, 68.1, 15.0), "5 mm")]),
]


PLATE = [
    (-52, 26, None, 1.0, "Isometric", "box + fin + plate hanging below on the 10 x 50 x 7 neck", []),
    (-90, -11, None, 1.0, "Low front view", "7 mm belt gap between box bottom and plate", []),
    (-72, -42, None, 1.0, "From below", "plate 80 x 50 x 5, neck at the right end", []),
    (100, 10, (89.0, 34.0, -4.0), 3.6, "Close-up: neck + slot",
     "neck 10 x 50 x 7, slot 70 x 50 x 7",
     [((89.0, 59.0, -7.0), (89.0, 59.0, 0.0), "7 mm")]),
]


def main(stl="box_with_fin.stl", out="box_3d_model.png", variant="plain"):
    tris = load_stl(stl)
    W, H, ss = 1000, 720, 3
    views = {"holes": HOLES, "plate": PLATE}.get(variant, PLAIN)
    panels = []
    for az, el, fo, zm, t, sub, ann in views:
        cam = Cam(tris, az, el, W, H, focus=fo, zoom=zm)
        im, zb, front, n = render(tris, cam, ss)
        im = draw_edges(im, tris, zb, ss, cam, front, n)
        for A, B, txt in ann:
            annotate(im, cam, A, B, txt)
        panels.append(label(im, t, sub))
    gap, pad = 12, 22
    sheet = Image.new("RGB", (W * 2 + gap + pad * 2, H * 2 + gap + pad * 2), (246, 248, 251))
    for i, p in enumerate(panels):
        sheet.paste(p, (pad + (i % 2) * (W + gap), pad + (i // 2) * (H + gap)))
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(*(a + ["box_with_fin.stl", "box_3d_model.png", "plain"][len(a):]))
