import sys, json, numpy as np
sys.path.insert(0,'.')
from gait import fit
from analyze import smooth
BASE=1.06; ZCAP=1.50; TOL=1.03
C={'H':('video_20241124_182031',130,'hollywood',(59,77)),'S':('video_20241125_155557',120,'seaworld',(45,62)),
   'D':('video_20241126_103842',115,'frame',(47,64)),'A':('video_20241128_162531',105,'safari',(49,67)),
   'O':('video_20241125_150317',110,'101',(43,60)),'Y':('video_20241125_105724',130,'yellow',(58,75)),
   'T':('video_20241128_162421',100,'safari',None),'P':('video_20241128_162602',75,'safari',None),
   'Q':('video_20241126_103953',110,'frame',None),
   'X':('video_20241126_171319',140,'desert',None)}
EV={}
for k,(n,hi,loc,used) in C.items():
    T,st,r2,a=fit(n,0,hi); bh=smooth(a['BH'],7); N=len(bh)
    g=lambda f: float(np.interp(f,np.arange(N),bh))
    ev=[]
    for i,(f,s) in enumerate(st):
        if 0<f<N-1: ev.append((float(f),('S',s),g(f)))
        if i+1<len(st):
            m=(f+st[i+1][0])/2
            if 0<m<N-1: ev.append((float(m),('M',s),g(m)))
    EV[k]=sorted(ev)
def nxt(lab):  # label of the event half a step later
    t,f=lab; return ('M',f) if t=='S' else ('S','R' if f=='L' else 'L')
NS=int(sys.argv[1]) if len(sys.argv)>1 else 8
start=(0.753*BASE, ('S','L'))      # display height + label after the main 1-step section (Yellow out)
best=[None]
def ok_range(k,a,b):
    u=C[k][3]
    return u is None or b<=u[0] or a>=u[1]
def rec(slot,D,lab,path,cost,lastloc,usedk):
    if best[0] and cost>=best[0][0]: return
    if slot==NS:
        for f,l,bh in EV['X']:
            if l==lab and bh<=D*TOL and BASE<=D/bh<=1.42 and C['X'][2]!=lastloc:
                c=cost+(max(BASE,D/bh)-BASE)**2+ 4*max(0,0.62-D)**2
                if not best[0] or c<best[0][0]: best[0]=(c,path+[('X',f,None,max(BASE,D/bh),None,D)])
        return
    for k,ev in EV.items():
        if k=='X' or k in usedk or C[k][2]==lastloc: continue
        for j in range(len(ev)-1):
            f,l,bh=ev[j]; f2,l2,bh2=ev[j+1]
            if l!=lab or l2!=nxt(lab): continue
            if bh>D*TOL: continue
            zin=max(BASE,D/bh)
            if zin>ZCAP: continue
            if not ok_range(k,f,f2): continue
            zout=min(ZCAP,max(BASE,D/bh2)); D2=bh2*zout
            c=cost+(zin-BASE)**2+(zout-BASE)**2+3*(D-D2)**2+ 4*max(0,0.66-D2)**2
            rec(slot+1,D2,l2,path+[(k,f,f2,zin,zout,D)],c,C[k][2],usedk|{k})
rec(0,start[0],start[1],[],0,'yellow',frozenset())
c,p=best[0]; print('cost',round(c,3))
for s in p: print(' ',s[0],C[s[0]][0],'in',round(s[1],1),'out',s[2] and round(s[2],1),'zin',round(s[3],3),'zout',s[4] and round(s[4],3),'D',round(s[5],3))
json.dump(p,open('shuffle.json','w'))
