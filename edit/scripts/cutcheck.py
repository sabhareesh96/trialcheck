import json,subprocess,sys,numpy as np
v,edl,out=sys.argv[1:4]; log=json.load(open(edl))
cuts=[l[4] for l in log[1:]]
raw=subprocess.run(['ffmpeg','-v','error','-i',v,'-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,480,270,3).astype(np.float32)
rows=[]
for c in cuts:
    a,b=F[c-1],F[c]; blend=(a+b)/2
    rows.append(np.concatenate([a,b,blend],1))
img=np.concatenate([np.concatenate(rows[i:i+4],1) if len(rows[i:i+4])==4 else np.concatenate(rows[i:i+4]+[np.zeros_like(rows[0])]*(4-len(rows[i:i+4])),1) for i in range(0,len(rows),4)],0)
subprocess.run(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{img.shape[1]}x{img.shape[0]}','-i','-','-frames:v','1',out],input=img.astype(np.uint8).tobytes())
