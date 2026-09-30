import glob, struct, zlib, subprocess, json, os
# Use ffmpeg to dump 1fps grayscale raw and diff frames to find big cuts.
D='/opt/data/projects/dailyqapp/promo/control-room-reel'
W,H=64,40
raw=subprocess.run(['ffmpeg','-v','error','-i',f'{D}/raw4/page@3c694bcce292d420c8653abbbd74cf9a.webm',
                    '-vf',f'fps=1,scale={W}:{H}','-pix_fmt','gray','-f','rawvideo','-'],
                   capture_output=True).stdout
n=len(raw)//(W*H)
prev=None
cuts=[]
for i in range(n):
    f=raw[i*W*H:(i+1)*W*H]
    if prev is not None:
        d=sum(abs(a-b) for a,b in zip(f,prev))/(W*H)
        if d>12: cuts.append((i,round(d,1)))
    prev=f
print('frames',n)
print('cuts',cuts)
