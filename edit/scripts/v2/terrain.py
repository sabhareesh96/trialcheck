import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
rng=np.random.default_rng(7)
W,H=2400,4266
FONT='/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
def noise(shape, scale, octaves=4, seed=0):
    r=np.random.default_rng(seed); out=np.zeros(shape,np.float32); amp=1; tot=0
    for o in range(octaves):
        s=max(2,int(scale/(2**o)))
        g=r.standard_normal((shape[0]//s+3, shape[1]//s+3)).astype(np.float32)
        up=cv2.resize(g,(g.shape[1]*s,g.shape[0]*s),interpolation=cv2.INTER_CUBIC)[:shape[0],:shape[1]]
        out+=amp*up; tot+=amp; amp*=0.5
    return out/tot
def letters_mask():
    im=Image.new('L',(W,H),0); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(FONT,560)
    txt='DUBAI'; bb=d.textbbox((0,0),txt,font=f,stroke_width=0)
    tw,th=bb[2]-bb[0],bb[3]-bb[1]
    x=(W-tw)//2-bb[0]; y=int(H*0.47)-th//2-bb[1]
    d.text((x,y),txt,font=f,fill=255)
    m=np.asarray(im).astype(np.float32)/255
    # hand-dug look: slightly wobbly, rounded edges
    wob=noise((H,W),60,3,11)*6
    mx=cv2.remap(m,(np.arange(W)[None,:]+wob).astype(np.float32),(np.arange(H)[:,None]+noise((H,W),60,3,12)*6).astype(np.float32),cv2.INTER_LINEAR)
    return cv2.GaussianBlur(mx,(0,0),3), (x+bb[0],y+bb[1],tw,th)
def heightfield(flat=None):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    h=np.zeros((H,W),np.float32)
    # big dunes: asymmetric crests perpendicular to wind, warped
    wind=np.deg2rad(28); u=xx*np.cos(wind)+yy*np.sin(wind)
    warp=noise((H,W),700,3,1)*260+noise((H,W),220,2,2)*60
    lam=1500.0; ph=((u+warp)/lam)%1.0
    prof=np.where(ph<0.78, ph/0.78, (1-ph)/0.22)       # long windward slope, steep slip face
    prof=cv2.GaussianBlur(prof.astype(np.float32),(0,0),14)
    h+=prof*70
    h+=noise((H,W),900,3,3)*45
    if flat is not None:
        h=h*(1-flat)+np.float32(np.median(h))*flat
    # wind ripples: perpendicular to wind, wavelength ~ 26px, phase-warped
    rip_ph=(u+noise((H,W),300,3,4)*40)/26.0
    ripples=np.abs(np.sin(np.pi*rip_ph))**1.6
    h+=ripples*3.2*(0.6+0.4*noise((H,W),400,2,5))
    h+=noise((H,W),6,2,6)*0.6
    return h
def carve(h, m):
    depth=15; berm=5
    hb=cv2.GaussianBlur(m,(0,0),5)
    out=h - depth*hb + berm*np.clip(cv2.GaussianBlur(m,(0,0),22)-hb,0,1)*3.0
    return out
def footprints(h, pts, foot=11, depth=7):
    for (x,y,ang) in pts:
        k=np.zeros_like(h[:1,:1])
        cv2.ellipse(fp:=np.zeros((64,64),np.float32),(32,32),(int(foot*0.55),foot),ang,0,360,1.0,-1)
        fp=cv2.GaussianBlur(fp,(0,0),2.2)
        x0,y0=int(x)-32,int(y)-32
        if 0<=x0<W-64 and 0<=y0<H-64: h[y0:y0+64,x0:x0+64]-=fp*depth
    return h
def shade(h, sun_az=200, sun_el=11, px=1.0):
    az=np.deg2rad(sun_az)
    # normals
    gx=cv2.Sobel(h,cv2.CV_32F,1,0,ksize=3)/8; gy=cv2.Sobel(h,cv2.CV_32F,0,1,ksize=3)/8
    L=np.array([np.cos(az)*np.cos(np.deg2rad(sun_el)), np.sin(az)*np.cos(np.deg2rad(sun_el)), np.sin(np.deg2rad(sun_el))])
    n=np.dstack([-gx,-gy,np.ones_like(h)]); n/=np.linalg.norm(n,axis=2,keepdims=True)
    lam=np.clip((n*L).sum(2),0,1)
    # cast shadows: rotate so the sun lies toward +x, then running max
    ang=np.rad2deg(az)
    Mr=cv2.getRotationMatrix2D((W/2,H/2),ang,1.0)
    diag=int(np.hypot(W,H))+4
    Mr[0,2]+=(diag-W)/2; Mr[1,2]+=(diag-H)/2
    hr=cv2.warpAffine(h,Mr,(diag,diag),flags=cv2.INTER_LINEAR,borderValue=float(h.min()))
    t=np.tan(np.deg2rad(sun_el)); xs=np.arange(diag,dtype=np.float32)
    v=hr-xs[None,:]*t
    m=np.maximum.accumulate(v[:,::-1],axis=1)[:,::-1]
    m=np.concatenate([m[:,1:],np.full((diag,1),-1e9,np.float32)],1)
    sh=(m+xs[None,:]*t > hr+0.4).astype(np.float32)
    Minv=cv2.invertAffineTransform(Mr)
    shb=cv2.warpAffine(sh,Minv,(W,H),flags=cv2.INTER_LINEAR)
    shb=cv2.GaussianBlur(shb,(0,0),1.6)
    return lam,1-shb
