import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

INK="#0B0E14"; TEXT="#E8EBF0"; MUTED="#8A94A6"; SODIUM="#F2A93B"; DIM="#8A6224"; HAIR="#252C3A"
OUT="/mnt/user-data/uploads/Dev/hackathon/roshni/out"

def style(ax):
    ax.set_facecolor(INK)
    for s in ("top","right"): ax.spines[s].set_visible(False)
    for s in ("bottom","left"):
        ax.spines[s].set_color(HAIR); ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=9, length=3, width=0.8)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)

# ---------- scatter: convergent validation, real data ----------
F=json.load(open(f"{OUT}/segments.geojson"))["features"]
a=np.array([f["properties"]["exposure"]["activity"] for f in F])
s=np.array([f["properties"]["exposure"]["structural"] for f in F])
rho=spearmanr(a,s).statistic
ra=a.argsort().argsort()/(len(a)-1); rs=s.argsort().argsort()/(len(s)-1)

fig=plt.figure(figsize=(7.6,5.0), dpi=200, facecolor=INK)
gs=fig.add_gridspec(1,2,width_ratios=[3.1,1.0],wspace=0.34,left=0.09,right=0.98,top=0.90,bottom=0.13)

ax=fig.add_subplot(gs[0,0]); style(ax)
ax.scatter(ra,rs,s=2.2,c=MUTED,alpha=0.16,linewidths=0)
bins=np.linspace(0,1,26); idx=np.digitize(ra,bins)-1
mx=[ra[idx==i].mean() for i in range(25) if (idx==i).sum()>8]
my=[rs[idx==i].mean() for i in range(25) if (idx==i).sum()>8]
ax.plot(mx,my,color=SODIUM,lw=2.4,zorder=5)
ax.set_xlabel("activity rank  (night-active POIs)",fontsize=10)
ax.set_ylabel("structural rank  (betweenness + night bus)",fontsize=10)
ax.set_xlim(-0.02,1.02); ax.set_ylim(-0.02,1.02)
ax.set_xticks([0,.5,1]); ax.set_yticks([0,.5,1])
ax.text(0.03,0.93,f"ρ = +{rho:.2f}",color=SODIUM,fontsize=19,fontweight="bold",transform=ax.transAxes)
ax.text(0.03,0.86,f"n = {len(a):,} segments  ·  98.4% of the network connected",
        color=MUTED,fontsize=9,transform=ax.transAxes)

bx=fig.add_subplot(gs[0,1]); style(bx)
bx.bar([0,1],[0.031,0.302],width=0.56,color=[DIM,SODIUM])
bx.set_xticks([0,1]); bx.set_xticklabels(["before","after"],fontsize=10)
bx.set_ylim(0,0.36); bx.set_yticks([0,0.1,0.2,0.3])
bx.set_title("ρ, same measurement",color=MUTED,fontsize=9.5,pad=8)
for x,v,c in ((0,0.031,MUTED),(1,0.302,TEXT)):
    bx.text(x,v+0.012,f"{v:.2f}",ha="center",color=c,fontsize=11,fontweight="bold")
bx.text(0.5,-0.20,"graph keyed on rounded\ncoords → on OSM node ids",
        ha="center",va="top",color=MUTED,fontsize=8.4,transform=bx.transAxes)
fig.savefig("assets/chart-scatter.png",facecolor=INK)
plt.close(fig)

# ---------- complaint categories ----------
cats=[("Street light not working",39847),("Garbage dump",16137),
      ("Garbage vehicle not arrived",12135),("Sweeping not done",3641),("Road side drains",3269)]
fig,ax=plt.subplots(figsize=(6.6,3.9),dpi=200,facecolor=INK); style(ax)
y=np.arange(len(cats))[::-1]
ax.barh(y,[c[1] for c in cats],height=0.62,color=[SODIUM]+[DIM]*4)
ax.set_yticks(y); ax.set_yticklabels([c[0] for c in cats],fontsize=10,color=TEXT)
ax.set_xlim(0,46000); ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
for yy,(_,v) in zip(y,cats):
    ax.text(v+900,yy,f"{v:,}",va="center",color=TEXT if v>20000 else MUTED,fontsize=10.5,
            fontweight="bold" if v>20000 else "normal")
fig.tight_layout(); fig.savefig("assets/chart-categories.png",facecolor=INK); plt.close(fig)

# ---------- closure rates ----------
fig,ax=plt.subplots(figsize=(5.4,2.5),dpi=200,facecolor=INK); style(ax)
ax.barh([1,0],[96.4,58.0],height=0.5,color=[SODIUM,DIM])
ax.set_yticks([1,0]); ax.set_yticklabels(["Electrical","Road maintenance"],fontsize=11,color=TEXT)
ax.set_xlim(0,112); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.text(98,1,"96.4%",va="center",color=TEXT,fontsize=14,fontweight="bold")
ax.text(59.6,0,"58.0%",va="center",color=MUTED,fontsize=12)
ax.set_title("complaints closed",color=MUTED,fontsize=9.5,loc="left",pad=6)
fig.tight_layout(); fig.savefig("assets/chart-closure.png",facecolor=INK); plt.close(fig)

# ---------- ward complaints ----------
w=[("Jnanabharathi",1345),("Ullalu",1026),("Hemmigepura",983),
   ("Dodda Bidarkallu",967),("Rajarajeshwari Nagar",964)]
fig,ax=plt.subplots(figsize=(6.4,3.5),dpi=200,facecolor=INK); style(ax)
y=np.arange(len(w))[::-1]
ax.barh(y,[x[1] for x in w],height=0.58,color=SODIUM)
ax.set_yticks(y); ax.set_yticklabels([x[0] for x in w],fontsize=10.5,color=TEXT)
ax.set_xlim(0,1600); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
for yy,(_,v) in zip(y,w): ax.text(v+30,yy,f"{v:,}",va="center",color=MUTED,fontsize=10)
ax.set_title("streetlight complaints, 2025, by ward",color=MUTED,fontsize=9.5,loc="left",pad=6)
fig.tight_layout(); fig.savefig("assets/chart-wards.png",facecolor=INK); plt.close(fig)

# ---------- counterfactual with whisker ----------
fig,ax=plt.subplots(figsize=(6.8,3.2),dpi=200,facecolor=INK); style(ax)
ax.barh([1],[4544],height=0.46,color=SODIUM)
ax.barh([0],[588],height=0.46,color=DIM)
ax.errorbar([588],[0],xerr=[[588-461],[735-588]],fmt="none",ecolor=MUTED,elinewidth=1.4,capsize=5)
ax.plot([2410,2410],[-0.30,0.30],color=TEXT,lw=1.4,ls=(0,(4,3)))
ax.text(2470,-0.02,"steelman  2,410",color=TEXT,fontsize=9.5,va="center")
ax.set_yticks([1,0]); ax.set_yticklabels(["Roshni's 40","Complaint order's 40"],fontsize=11,color=TEXT)
ax.set_xlim(0,5400); ax.set_xticks([]); ax.spines["bottom"].set_visible(False)
ax.text(4620,1,"4,544",va="center",color=TEXT,fontsize=13,fontweight="bold")
ax.text(660,0.30,"588",va="center",color=MUTED,fontsize=10.5)
ax.set_title("exposed pedestrian-km restored  ·  whisker = P5–P95 over 300 draws",
             color=MUTED,fontsize=9,loc="left",pad=6)
fig.tight_layout(); fig.savefig("assets/chart-counterfactual.png",facecolor=INK); plt.close(fig)

# ---------- learning curve ----------
c=json.load(open(f"{OUT}/curve.json"))["points"]
t=[(p["reports"],p["ratio"]) for p in c if p["targeted"]]
r=[(p["reports"],p["ratio"]) for p in c if not p["targeted"]]
fig,ax=plt.subplots(figsize=(6.2,3.5),dpi=200,facecolor=INK); style(ax)
ax.plot([x for x,_ in t],[y*100 for _,y in t],color=SODIUM,lw=2.4,marker="o",ms=4,label="reports we asked for")
ax.plot([x for x,_ in r],[y*100 for _,y in r],color=MUTED,lw=1.8,ls=(0,(5,3)),marker="o",ms=3,label="reports at random")
ax.set_xlabel("citizen reports",fontsize=10); ax.set_ylabel("% of a perfect ranking",fontsize=10)
ax.set_ylim(50,82); ax.set_xlim(-12,415)
lg=ax.legend(frameon=False,fontsize=9.5,loc="upper left")
for txt in lg.get_texts(): txt.set_color(TEXT)
ax.annotate("56% with zero reports",xy=(0,55.75),xytext=(46,52.4),color=MUTED,fontsize=9,
            arrowprops=dict(arrowstyle="-",color=HAIR,lw=1))
fig.tight_layout(); fig.savefig("assets/chart-curve.png",facecolor=INK); plt.close(fig)
print("charts written")
