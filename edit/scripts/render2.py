import json, subprocess, sys, numpy as np, cv2
sys.path.insert(0,'/tmp/claude-0/work')
from analyze import smooth
CL='/tmp/claude-0/-home-user-trialcheck/e200e00b-2842-5fd8-9752-6982b5d73dda/scratchpad/clips'
OW,OH=1080,1920; BASE=1.06; ZCAP=1.42; STEP=18   # 18 frames/step = 100 BPM at 30 fps
def frames(name):
    p=subprocess.run(['ffmpeg','-v','error','-i',f'{CL}/{name}.mp4','-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,1920,1080,3)
def track(name):
    d=json.load(open(f'/tmp/claude-0/work/{name}.json')); W,H=d['W'],d['H']; n=len(d['frames'])
    bh=np.full(n,np.nan); cx=np.full(n,np.nan); cy=np.full(n,np.nan)
    for i,f in enumerate(d['frames']):
        if f: x1,y1,x2,y2=f['box']; bh[i]=(y2-y1)/H; cx[i]=(x1+x2)/2/W; cy[i]=(y1+y2)/2/H
    return smooth(bh,7),smooth(cx,7),smooth(cy,7)
def crop(img,z,ccx,ccy):
    w=OW/z; h=OH/z
    x=np.clip(ccx*OW-w/2,0,OW-w); y=np.clip(ccy*OH-h/2,0,OH-h)
    M=np.float32([[z,0,-x*z],[0,z,-y*z]])
    return cv2.warpAffine(img,M,(OW,OH),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
def ccenter(sx,sy,tx,ty,z):
    # crop centre so that source point (sx,sy) lands at display (tx,ty)
    return sx-(tx-0.5)/z, sy-(ty-0.5)/z
def main(plan,out):
    plan=json.load(open(plan))
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{OW}x{OH}','-r','30','-i','-',
        '-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',out],stdin=subprocess.PIPE)
    names={'F':'video_20241124_111755','H':'video_20241124_182031','Y':'video_20241125_105724','O':'video_20241125_150317',
           'S':'video_20241125_155557','D':'video_20241126_103842','A':'video_20241128_162531','X':'video_20241126_171319'}
    log=[]; t_out=0; D=None; tx=ty=None
    for si,(k,fin,fout,zin,zout,_) in enumerate(plan):
        name=names[k]; V=frames(name); bh,cx,cy=track(name); n=len(V)
        if si==0:
            # opening: natural framing, back close-up -> 2 steps, trimmed to exactly 2 beats ending on the downstep
            nout=2*STEP; src=np.arange(nout)+ (fout-nout)
            for s in src:
                i=int(round(s)); ff.stdin.write(crop(V[i],BASE,0.5,0.5).tobytes())
            i=int(round(fout)); D=bh[i]*BASE   # display state at the downstep frame the next clip opens on
            tx=(cx[i]-0.5)*BASE+0.5; ty=(cy[i]-0.5)*BASE+0.5
            log.append((k,name,int(round(src[0])),i,t_out,nout)); t_out+=nout; continue
        if k!='X':
            src=np.linspace(fin,fout,STEP+1)[:-1]   # open on this downstep, stop one frame before the next
            seq=[]
            for s in src:
                i=int(round(s)); z=np.clip(D/bh[i],BASE,ZCAP)
                seq.append((i,z,*ccenter(cx[i],cy[i],tx,ty,z)))
            for i,z,a,b in seq: ff.stdin.write(crop(V[i],z,a,b).tobytes())
            iL=int(round(fout)); D=bh[iL]*np.clip(D/bh[iL],BASE,ZCAP)
            log.append((k,name,seq[0][0],iL,t_out,STEP)); t_out+=STEP
        else:
            i0=int(round(fin)); idx=list(range(i0,n)); seq=[]
            # finale: keep the subject lock (zoom capped) so her turn to camera stays readable;
            # horizontal target eases to centre over the first 1.5 s
            for j,i in enumerate(idx):
                z=np.clip(D/bh[i],BASE,ZCAP); u=min(1,j/45); u=u*u*(3-2*u)
                seq.append((i,z,*ccenter(cx[i],cy[i],tx*(1-u)+0.5*u,ty,z)))
            zs=smooth(np.array([q[1] for q in seq]),9); a_=smooth(np.array([q[2] for q in seq]),9); b_=smooth(np.array([q[3] for q in seq]),9)
            seq=[(q[0],zs[j],a_[j],b_[j]) for j,q in enumerate(seq)]
            for i,z,a,b in seq: ff.stdin.write(crop(V[i],z,a,b).tobytes())
            log.append((k,name,i0,idx[-1],t_out,len(seq))); t_out+=len(seq)
        del V
    ff.stdin.close(); ff.wait()
    json.dump(log,open(out+'.edl.json','w'))
    for l in log: print(l)
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
