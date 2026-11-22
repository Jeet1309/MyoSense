"""Engineering views (mm) for: box + fin + strap plate on a 10 x 50 x 7 neck."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BOX = dict(x0=0, x1=108, y0=0, y1=68, z0=0, z1=44)
IN = dict(x0=4, x1=104, y0=4, y1=64, z0=4, z1=44)
FIN = dict(x0=12, x1=15, y0=4, y1=7, z0=4, z1=21)
NECK = dict(x0=84, x1=94, y0=9, y1=59, z0=-7, z1=0)
PLATE = dict(x0=14, x1=94, y0=9, y1=59, z0=-12, z1=-7)

FILL = "#bfd0e6"
FILL2 = "#a9bdd8"
EDGE = "#2f4257"
DIM = "#c0264a"
DIM2 = "#155e75"


def rect(ax, x0, x1, y0, y1, fc=FILL, ec=EDGE, lw=1.6, ls="-", z=2, hatch=None, alpha=1):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=lw,
                           ls=ls, zorder=z, hatch=hatch, alpha=alpha))


def dim(ax, x1, y1, x2, y2, txt, color=DIM, fs=12, off=(0, 0), rot=0, ha="center"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=6,
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.5,
                                shrinkA=0, shrinkB=0, mutation_scale=12))
    ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], txt, color=color,
            fontsize=fs, ha=ha, va="center", rotation=rot, fontweight="bold",
            zorder=7, bbox=dict(fc="white", ec="none", pad=1.0))


def note(ax, x, y, txt, color=DIM2, fs=10.5, ha="left", rot=0):
    ax.text(x, y, txt, color=color, fontsize=fs, ha=ha, va="center",
            rotation=rot, zorder=8, bbox=dict(fc="white", ec="none", pad=0.8, alpha=.9))


def frame(ax, title, xlim, ylim, xl, yl):
    ax.set_title(title, fontsize=14, fontweight="bold", color="#16233a", pad=10)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xlabel(xl, fontsize=11); ax.set_ylabel(yl, fontsize=11)
    ax.grid(alpha=.25, lw=.6); ax.tick_params(labelsize=9)


fig, axs = plt.subplots(2, 2, figsize=(19, 13))

# ---------------- TOP VIEW (XY) ----------------
ax = axs[0][0]
rect(ax, 0, 108, 0, 68, fc=FILL)
rect(ax, 4, 104, 4, 64, fc="white", ls="-")
rect(ax, FIN["x0"], FIN["x1"], FIN["y0"], FIN["y1"], fc=FILL2)
rect(ax, PLATE["x0"], PLATE["x1"], PLATE["y0"], PLATE["y1"], fc="none", ls=(0, (7, 4)), lw=1.5, ec="#5a6f88")
rect(ax, NECK["x0"], NECK["x1"], NECK["y0"], NECK["y1"], fc="none", ls=(0, (7, 4)), lw=1.5, ec="#8a5a2b")
frame(ax, "1 - TOP VIEW  (looking down into the open box)", (-26, 122), (-24, 82), "X (mm)", "Y (mm)")
dim(ax, 0, -12, 108, -12, "108", off=(0, -7))
dim(ax, -12, 0, -12, 68, "68", off=(-7, 0), rot=90)
dim(ax, PLATE["x0"], 68 + 9, PLATE["x1"], 68 + 9, "plate 80", color=DIM2, fs=11, off=(0, 5))
dim(ax, 108 + 10, PLATE["y0"], 108 + 10, PLATE["y1"], "50", color=DIM2, fs=11, off=(6, 0), rot=90)
dim(ax, 4, 21, FIN["x0"], 21, "8", off=(0, -5))
note(ax, 30, 30, "fin: 3 thick, 17 tall\n(8 mm from the left inner face)")
note(ax, 46, 74, "plate 80 x 50 (hidden below)", color="#5a6f88", ha="center")
note(ax, 96, 66, "neck 10 x 50 (hidden)", color="#8a5a2b")
note(ax, 52, 12, "inner cavity 100 x 60", color="#33475e", ha="center")

# ---------------- FRONT VIEW (XZ) ----------------
ax = axs[0][1]
rect(ax, 0, 108, 0, 44, fc=FILL)
rect(ax, 4, 104, 4, 44, fc="white", ls="-")
rect(ax, FIN["x0"], FIN["x1"], FIN["z0"], FIN["z1"], fc="none", ls=(0, (5, 3)), ec="#5a6f88", lw=1.4)
rect(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc=FILL2)
rect(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc=FILL)
frame(ax, "2 - FRONT VIEW  (from the fin side)", (-26, 130), (-32, 60), "X (mm)", "Z (mm)")
dim(ax, PLATE["x0"], -22, PLATE["x1"], -22, "plate 80", color=DIM2, off=(0, -6))
dim(ax, NECK["x0"], 52, NECK["x1"], 52, "neck 10", color=DIM2, off=(0, 5))
dim(ax, 112, PLATE["z0"], 112, PLATE["z1"], "5", color=DIM2, off=(7, 0), rot=90)
dim(ax, 118, 0, 118, -7, "7", off=(8, 0), rot=90)
dim(ax, 112, 0, 112, 44, "44", off=(7, 0), rot=90)
ax.annotate("", xy=(104, 0), xytext=(104, -7), arrowprops=dict(arrowstyle="->", color=DIM, lw=1.4, ls=":"))
note(ax, 26, -18, "slot 70 x 50 x 7  -> belt goes here", color=DIM, fs=11)
note(ax, 26, 33, "fin (hidden)", color="#5a6f88")
note(ax, 44, 52, "total height 56", color=DIM, ha="center")
ax.annotate("", xy=(0, 44), xytext=(0, -12), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.2, ls="--"))

# ---------------- SIDE VIEW (YZ) ----------------
ax = axs[1][0]
rect(ax, 0, 68, 0, 44, fc=FILL)
rect(ax, 4, 64, 4, 44, fc="white", ls="-")
rect(ax, NECK["y0"], NECK["y1"], NECK["z0"], NECK["z1"], fc=FILL2)
rect(ax, PLATE["y0"], PLATE["y1"], PLATE["z0"], PLATE["z1"], fc=FILL)
frame(ax, "3 - SIDE VIEW  (from the right end, neck face)", (-24, 94), (-32, 60), "Y (mm)", "Z (mm)")
dim(ax, 0, -20, 68, -20, "68", off=(0, -6))
dim(ax, -10, PLATE["y0"], -10, PLATE["y1"], "50", color=DIM2, off=(-7, 0), rot=90)
dim(ax, 78, PLATE["y0"], 78, PLATE["y1"], "neck 50 wide", color=DIM2, off=(0, 0), rot=90, fs=10)
dim(ax, 74, PLATE["z0"], 74, PLATE["z1"], "5", color=DIM2, off=(7, 0), rot=90)
dim(ax, 74, 0, 74, 44, "44", off=(8, 0), rot=90)
dim(ax, 74, 0, 74, -7, "7", off=(8, 0), rot=90)
dim(ax, PLATE["y1"], -16, 68, -16, "9", off=(0, 6), fs=10)
dim(ax, 0, -16, PLATE["y0"], -16, "9", off=(0, 6), fs=10)
note(ax, 34, 56, "neck + plate span the full 50 mm width", color=DIM2, ha="center")

# ---------------- SECTION A-A (XZ at Y = 34) ----------------
ax = axs[1][1]
rect(ax, 0, 4, 0, 44, fc=FILL, hatch="///", lw=0)
rect(ax, 104, 108, 0, 44, fc=FILL, hatch="///", lw=0)
rect(ax, 4, 104, 0, 4, fc=FILL, hatch="///", lw=0)
rect(ax, 0, 108, 0, 44, fc="none", lw=1.8)
rect(ax, 4, 4, 4, 44, fc="none", lw=1.2, ec=EDGE)
rect(ax, 104, 104, 4, 44, fc="none", lw=1.2, ec=EDGE)
rect(ax, 4, 104, 4, 4, fc="none", lw=1.2, ec=EDGE)
rect(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc=FILL2, hatch="///", lw=0)
rect(ax, NECK["x0"], NECK["x1"], NECK["z0"], NECK["z1"], fc="none", lw=1.6)
rect(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc=FILL, hatch="///", lw=0)
rect(ax, PLATE["x0"], PLATE["x1"], PLATE["z0"], PLATE["z1"], fc="none", lw=1.6)
rect(ax, FIN["x0"], FIN["x1"], FIN["z0"], FIN["z1"], fc="none", ls=(0, (5, 3)), ec="#5a6f88", lw=1.4)
frame(ax, "4 - SECTION A-A  (cut at Y = 34 mm)", (-26, 130), (-32, 60), "X (mm)", "Z (mm)")
dim(ax, 4, -20, PLATE["x0"], -20, "10", off=(0, 6), fs=10)
dim(ax, PLATE["x0"], -20, NECK["x0"], -20, "70 slot", color=DIM, off=(0, -6))
dim(ax, NECK["x0"], -20, 94, -20, "10", off=(0, 6), fs=10)
dim(ax, 94, -20, 104, -20, "10", off=(0, 6), fs=10)
dim(ax, 100, PLATE["z0"], 100, -7, "5 plate", color=DIM2, off=(34, 0), rot=90, fs=10)
dim(ax, 112, 0, 112, -7, "7 gap", off=(16, 0), rot=90, fs=10)
ax.annotate("", xy=(NECK["x0"], -3.5), xytext=(PLATE["x0"], -3.5),
            arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.3))
note(ax, 34, -3.5, "belt passage", color=DIM, ha="center")
note(ax, 30, 30, "fin (hidden behind cut)", color="#5a6f88")

fig.suptitle("box 108 x 68 x 44  +  fin 3 x 3 x 17  +  strap plate 80 x 50 x 5 on a 10 x 50 x 7 neck",
             fontsize=17, fontweight="bold", color="#0f1b2b", y=0.985)
plt.tight_layout(rect=[0, 0, 1, 0.965])
plt.savefig("plate_views_v2.png", dpi=115)
print("wrote plate_views_v2.png")
