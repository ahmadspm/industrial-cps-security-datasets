import gzip,json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from pathlib import Path
rows=[json.loads(x) for x in gzip.open('/tmp/events.gz','rt')]
groups=collections.defaultdict(list)
for r in rows:
    if isinstance(r.get('relative_seconds'),(float,int)): groups[r['trace_id']].append(r)
name=max(groups,key=lambda k:len(groups[k]))
records=sorted(groups[name],key=lambda r:r['relative_seconds'])
times=[r['relative_seconds'] for r in records]
gaps=[b-a for a,b in zip(times,times[1:])]
fig,axes=plt.subplots(2,1,figsize=(12,5),layout='constrained')
fig.patch.set_facecolor('white')
fig.suptitle('Recorded operational event replay · '+name,fontsize=14)
for ax in axes:
    ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
axes[0].set(xlabel='Elapsed trace time (s)',ylabel='Cumulative events',xlim=(0,max(times) or 1),ylim=(0,len(times)))
axes[1].set(xlabel='Event interval index',ylabel='Inter-event interval (s)',xlim=(0,max(1,len(gaps))),ylim=(0,max(gaps or [1])*1.05))
l1,=axes[0].plot([],[],color='#087f9c',linewidth=2)
l2,=axes[1].plot([],[],color='#dc8b35',linewidth=1)
def update(frame):
    n=max(2,int(len(times)*(frame+1)/40))
    l1.set_data(times[:n],range(1,n+1));l2.set_data(range(len(gaps[:n-1])),gaps[:n-1]);return l1,l2
out=Path('public/assets/operational-trace-replay.gif')
FuncAnimation(fig,update,frames=40,interval=120).save(out,writer=PillowWriter(fps=8))
print(name,len(records),out)
