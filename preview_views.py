import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

xs=[0,.4,1.2,1.4,10.4,10.8]; ys=[0,.4,.7,6.4,6.8]; zs=[0,.4,2.1,4.4]
def solid(x0,x1,y0,y1,z0,z1):
    floor = z1<=0.4
    wall = x0<0.4 or x1>10.4 or y0<0.4 or y1>6.4
    fin = x0>=1.2-1e-9 and x1<=1.4+1e-9 and y0>=.4-1e-9 and y1<=.7+1e-9 and z1<=2.1+1e-9
    return floor or wall or fin

fig,axs = plt.subplots(1,3,figsize=(16,6))

# TOP VIEW (looking down)
ax=axs[0]; ax.set_title("TOP VIEW (into the open box)")
for i in range(5):
  for j in range(4):
    if solid(xs[i],xs[i+1],ys[j],ys[j+1],0.4,2.1):
        ax.add_patch(Rectangle((xs[i],ys[j]),xs[i+1]-xs[i],ys[j+1]-ys[j],
             fc="#9fb6d4",ec="#33475e",lw=0.8))
for i in range(5):
  for j in range(4):
    if solid(xs[i],xs[i+1],ys[j],ys[j+1],2.1,4.4) and not solid(xs[i],xs[i+1],ys[j],ys[j+1],0.4,2.1):
        ax.add_patch(Rectangle((xs[i],ys[j]),xs[i+1]-xs[i],ys[j+1]-ys[j],
             fc="white",ec="#33475e",lw=0.8,hatch="//"))
ax.annotate("",(1.2,3.4),(0.4,3.4),arrowprops=dict(arrowstyle="<->",color="crimson",lw=1.6))
ax.text(0.55,3.55,"0.8",color="crimson",fontweight="bold")
ax.annotate("",(2.2,1.15),(1.4,1.15),arrowprops=dict(arrowstyle="<->",color="darkgreen",lw=1.4))
ax.text(1.62,1.28,"0.2 thick",color="darkgreen",fontsize=9,fontweight="bold")
ax.annotate("",(2.0,0.95),(2.0,0.4),arrowprops=dict(arrowstyle="<->",color="darkgreen",lw=1.4))
ax.text(2.12,0.55,"0.3 deep",color="darkgreen",fontsize=9,fontweight="bold")
ax.text(3.2,5.2,"inner cavity 10 x 6 cm",fontsize=11)
ax.set_xlim(-.6,11.4); ax.set_ylim(-.6,7.4); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xlabel("X (cm)"); ax.set_ylabel("Y (cm)")

# SECTION at y = 0.55 (through the fin)
ax=axs[1]; ax.set_title("SECTION through fin (Y = 0.55 cm)")
for i in range(5):
  for k in range(3):
    if solid(xs[i],xs[i+1],0.4,0.7,zs[k],zs[k+1]):
        ax.add_patch(Rectangle((xs[i],zs[k]),xs[i+1]-xs[i],zs[k+1]-zs[k],
             fc="#9fb6d4",ec="#33475e",lw=0.8))
ax.annotate("",(1.7,2.1),(1.7,0.4),arrowprops=dict(arrowstyle="<->",color="crimson",lw=1.6))
ax.text(1.8,1.05,"fin 1.7 tall",color="crimson",fontweight="bold")
ax.annotate("",(1.3,2.9),(1.3,4.4),arrowprops=dict(arrowstyle="<->",color="gray",lw=1.2))
ax.text(1.42,3.4,"open top\n(2.3 clear above fin)",fontsize=8,color="gray")
ax.set_xlim(-.6,11.4); ax.set_ylim(-.6,5.0); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xlabel("X (cm)"); ax.set_ylabel("Z (cm)")

# FRONT SECTION at x = 1.3
ax=axs[2]; ax.set_title("CROSS-SECTION X = 1.3 cm")
for j in range(4):
  for k in range(3):
    if solid(1.2,1.4,ys[j],ys[j+1],zs[k],zs[k+1]):
        ax.add_patch(Rectangle((ys[j],zs[k]),ys[j+1]-ys[j],zs[k+1]-zs[k],
             fc="#c9b7d4",ec="#4a3a55",lw=0.8))
for j in range(4):
  for k in range(3):
    if not solid(1.2,1.4,ys[j],ys[j+1],zs[k],zs[k+1]):
        ax.add_patch(Rectangle((ys[j],zs[k]),ys[j+1]-ys[j],zs[k+1]-zs[k],
             fc="none",ec="#bbbbbb",lw=0.5,ls=":"))
ax.text(2.2,1.2,"fin cross-section\n0.3 wide x 1.7 tall",color="#4a3a55",fontweight="bold")
ax.set_xlim(-.4,7.8); ax.set_ylim(-.6,5.0); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.set_xlabel("Y (cm)"); ax.set_ylabel("Z (cm)")
plt.tight_layout(); plt.savefig("box_views.png",dpi=130)
print("ok")
