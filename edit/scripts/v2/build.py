import numpy as np, cv2, sys
sys.path.insert(0,'/tmp/claude-0/drone')
from terrain import *
m,(tx,ty,tw,th)=letters_mask()
flat=np.zeros((H,W),np.float32)
cv2.ellipse(flat,(int(tx+tw/2),int(ty+th/2)),(int(tw*0.72),int(th*1.6)),0,0,360,1.0,-1)
flat=cv2.GaussianBlur(flat,(0,0),160)*0.95
h=heightfield(flat)
h=carve(h,m)
# footprint trail from bottom-right to the end of the word, then a figure standing by the "I"
pts=[]; x,y=tx-260, H-200
endx,endy=tx+40, ty+th+170
N=20
for i in range(N):
    u=i/(N-1); px=x+(endx-x)*u+np.sin(u*5)*40; py=y+(endy-y)*u
    side=1 if i%2 else -1
    ang=np.rad2deg(np.arctan2(endy-y,endx-x))+90
    pts.append((px+side*12*np.cos(np.deg2rad(ang-90+90)),py+side*12*np.sin(np.deg2rad(ang)),ang))
h=footprints(h,pts,foot=17,depth=8)
np.save('h.npy',h)
SUN_AZ=205; SUN_EL=17
lam,sh=shade(h,SUN_AZ,SUN_EL)
alb_noise=noise((H,W),500,3,21)*0.5+0.5
base=np.array([0.80,0.52,0.30],np.float32)[None,None,:]      # RGB sand
alb=base*(0.88+0.22*alb_noise[...,None])
sun=np.array([1.00,0.78,0.52],np.float32); sky=np.array([0.55,0.45,0.50],np.float32)
direct=(lam*sh)[...,None]*sun*1.45
amb=sky*0.95*(0.85+0.15*np.clip((h-h.min())/(np.ptp(h)),0,1))[...,None]
img=alb*(direct+amb)
# figure + long shadow (sun from SUN_AZ -> shadow points away from sun)
fx,fy=endx+10, endy-40
az=np.deg2rad(SUN_AZ); dx,dy=-np.cos(az),-np.sin(az)
# her real silhouette (desert clip, standing frame) stretched into a long sunset shadow
sil=np.load('/tmp/claude-0/fin/masks.npy')[-1].astype(np.float32)/255
ys_,xs_=np.where(sil>0.5); sil=sil[ys_.min():ys_.max(),xs_.min():xs_.max()]
SH_LEN=int(230/np.tan(np.deg2rad(SUN_EL))); SH_W=int(sil.shape[1]/sil.shape[0]*230)
s2=cv2.resize(sil,(SH_W,SH_LEN))[::-1]          # feet at the top row -> anchor at figure
canvas=np.zeros((H,W),np.float32)
ang=np.rad2deg(np.arctan2(dy,dx))-90
pad=SH_LEN+40; tile=np.zeros((2*pad,2*pad),np.float32)
tile[pad:pad+SH_LEN, pad-SH_W//2:pad-SH_W//2+SH_W]=s2
R=cv2.getRotationMatrix2D((pad,pad),-ang,1.0)
tile=cv2.warpAffine(tile,R,(2*pad,2*pad))
x0,y0=int(fx)-pad,int(fy)-pad
ya,yb=max(0,y0),min(H,y0+2*pad); xa,xb=max(0,x0),min(W,x0+2*pad)
canvas[ya:yb,xa:xb]=tile[ya-y0:yb-y0,xa-x0:xb-x0]
shadow=cv2.GaussianBlur(canvas,(0,0),2.5)
img=img*(1-0.55*shadow[...,None])
# the figure from above (~45 px): white skirt, grey jacket shoulders, dark hair
cv2.ellipse(img,(int(fx),int(fy)),(24,20),0,0,360,(0.97,0.94,0.89),-1,lineType=cv2.LINE_AA)
cv2.ellipse(img,(int(fx),int(fy-2)),(17,11),0,0,360,(0.60,0.56,0.55),-1,lineType=cv2.LINE_AA)
cv2.circle(img,(int(fx),int(fy-3)),8,(0.10,0.07,0.06),-1,lineType=cv2.LINE_AA)
# grade: warm, slight vignette, filmic tone map
yy,xx=np.mgrid[0:H,0:W]; vig=1-0.28*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
img=img*vig[...,None]
img=img/(1+img*0.35)*1.25
img=np.clip(img,0,1)
out=(img[...,::-1]*255).astype(np.uint8)
cv2.imwrite('drone_still.png',out)
cv2.imwrite('/tmp/claude-0/-home-user-trialcheck/e200e00b-2842-5fd8-9752-6982b5d73dda/scratchpad/sheets/drone_still_prev.jpg',cv2.resize(out,(540,960)))
crop=out[int(ty-200):int(ty+th+400), int(tx-100):int(tx+tw+300)]
cv2.imwrite('/tmp/claude-0/-home-user-trialcheck/e200e00b-2842-5fd8-9752-6982b5d73dda/scratchpad/sheets/drone_still_crop.jpg',cv2.resize(crop,(crop.shape[1]//2,crop.shape[0]//2)))
print('letters at',tx,ty,tw,th,'figure',fx,fy)
