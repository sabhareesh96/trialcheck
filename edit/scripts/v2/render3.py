import json, subprocess, sys, numpy as np, cv2
sys.path.insert(0,'/tmp/claude-0/work'); sys.path.insert(0,'/tmp/claude-0/fin')
from analyze import smooth
from render2 import frames, track, crop, ccenter, OW, OH, BASE
from PIL import Image, ImageDraw, ImageFont
STEP=18; HALF=9
ZCAP_MAIN=1.42; ZCAP_SHUF=1.50
N={'F':'video_20241124_111755','H':'video_20241124_182031','Y':'video_20241125_105724','O':'video_20241125_150317',
   'S':'video_20241125_155557','D':'video_20241126_103842','A':'video_20241128_162531','X':'video_20241126_171319',
   'T':'video_20241128_162421','P':'video_20241128_162602','Q':'video_20241126_103953'}
FONT='/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
cache={}
def clip(k):
    if k not in cache: cache.clear(); cache[k]=(frames(N[k]),*track(N[k]))
    return cache[k]
# ---------- DUBAI title that rises from behind the dune ridge (source coords of the desert clip) ----------
def letter_layers(width_px=680):
    f=ImageFont.truetype(FONT,300); d=ImageDraw.Draw(Image.new('L',(10,10)))
    bb=d.textbbox((0,0),'DUBAI',font=f); s=width_px/(bb[2]-bb[0]); f=ImageFont.truetype(FONT,int(300*s))
    bb=d.textbbox((0,0),'DUBAI',font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    layers=[]; x=-bb[0]
    for ch in 'DUBAI':
        im=Image.new('L',(tw+40,th+40),0); dd=ImageDraw.Draw(im)
        dd.text((x+20,-bb[1]+20),ch,font=f,fill=255)
        layers.append(np.asarray(im).astype(np.float32)/255)
        x+=dd.textlength(ch,font=f)
    return layers,tw,th
LAYERS,TW,TH=letter_layers()
RIDGE=np.load('/tmp/claude-0/fin/ridge_ref.npy'); SHIFT=np.load('/tmp/claude-0/fin/shift.npy'); MASKS=np.load('/tmp/claude-0/fin/masks.npy')
X0=83
def ease_out_back(u,s=1.25):
    u=np.clip(u,0,1)-1; return 1+u*u*((s+1)*u+s)
def title_on(img, i, j):
    """img: source frame i of the desert clip; j: frames since the finale started."""
    dx,dy,_=SHIFT[i-X0]; subj=MASKS[i-X0].astype(np.float32)/255
    H,W=img.shape[:2]
    base_y=float(np.median(RIDGE))+dy+6       # letters' baseline sits just below the ridge
    ox=W/2-TW/2-20+dx
    alpha=np.zeros((H,W),np.float32)
    for li,L in enumerate(LAYERS):
        u=(j-li*3)/20.0
        rise=ease_out_back(u)                   # 0 -> fully hidden below the ridge, 1 -> resting (slight overshoot)
        oy=base_y-TH-20 + (1-rise)*(TH+60)
        vel=abs(ease_out_back(u+0.05)-ease_out_back(u))*(TH+60)
        Lb=L if vel<2 else cv2.blur(L,(1,int(min(vel*2,60))|1))
        y0=int(round(oy)); x0=int(round(ox))
        ya,yb=max(0,y0),min(H,y0+L.shape[0]); xa,xb=max(0,x0),min(W,x0+L.shape[1])
        if yb>ya and xb>xa: alpha[ya:yb,xa:xb]=np.maximum(alpha[ya:yb,xa:xb],Lb[ya-y0:yb-y0,xa-x0:xb-x0])
    # occlusion by the dune: only visible above the ridge line (shifted with the camera)
    xs=np.arange(W); ridge=np.interp(xs-dx,xs,RIDGE)+dy
    yy=np.arange(H)[:,None]; sky=np.clip((ridge[None,:]-yy)/1.5,0,1)
    a=alpha*sky*(1-subj)*0.95
    # colour: warm cream, lit by the sunset; a touch of the sky bleeds through like haze
    grad=np.linspace(0,1,H,dtype=np.float32)[:,None,None]
    col=np.array([236,244,252],np.float32)*(1-0.25*grad)+np.array([180,214,255],np.float32)*0.25*grad   # BGR
    col=col*0.9+img.astype(np.float32)*0.1
    out=img.astype(np.float32)*(1-a[...,None])+col*a[...,None]
    # sun bloom over the letters
    lum=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
    bloom=cv2.GaussianBlur(np.clip(lum-215,0,40)/40,(0,0),25)
    out+= (bloom*a*90)[...,None]*np.array([0.75,0.9,1.0],np.float32)
    return np.clip(out,0,255).astype(np.uint8)
# ---------- whip blur ----------
def vblur(img,k,shift):
    if k>1: img=cv2.blur(img,(1,int(k)|1))
    if shift: img=np.roll(img,int(shift),axis=0)
    return img
def main(out):
    plan=json.load(open('plan.json')); shuf=json.load(open('shuffle.json'))
    frames_out=[]; log=[]
    def emit(im): frames_out.append(im)
    # A. opening + B. main steps (as v3)
    D=tx=ty=None
    for si,(k,fin,fout,zin,zout,_) in enumerate(plan):
        if k=='X': continue
        V,bh,cx,cy=clip(k)
        if si==0:
            src=np.arange(2*STEP)+(fout-2*STEP)
            for s in src: emit(crop(V[int(round(s))],BASE,0.5,0.5))
            i=int(round(fout)); D=bh[i]*BASE; tx=(cx[i]-0.5)*BASE+0.5; ty=(cy[i]-0.5)*BASE+0.5
            log.append(('open',N[k],int(src[0]),i)); continue
        src=np.linspace(fin,fout,STEP+1)[:-1]
        for s in src:
            i=int(round(s)); z=np.clip(D/bh[i],BASE,ZCAP_MAIN); emit(crop(V[i],z,*ccenter(cx[i],cy[i],tx,ty,z)))
        iL=int(round(fout)); D=bh[iL]*np.clip(D/bh[iL],BASE,ZCAP_MAIN); log.append(('step',N[k],int(round(fin)),iL))
    # C. shuffle: half-step cuts on 8th notes
    for k,fin,fout,zin,zout,_ in shuf:
        if k=='X': xin=fin; continue
        V,bh,cx,cy=clip(k)
        src=np.linspace(fin,fout,HALF+1)[:-1]
        for s in src:
            i=int(round(s)); z=np.clip(D/bh[i],BASE,ZCAP_SHUF); emit(crop(V[i],z,*ccenter(cx[i],cy[i],tx,ty,z)))
        iL=int(round(fout)); D=bh[iL]*np.clip(D/bh[iL],BASE,ZCAP_SHUF); log.append(('shuffle',N[k],int(round(fin)),iL))
    # D. finale with the DUBAI title
    V,bh,cx,cy=clip('X'); i0=int(round(xin)); idx=list(range(i0,len(V)))
    seq=[]
    for j,i in enumerate(idx):
        z=np.clip(D/bh[i],BASE,ZCAP_MAIN); u=min(1,j/45); u=u*u*(3-2*u)
        seq.append((i,z,*ccenter(cx[i],cy[i],tx*(1-u)+0.5*u,ty,z)))
    zs=smooth(np.array([q[1] for q in seq]),9); a_=smooth(np.array([q[2] for q in seq]),9); b_=smooth(np.array([q[3] for q in seq]),9)
    fin_frames=[]
    for j,(q) in enumerate(seq):
        i=q[0]; fin_frames.append(crop(title_on(V[i],i,j),zs[j],a_[j],b_[j]))
    TARGET=90
    while len(fin_frames)<TARGET: fin_frames.append(fin_frames[-1])
    fin_frames=fin_frames[:TARGET]
    for w in range(6):   # whip-tilt up out of the desert
        t=(w+1)/6; fin_frames[TARGET-6+w]=vblur(fin_frames[TARGET-6+w],8+t*t*260,int(t*t*420))
    for f in fin_frames: emit(f)
    log.append(('finale',N['X'],i0,idx[-1]))
    # E. drone climb over DUBAI written in the sand
    still=cv2.imread('/tmp/claude-0/drone/drone_still.png'); Hs,Ws=still.shape[:2]
    cxw,cyw=329+1742/2, 1798+414/2+60
    ND=144; grain_rng=np.random.default_rng(3)
    for j in range(ND):
        u=j/(ND-1); e=1-(1-u)**3
        zoom=2.25*(1-e)+1.0*e                      # output px per world px relative to fit
        rot=14*(1-e)
        fit=OW/Ws
        s=fit*zoom
        ccx=cxw*(1-e)+(Ws/2)*e; ccy=cyw*(1-e)+(Hs/2)*e
        M=cv2.getRotationMatrix2D((ccx,ccy),rot,s); M[0,2]+=OW/2-ccx; M[1,2]+=OH/2-ccy
        im=cv2.warpAffine(still,M,(OW,OH),flags=cv2.INTER_LANCZOS4 if s<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        if j<6:
            t=1-(j+1)/7; im=vblur(im,8+t*t*240,-int(t*t*300))
        g=grain_rng.normal(0,3.0,(OH//2,OW//2)).astype(np.float32); g=cv2.resize(g,(OW,OH))
        im=np.clip(im.astype(np.float32)+g[...,None],0,255)
        if j>=ND-24: im=im*(1-(j-(ND-24)+1)/24)**1.5
        emit(im.astype(np.uint8))
    log.append(('drone','procedural',0,ND))
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{OW}x{OH}','-r','30','-i','-',
        '-c:v','libx264','-crf','16','-preset','slow','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for f in frames_out: ff.stdin.write(np.ascontiguousarray(f).tobytes())
    ff.stdin.close(); ff.wait()
    print('frames',len(frames_out)); json.dump(log,open(out+'.log.json','w')); [print(l) for l in log]
if __name__=='__main__': main(sys.argv[1])
