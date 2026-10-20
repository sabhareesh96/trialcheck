import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, stft, istft
SR=48000; BPM=100; B=60/BPM; DUR=15.0
N=int(SR*(DUR+0.01)); L=np.zeros((2,N),np.float32)
rng=np.random.default_rng(1)
def t_(d): return np.arange(int(d*SR))/SR
def add(sig,at,gain=1.0,pan=0.0,bus=None):
    i=int(round(at*SR)); 
    if sig.ndim==1: sig=np.vstack([sig*np.sqrt(0.5*(1-pan)),sig*np.sqrt(0.5*(1+pan))])*1.4142
    j=min(N,i+sig.shape[1]); (bus if bus is not None else L)[:,i:j]+=gain*sig[:,:j-i]
def filt(x,kind,f,order=2):
    sos=butter(order,f,btype=kind,fs=SR,output='sos'); return sosfilt(sos,x)
def note(n): return 440*2**((n-69)/12)
# ---------- instruments ----------
def kick(d=0.55,punch=1.0):
    t=t_(d); f=44+120*np.exp(-t*32)*punch; ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*6.5); s+=filt(rng.standard_normal(len(t)),'high',2500)*np.exp(-t*300)*0.35
    return np.tanh(s*1.6)
def bass808(f,d,glide=0.0,decay=None):
    t=t_(d); fr=f*(1+glide*np.exp(-t*14)); ph=2*np.pi*np.cumsum(fr)/SR
    env=np.minimum(1,t/0.004)*np.exp(-t/(decay or d*0.55)); env*=np.clip((d-t)/0.03,0,1)
    s=np.sin(ph)*env; return np.tanh(s*2.4)*0.9          # saturation = harmonics that phones can play
def clap():
    t=t_(0.35); n=rng.standard_normal(len(t))
    env=sum(np.exp(-np.clip(t-o,0,None)*120)*(t>=o) for o in (0,0.011,0.022))*0.6+np.exp(-t*14)*0.5
    return filt(filt(n*env,'band',[900,5000]),'high',600)
def hat(open_=False):
    t=t_(0.22 if open_ else 0.05); n=rng.standard_normal(len(t))
    return filt(n,'high',7500)*np.exp(-t*(14 if open_ else 90))*0.5
def crash(d=2.2):
    t=t_(d); n=rng.standard_normal(len(t))
    return filt(n,'high',3500)*np.exp(-t*2.2)*0.6
def sweep_noise(d,f0,f1,shape=1.0):
    n=rng.standard_normal(int(d*SR)); f,tt,Z=stft(n,SR,nperseg=2048)
    u=np.clip(tt/d,0,1)**shape; fc=f0*(f1/f0)**u
    g=np.exp(-0.5*(np.log(f[:,None]+1)-np.log(fc[None,:]))**2/0.35**2)
    _,y=istft(Z*g,SR,nperseg=2048); y=y[:int(d*SR)]; return y/np.max(np.abs(y))
def riser(d):
    t=t_(d); u=t/d; s=sweep_noise(d,300,9000,1.6)*u**2*0.5
    f=180*(8**u**1.4); s+=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*0.08*u**2
    return s
def boom(d=2.8):
    t=t_(d); f=58*np.exp(-t*0.9)+24; s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.4)
    s+=filt(rng.standard_normal(len(t)),'low',300)*np.exp(-t*7)*0.6
    return np.tanh(s*2.0)
def whoosh(d=0.7):
    t=t_(d); env=np.sin(np.pi*np.clip(t/d,0,1))**2
    return sweep_noise(d,250,7000,1.0)*env
def pluck(f,d=1.0,bright=0.6):
    n=int(d*SR); p=int(SR/f); buf=rng.uniform(-1,1,p)*1.0; out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=0.996*(bright*buf[i%p]+(1-bright)*buf[(i+1)%p]) if True else 0
    return out*np.exp(-np.arange(n)/SR*2.2)
def pad(freqs,d):
    t=t_(d); s=np.zeros(len(t))
    for f in freqs:
        for det in (-0.12,0,0.11):
            ph=2*np.pi*f*2**(det/12)*t+rng.uniform(0,6.28); s+=2*(ph/(2*np.pi)%1)-1
    s=filt(s,'low',1400,4)/(len(freqs)*3)
    env=np.minimum(1,t/0.8)*np.minimum(1,(d-t)/1.2); return s*np.clip(env,0,1)
def reverb(x,rt=1.4,mix=0.25):
    t=t_(rt); ir=rng.standard_normal((2,len(t)))*np.exp(-t*6.9/rt); ir[:,:int(0.01*SR)]*=np.linspace(0,1,int(0.01*SR))
    wet=np.vstack([fftconvolve(x[0],ir[0])[:x.shape[1]],fftconvolve(x[1],ir[1])[:x.shape[1]]])
    wet*=np.max(np.abs(x))/(np.max(np.abs(wet))+1e-9); return x*(1-mix)+wet*mix
# ---------- arrangement (beat k at k*B s) ----------
D1,Eb1,F1s,G1,A1,Bb1,C2=[note(n) for n in (26,27,30,31,33,34,36)]   # D hijaz, 808 register
HIJ=[note(n) for n in (62,63,66,67,69,70,72,74)]                     # D4 Eb4 F#4 G4 A4 Bb4 C5 D5
drums=np.zeros_like(L); bass=np.zeros_like(L); mel=np.zeros_like(L); fx=np.zeros_like(L)
at=lambda k: k*B
# intro (beats 0-2): hijaz plucks, filtered pad, reverse cymbal + riser into the drop
for k,(n,v) in enumerate([(0,.9),(1,.6),(2,.7),(4,.8),(3,.6),(2,.7),(1,.6),(0,.9)]):
    add(pluck(HIJ[n],0.9),at(k*0.25),0.33*v,pan=-0.3+0.1*k,bus=mel)
add(pad([note(50),note(54),note(57)],DUR),0,0.16,bus=mel)
add(crash(1.0)[::-1],at(2)-1.0,0.5,bus=fx); add(riser(1.0),at(2)-1.0,0.45,bus=fx)
# main section (beats 2-8): one kick + one 808 on every cut
riff=[D1,D1,F1s,D1,G1,F1s,Eb1]
for i,k in enumerate(range(2,9)):
    if k<8:
        add(kick(),at(k),1.0,bus=drums); add(bass808(riff[i],B*0.95,glide=0.3 if i==0 else 0.0),at(k),0.95,bus=bass)
    if k in (3,5,7): add(clap(),at(k),0.55,bus=drums)
    for h in range(2): add(hat(),at(k+h*0.5),0.35 if h else 0.22,pan=0.25,bus=drums)
add(crash(),at(2),0.55,bus=fx)
for r in range(4): add(hat(),at(7.5+r*0.125),0.25,pan=0.25,bus=drums)     # hat roll into the shuffle
for k,n in [(2,0),(3,2),(4,3),(5,4),(6,3),(7,2)]: add(pluck(HIJ[n],0.6),at(k)+B*0.5,0.18,pan=0.35,bus=mel)
# shuffle (beats 8-12): an 808 stab + kick on EVERY 8th note = every shuffle cut, snare roll building
stabs=[D1,D1*2,F1s,D1,A1,G1,F1s,Eb1]
for i in range(8):
    tt=at(8)+i*B/2
    add(kick(0.3,0.8),tt,0.85,bus=drums); add(bass808(stabs[i],B/2*0.9,glide=0.15),tt,0.9,bus=bass)
    add(hat(),tt+B/4,0.25,pan=0.2,bus=drums)
for r in range(16): add(clap(),at(8)+r*B/4,0.08+0.32*(r/15)**2,bus=drums)
add(riser(2.4),at(8),0.5,bus=fx); add(crash(1.2)[::-1],at(12)-1.2,0.45,bus=fx)
# finale (beat 12): impact as DUBAI rises, half-time groove, hijaz melody
add(boom(3.0),at(12),1.0,bus=bass); add(crash(2.6),at(12),0.6,bus=fx); add(kick(0.7,1.2),at(12),1.0,bus=drums)
add(bass808(D1,B*2.0,glide=0.5,decay=0.9),at(12),0.85,bus=bass)
for k in (14,): add(kick(),at(k),0.9,bus=drums); 
add(bass808(F1s,B*1.0,decay=0.5),at(14),0.75,bus=bass); add(bass808(G1,B*1.0,decay=0.5),at(15),0.75,bus=bass)
add(bass808(Eb1,B*1.0,glide=0.2,decay=0.5),at(16),0.75,bus=bass)
for k in (13,15): add(clap(),at(k),0.55,bus=drums)
for k in np.arange(12.5,16.5,0.5): add(hat(open_=(k%1==0.5 and k>14)),at(k),0.22,pan=0.25,bus=drums)
for j,(n,b) in enumerate([(4,12.5),(5,13),(4,13.5),(2,14),(3,14.5),(1,15),(2,15.5),(0,16)]):
    add(pluck(HIJ[n],1.1),at(b),0.3,pan=-0.2,bus=mel)
add(whoosh(0.75),at(17)-0.6,0.6,bus=fx); add(riser(1.2),at(17)-1.2,0.35,bus=fx)
# drone (beat 17): impact, sustained 808, wide pad, last hijaz phrase, ring-out with the fade
add(boom(3.5),at(17),0.9,bus=bass); add(crash(3.0),at(17),0.5,bus=fx); add(kick(0.7,1.2),at(17),0.9,bus=drums)
add(bass808(D1,B*4,glide=0.4,decay=1.6),at(17),0.8,bus=bass)
add(pad([note(62),note(66),note(69),note(74)],DUR-at(17)),at(17),0.14,bus=mel)
for k in (19,21,23): add(kick(0.5,0.9),at(k),0.6,bus=drums); 
add(bass808(A1,B*2,decay=0.9),at(21),0.6,bus=bass)
for j,(n,b) in enumerate([(7,18),(6,18.5),(5,19),(4,19.5),(3,20.5),(2,21),(1,21.5),(0,22.5)]):
    add(pluck(HIJ[n],1.4),at(b),0.3,pan=0.2*(-1)**j,bus=mel)
# ---------- mix ----------
mel=reverb(mel,1.8,0.35); drums=reverb(drums,0.9,0.12); fx=reverb(fx,1.5,0.2)
kick_env=np.zeros(N)
for k in list(range(2,8))+[12,14,17,19,21,23]: i=int(at(k)*SR); kick_env[i:i+int(0.25*SR)]=np.maximum(kick_env[i:i+int(0.25*SR)],np.exp(-np.arange(min(int(0.25*SR),N-i))/SR*12))
duck=1-0.45*kick_env
mix=drums*0.9+bass*1.0+mel*duck*0.9+fx*0.75
mix[:, :]=filt(mix,'high',28,2)
fade_start=int(14.2*SR); g=np.ones(N); g[fade_start:]=np.linspace(1,0,N-fade_start)**1.3; mix*=g
mix=np.tanh(mix*1.25)/np.tanh(1.25); mix*=0.79/np.max(np.abs(mix))
sf.write('track.wav',mix.T[:int(DUR*SR)],SR,subtype='PCM_24')
cues={'drop':at(2),'step_cuts':[at(k) for k in range(2,9)],'shuffle_cuts':[at(8)+i*B/2 for i in range(9)],'finale_impact':at(12),'drone_impact':at(17),'end':DUR}
import json; json.dump(cues,open('cues.json','w'),indent=1); print(cues)
