import sys, itertools, json, numpy as np
sys.path.insert(0,'.')
from gait import fit
from analyze import load, smooth
CLIPS={'F':('video_20241124_111755',0,90),'H':('video_20241124_182031',0,130),'Y':('video_20241125_105724',0,130),
       'O':('video_20241125_150317',0,110),'S':('video_20241125_155557',0,120),'D':('video_20241126_103842',0,115),
       'A':('video_20241128_162531',0,105),'X':('video_20241126_171319',0,140)}
ST={}; BHs={}
for k,(n,lo,hi) in CLIPS.items():
    T,st,r2,a=fit(n,lo,hi); bh=smooth(a['BH'],5)
    BHs[k]=bh
    ST[k]=[(f,s,float(np.interp(f,np.arange(len(bh)),bh))) for f,s in st if f>0 and f<len(bh)-1]
ZMAX=1.35
TOL=1.03
order=['F','H','Y','O','S','D','A','X']
best=None
def rec(i, D, foot, path, cost):
    global best
    if best and cost>=best[0]: return
    k=order[i]
    if k=='X':   # finale: enter at strike with right foot, BH<=D, z>=1
        for f,s,bh in ST[k]:
            if s==foot and bh<=D*TOL and D/bh<=ZMAX:
                c=cost+(max(1,D/bh)-1)**2
                if not best or c<best[0]: best=(c,path+[(k,f,None,D/bh,None,D)])
        return
    for j,(f,s,bh) in enumerate(ST[k]):
        if s!=foot or bh>D*TOL or D/bh>ZMAX: continue
        zin=max(1.0,D/bh)
        for nsteps in (1,2):
            if j+nsteps>=len(ST[k]): continue
            f2,s2,bh2=ST[k][j+nsteps]
            # choose z_out: keep displayed height as close to D as allowed (constant-scale tracking)
            zout=min(ZMAX,max(1.0,D/bh2)); D2=bh2*zout
            c=cost+(zin-1)**2+(zout-1)**2+ (0.15 if nsteps==2 else 0) + 2*(D-D2)**2 + 3*max(0,0.56-D2)**2
            rec(i+1,D2,s2,path+[(k,f,f2,zin,zout,D)],c)
# opening: F from frame 0 at natural framing until a strike
for perm in itertools.permutations(['H','Y','O','S','D','A']):
    order[:]=['F',*perm,'X']
    for f,s,bh in ST['F']:
        if bh>0.85 or f>80: continue
        rec(1,bh,s,[('F',0,f,1.0,1.0,bh)],0)
print('strikes'); [print(' ',k,[(round(f,1),s,round(b,2)) for f,s,b in v]) for k,v in ST.items()]
print('cost',round(best[0],3))
for p in best[1]: print(' ',p[0],CLIPS[p[0]][0],'in',p[1],'out',p[2],'zin',round(p[3],3),'zout',p[4] and round(p[4],3),'D',round(p[5],3))
json.dump(best[1],open('plan.json','w'))
