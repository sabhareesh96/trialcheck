import sys, json, subprocess, numpy as np
import torch; torch.set_num_threads(1)
from ultralytics import YOLO
model = YOLO('/tmp/claude-0/models/yolo11s-pose.pt')
W,H = 540,960
def frames(path):
    p = subprocess.Popen(['ffmpeg','-v','error','-i',path,'-vf',f'scale={W}:{H}','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
    n=W*H*3
    while True:
        b=p.stdout.read(n)
        if len(b)<n: break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3)
for path in sys.argv[1:]:
    out=[]; prev=None
    for i,f in enumerate(frames(path)):
        r = model.predict(f, imgsz=480, verbose=False, conf=0.25)[0]
        best=None
        if r.boxes is not None and len(r.boxes):
            bx=r.boxes.xyxy.numpy(); kp=r.keypoints.data.numpy(); cf=r.boxes.conf.numpy()
            scores=[]
            for j,b in enumerate(bx):
                area=(b[2]-b[0])*(b[3]-b[1]); cx=(b[0]+b[2])/2
                s=area/(W*H) - abs(cx-W/2)/W*0.5
                if prev is not None:
                    pb=np.array(prev['box']); 
                    ix=max(0,min(b[2],pb[2])-max(b[0],pb[0])); iy=max(0,min(b[3],pb[3])-max(b[1],pb[1]))
                    iou=ix*iy/((b[2]-b[0])*(b[3]-b[1])+(pb[2]-pb[0])*(pb[3]-pb[1])-ix*iy+1e-6)
                    s+=iou*2
                scores.append(s)
            j=int(np.argmax(scores))
            best={'box':bx[j].round(1).tolist(),'conf':round(float(cf[j]),3),'kp':kp[j].round(1).tolist(),'n':len(bx)}
            prev=best
        out.append(best)
    name=path.split('/')[-1].replace('.mp4','')
    json.dump({'W':W,'H':H,'frames':out},open(f'/tmp/claude-0/work/{name}.json','w'))
    print(name,len(out),flush=True)
