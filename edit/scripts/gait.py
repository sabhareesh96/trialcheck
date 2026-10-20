import sys; sys.path.insert(0,'/tmp/claude-0/work')
from analyze import load
import numpy as np
def fit(n, lo=None, hi=None):
    a=load(n); DY=a['DY']/ (a['BH']*960); m=~np.isnan(DY)&(a['FY']<0.985)
    idx=np.arange(a['n'])
    if lo is not None: m&=idx>=lo
    if hi is not None: m&=idx<hi
    t=idx[m]; y=DY[m]
    best=None
    for T in np.arange(26,46,0.25):           # stride period (2 steps) in frames
        w=2*np.pi/T
        X=np.c_[np.sin(w*t),np.cos(w*t),np.ones_like(t)]
        c,res,*_=np.linalg.lstsq(X,y,rcond=None)
        r=((X@c-y)**2).sum()
        if best is None or r<best[0]: best=(r,T,c)
    r,T,c=best; w=2*np.pi/T; ph=np.arctan2(c[1],c[0]); A=np.hypot(c[0],c[1])
    # extrema where w t + ph = pi/2 + k pi
    ks=np.arange(-5,20); ts=(np.pi/2+ks*np.pi-ph)/w
    ts=ts[(ts>=t.min()-T/2)&(ts<=t.max()+T/2)]
    foot=['L' if (A*np.sin(w*x+ph))<0 else 'R' for x in ts]   # DY<0 -> left ankle higher (further) = left foot forward
    r2=1-r/((y-y.mean())**2).sum()
    return T, list(zip(np.round(ts,1),foot)), r2, a
if __name__=='__main__':
    for arg in sys.argv[1:]:
        n,*rng=arg.split(':'); lo,hi=(int(rng[0]),int(rng[1])) if rng else (None,None)
        T,st,r2,a=fit(n,lo,hi)
        print(n,f'stride={T:.2f}f step={T/2:.2f}f r2={r2:.2f}')
        print('   ',' '.join(f"{f}{s}(BH{a['BH'][int(round(f))] if 0<=round(f)<a['n'] else float('nan'):.2f})" for f,s in st))
