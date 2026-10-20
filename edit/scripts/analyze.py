import json, sys, glob, numpy as np
# COCO kp: 5 Lsh 6 Rsh 11 Lhip 12 Rhip 13 Lknee 14 Rknee 15 Lank 16 Rank
def load(name):
    d=json.load(open(f'/tmp/claude-0/work/{name}.json')); W,H=d['W'],d['H']
    fr=d['frames']; n=len(fr)
    S=np.full(n,np.nan); CX=np.full(n,np.nan); CY=np.full(n,np.nan); DY=np.full(n,np.nan); BH=np.full(n,np.nan); FY=np.full(n,np.nan)
    for i,f in enumerate(fr):
        if not f: continue
        k=np.array(f['kp']); c=k[:,2]
        parts=[]
        if c[5]>.5 and c[6]>.5: parts.append(np.hypot(*(k[5,:2]-k[6,:2]))/0.23)
        if c[11]>.5 and c[12]>.5: parts.append(np.hypot(*(k[11,:2]-k[12,:2]))/0.17)
        if min(c[[5,6,11,12]])>.5: parts.append(abs((k[11,1]+k[12,1])/2-(k[5,1]+k[6,1])/2)/0.30)
        if parts: S[i]=np.median(parts)/H   # ~ apparent body height as fraction of frame height
        if min(c[[5,6,11,12]])>.4:
            CX[i]=k[[5,6,11,12],0].mean()/W; CY[i]=k[[5,6,11,12],1].mean()/H
        if c[15]>.4 and c[16]>.4:
            DY[i]=k[15,1]-k[16,1]; FY[i]=max(k[15,1],k[16,1])/H
        b=f['box']; BH[i]=(b[3]-b[1])/H
    return dict(S=S,CX=CX,CY=CY,DY=DY,BH=BH,FY=FY,n=n)
def smooth(x,w=5):
    y=x.copy(); m=~np.isnan(x)
    if m.sum()<w: return y
    idx=np.arange(len(x)); xi=np.interp(idx,idx[m],x[m])
    k=np.ones(w)/w; ys=np.convolve(np.pad(xi,w//2,mode='edge'),k,'valid'); ys[~m]=np.nan
    return ys
def strikes(DY,fps=30):
    d=smooth(DY,3); out=[]
    for i in range(2,len(d)-2):
        if np.isnan(d[i-2:i+3]).any(): continue
        if abs(d[i])>=np.max(np.abs(d[i-4 if i>=4 else 0:i+5])) and abs(d[i])>8:
            out.append((i,'L' if d[i]<0 else 'R'))   # foot further away (smaller y) = forward/planting foot
    # dedupe within 6 frames
    res=[]
    for s in out:
        if res and s[0]-res[-1][0]<6: continue
        res.append(s)
    return res
if __name__=='__main__':
    for p in sorted(glob.glob('/tmp/claude-0/work/video_*.json')):
        n=p.split('/')[-1][:-5]; a=load(n); st=strikes(a['DY'])
        print(n, 'frames',a['n'],'strikes:',' '.join(f"{i}{s}(S={a['S'][i]:.2f},cx={a['CX'][i]:.2f})" for i,s in st))
