import cv2, numpy as np, json, subprocess
from rembg import remove, new_session
from scipy.ndimage import median_filter
CL='/tmp/claude-0/-home-user-trialcheck/e200e00b-2842-5fd8-9752-6982b5d73dda/scratchpad/clips/video_20241126_171319.mp4'
def frames():
    p=subprocess.run(['ffmpeg','-v','error','-i',CL,'-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True,check=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,1920,1080,3)
def ridge_in_band(im, y0=270, y1=360, subj=None):
    g=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32),(0,0),1.2)
    k=6; ys=[]; 
    band=g[y0-k:y1+k]
    c=np.cumsum(np.vstack([np.zeros((1,band.shape[1])),band]),0)
    y=np.arange(k,band.shape[0]-k)
    sc=(c[y]-c[y-k])/k-(c[y+k]-c[y])/k
    r=(y[np.argmax(sc,0)]+y0-k).astype(float); r[sc.max(0)<3]=np.nan
    if subj is not None: r[(subj[y0-80:y1]>64).any(0)]=np.nan
    xs=np.arange(len(r)); m=~np.isnan(r); r=np.interp(xs,xs[m],r[m])
    return median_filter(r,31,mode='nearest')
def subject_masks(V, idx, boxes, sess):
    out={}
    for i in idx:
        m=remove(V[i],session=sess,only_mask=True).astype(np.float32)/255
        x1,y1,x2,y2=boxes[i]; pad=0.10*(x2-x1)+20
        clip=np.zeros_like(m); clip[max(0,int(y1-pad)):int(y2+pad),max(0,int(x1-pad)):int(x2+pad)]=1
        clip=cv2.GaussianBlur(clip,(0,0),15)
        out[i]=np.clip(m*clip,0,1)
    return out
def shift(ref, im, mref, mim, y0=230, y1=430):
    a=cv2.cvtColor(ref[y0:y1],cv2.COLOR_BGR2GRAY).astype(np.float32); b=cv2.cvtColor(im[y0:y1],cv2.COLOR_BGR2GRAY).astype(np.float32)
    w=(1-np.maximum(mref[y0:y1],mim[y0:y1]))*cv2.createHanningWindow(a.shape[::-1],cv2.CV_32F)
    (dx,dy),resp=cv2.phaseCorrelate(a*w,b*w)
    return dx,dy,resp
