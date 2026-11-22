"""Engineering views (mm) - box + fin + strap plate, edges filleted r = 2 mm."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

R = 2.0
FIN = dict(x0=12, x1=15, y0=4, y1=7, z0=4, z1=21)
NECK = dict(x0=84, x1=94, y0=9, y1=59, z0=-7, z1=0)
PLATE = dict(x0=14, x1=94, y0=9, y1=59, z0=-12, z1=-7)

FILL = "#bfd0e6"
FILL2 = "#a9bdd8"
EDGE = "#2f4257"
DIM = "#c0264a"
DIM2 = "#155e75"


def rpath(x0, x1, y0, y1, r=R, corners=("bl", "br", "tr", "tl")):
    pts = []

    def arc(cx, cy, a0, a1):
        for t in np.linspace(a0, a1, 14):
            pts.append((cx + r * np.cos(t), cy + r * np.sin(t)))

    if "bl" in corners:
        arc(x0 + r, y0 + r, np.pi, 1.5 * np.pi)
    else:
        pts.append((x0, y0))
    if "br" in corners:
        arc(x1 - r, y0 + r, 1.5 * np.pi, 2 * np.pi)
    else:
        pts.append((x1, y0))
    if "tr" in corners:
        arc(x1 - r, y1 - r, 0, 0.5 * np.pi)
    else:
        pts.append((x1, y1))
    if "tl" in corners:
        arc(x0 + r, y1 - r, 0.5 * np.pi, np.pi)
    else:
        pts.append((x0, y1))
    return pts


def shape(ax, x0, x1, y0, y1, r=R, corners=("bl", "br", "tr", "tl"),
          fc=FILL, ec=EDGE, lw=1.7, ls="-", z=2, hatch=None, alpha=1):
    ax.add_patch(Polygon(rpath(x0, x1, y0, y1, r, corners), closed=True,
                         fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, hatch=hatch, alpha=alpha))


def rect(ax, x0, x1, y0, y1, fc="white", ec=EDGE, lw=1.4, ls="-", z=2, hatch=None):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, hatch=hatch))


def dim(ax, x1, y1, x2, y2, txt, color=DIM, fs=12, off=(0, 0), rot=0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=6,
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.5,
                                shrinkA=0, shrinkB=0, mutation_scale=12))
    ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], txt, color=color,
            fontsize=fs, ha="center", va="center", rotation=rot, fontweight="bold",
            zorder=7, bbox=dict(fc="white", ec="none", pad=1.0))


def note(ax, x, y, txt, color=DIM2, fs=10.5, ha="left"):
    ax.text(x, y, txt, color=color, fontsize=fs, ha=ha, va="center", zorder=8,
            bbox=dict(fc="white", ec="none", pad=0.8, alpha=.9))


def leader(ax, xy, xytext, txt, color="#8a5a2b", fs=10):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=fs, color=color, fontweight="bold",
                zorder=9, ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color=color, lw=1.3,
                                connectionstyle="arc3,rad=0.25"),
                bbox=dict(fc="white", ec="none", pad=1.0))


def frame(ax, title, xlim, ylim, xl, yl):
    ax.set_title(title, fontsize=14, fontweight="bold", color="#16233a", pad=10)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xlabel(xl, fontsize=11); ax.set_ylabel(yl, fontsize=11)
    ax.grid(alpha=.25, lw=.6); ax.tick_params(labelsize=9)


fig, axs = plt.subplots(2, 2, figsize=(19, 13))

# ---------------- 1 TOP VIEW ----------------
ax = axs[0][0]
rect(ax, 0, 108, 0, 68, fc=FILL)
rect(ax, 4, 104, 4, 64)
rect(ax, FIN["x0"], FIN["x1"], FIN["y0"], FIN["y1"], fc=FILL2)
shape(ax, PLATE["x0"], PLATE["x1"], PLATE["y0"], PLATE["y1"], fc="none",
      ls=(0, (7, 4)), lw=1.5, ec="#5a6f88", z=3)
shape(ax, NECK["x0"], NECK["x1"], NECK["y0"], NECK["y1"], fc="none",
      ls=(0, (7, 4)), lw=1.5, ec="#8a5a2b", z=3)
frame(ax, "1 - TOP VIEW  (looking down into the open box)", (-26, 122), (-24, 82), "X (mm)", "Y (mm)")
dim(ax, 0, -12, 108, -12, "108", off=(0, -7))
dim(ax, -12, 0, -12, 68, "68", off=(-7, 0), rot=90)
dim(ax, PLATE["x0"], 68 + 9, PLATE["x1"], 68 + 9, "plate 80", color=DIM2, fs=11, off=(0, 5))
dim(ax, 108 + 10, PLATE["y0"], 108 + 10, PLATE["y1"], "50", color=DIM2, fs=11, off=(6, 0), rot=90)
dim(ax, 4, 21, FIN["x0"], 21, "8", off=(0, -5))
note(ax, 30, 30, "fin: 3 thick, 17 tall\n(8 mm from the left inner face)")
note(ax, 46, 74, "plate 80 x 50 (hidden below)", color="#5a6f88", ha="center")
note(ax, 96, 66, "neck 10 x 50 (hidden)", color="#8a5a2b")
note(ax, 52, 11, "inner cavity 100 x 60", color="#33475e", ha="center")
leader(ax, (94 - 0.6, 59 - 0.6), (72, 47), "plate corners r2")

# ---------------- 2 FRONT VIEW ----------------
ax = axs[0][1]
shape(ax, 0, 108, 0, 44, fc=FILL, corners=("bl", "br"))
rect(ax, 4, 104, 4, 44)
rect(ax, FIN["x0"], FIN["x1"], FIN["z0"], FIN["z1"], fc="none", ls=(0, (5, 3)), ec="#5a6f88")
shape(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc=FILL2)
shape(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc=FILL)
frame(ax, "2 - FRONT VIEW  (from the fin side)", (-26, 130), (-32, 60), "X (mm)", "Z (mm)")
dim(ax, PLATE["x0"], -22, PLATE["x1"], -22, "plate 80", color=DIM2, off=(0, -6))
dim(ax, NECK["x0"], 52, NECK["x1"], 52, "neck 10", color=DIM2, off=(0, 5))
dim(ax, 114, PLATE["z0"], 114, PLATE["z1"], "5", color=DIM2, off=(7, 0), rot=90)
dim(ax, 120, 0, 120, -7, "7", off=(8, 0), rot=90)
note(ax, 22, -18, "slot 70 x 50 x 7  ->  belt goes here", color=DIM, fs=11)
note(ax, 26, 33, "fin (hidden)", color="#5a6f88")
leader(ax, (2 - 1.4, 2 - 1.4), (16, 8), "box bottom edge r2", color="#0f766e")
leader(ax, (94 - 1.6, -7 - 1.6), (74, -27), "plate + neck r2", color="#8a5a2b")

# ---------------- 3 SIDE VIEW ----------------
ax = axs[1][0]
shape(ax, 0, 68, 0, 44, fc=FILL, corners=("bl", "br"))
rect(ax, 4, 64, 4, 44)
shape(ax, NECK["y0"], NECK["y1"], NECK["z0"], NECK["z1"], fc=FILL2)
shape(ax, PLATE["y0"], PLATE["y1"], PLATE["z0"], PLATE["z1"], fc=FILL)
frame(ax, "3 - SIDE VIEW  (from the right end, neck face)", (-24, 94), (-32, 60), "Y (mm)", "Z (mm)")
dim(ax, 0, -22, 68, -22, "68", off=(0, -6))
dim(ax, -10, PLATE["y0"], -10, PLATE["y1"], "50", color=DIM2, off=(-7, 0), rot=90)
dim(ax, 78, 0, 78, 44, "44", off=(8, 0), rot=90)
dim(ax, 78, 0, 78, -7, "7", off=(8, 0), rot=90)
dim(ax, 74, PLATE["z0"], 74, PLATE["z1"], "5", color=DIM2, off=(7, 0), rot=90)
dim(ax, PLATE["y1"], -16, 68, -16, "9", off=(0, 6), fs=10)
dim(ax, 0, -16, PLATE["y0"], -16, "9", off=(0, 6), fs=10)
note(ax, 34, 56, "plate + neck span the full 50 mm width", color=DIM2, ha="center")
leader(ax, (9 + 1.2, -12 + 1.2), (26, -22), "all edges r2", color="#8a5a2b")

# ---------------- 4 SECTION A-A ----------------
ax = axs[1][1]
shape(ax, 0, 4, 0, 44, fc=FILL, hatch="////", lw=0, corners=("bl",))
shape(ax, 104, 108, 0, 44, fc=FILL, hatch="////", lw=0, corners=("br",))
rect(ax, 4, 104, 0, 4, fc=FILL, hatch="////", lw=0)
shape(ax, 0, 108, 0, 44, fc="none", corners=("bl", "br"), lw=1.8)
ax.plot([4, 4], [4, 44], color=EDGE, lw=1.2, zorder=3)
ax.plot([104, 104], [4, 44], color=EDGE, lw=1.2, zorder=3)
ax.plot([4, 104], [4, 4], color=EDGE, lw=1.2, zorder=3)
shape(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc=FILL2, hatch="////", lw=0, z=3)
shape(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc="none", z=4)
shape(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc=FILL, hatch="////", lw=0, z=3)
shape(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc="none", z=4)
rect(ax, FIN["x0"], FIN["x1"], FIN["z0"], FIN["z1"], fc="none", ls=(0, (5, 3)), ec="#5a6f88")
frame(ax, "4 - SECTION A-A  (cut at Y = 34 mm)", (-26, 130), (-32, 60), "X (mm)", "Z (mm)")
dim(ax, 4, -22, PLATE["x0"], -22, "10", off=(0, 6), fs=10)
dim(ax, PLATE["x0"], -22, NECK["x0"], -22, "70 slot", off=(0, -6))
dim(ax, NECK["x0"], -22, 94, -22, "10", off=(0, 6), fs=10)
dim(ax, 94, -22, 104, -22, "10", off=(0, 6), fs=10)
dim(ax, 112, 0, 112, -7, "7 gap", off=(15, 0), rot=90, fs=10)
ax.annotate("", xy=(NECK["x0"] - 2, -3.5), xytext=(PLATE["x0"] + 2, -3.5),
            arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.3))
note(ax, 34, -3.5, "belt passage", color=DIM, ha="center")
note(ax, 30, 30, "fin (hidden behind cut)", color="#5a6f88")
leader(ax, (106 - 1.2, 2 - 1.2), (86, 12), "r2", color="#0f766e")

fig.suptitle("box 108 x 68 x 44  +  fin 3 x 3 x 17  +  plate 80 x 50 x 5 on 10 x 50 x 7 neck   -   edges filleted r = 2 mm",
             fontsize=16.5, fontweight="bold", color="#0f1b2b", y=0.985)
plt.tight_layout(rect=[0, 0, 1, 0.965])
plt.savefig("plate_views_rounded.png", dpi=115)
print("wrote plate_views_rounded.png")
