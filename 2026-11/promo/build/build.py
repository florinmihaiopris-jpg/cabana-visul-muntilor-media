import subprocess,os
X="/tmp/claude-0/-home-user-cabana-visul-muntilor-media/c8c2a9a3-2610-58b7-b9b3-0a5b8adc5a3a/scratchpad/wt/x/"
R="/home/user/cabana-visul-muntilor-media/"
V={'stars_up':X+"19784309-uhd_2160_3836_24fps.mp4",'circles':X+"17111784_2794_1440_30fps.mp4",'moon':X+"3878212-uhd_3840_2160_30fps.mp4",
   'morning':X+"WhatsApp Video 2026-11-15 at 21.02.11.mp4",'terrace':X+"WhatsApp Video 2026-11-15 at 21.02.15.mp4",'falls':X+"WhatsApp Video 2026-11-15 at 21.02.17.mp4",
   'plasa':R+"2026-11/poze-reale/plasa/plasa_c.mp4"}
I={'p1':X+"WhatsApp Image 2026-11-15 at 21.02.16.jpeg",'p2':X+"WhatsApp Image 2026-11-15 at 21.02.17.jpeg",'p3':X+"WhatsApp Image 2026-11-15 at 21.02.18 (1).jpeg",
   'p6':X+"WhatsApp Image 2026-11-15 at 21.02.18 (4).jpeg",'iulia1':R+"2026-11/poze-reale/iulia/iulia_1.jpg",'brazi':R+"2026-11/poze-reale/toamna/cabana-intre-brazi.jpg"}
ENC=["-an","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-r","30"]
def run(a): subprocess.run(["ffmpeg","-v","error","-y"]+a,check=True)
def ov(chain,ovs):
    # chain ends with [b]
    s=chain; last="b"
    for k,o in enumerate(ovs): s+=f";[{last}][{k+1}:v]overlay=0:0[o{k}]"; last=f"o{k}"
    return s,last
def fade(d): return f"fade=t=in:st=0:d=0.35,fade=t=out:st={d-0.35}:d=0.35"
def vid(out,src,ss,d,speed=1.0,crop="center",ovs=[],extra=""):
    srcd=d*speed
    if crop=="center": cf="scale=-2:1920,crop=1080:1920"
    elif crop=="fit": cf="scale=1080:1920"
    else: cf=crop
    chain=f"[0:v]trim=0:{srcd},setpts=PTS/{speed},{cf},fps=30,setsar=1{extra},{fade(d)}[b]"
    s,last=ov(chain,ovs)
    a=["-ss",str(ss),"-i",src]; 
    for o in ovs: a+=["-i",o]
    run(a+["-filter_complex",s,"-map",f"[{last}]","-t",str(d)]+ENC+[out])
def img(out,src,d,ovs=[],zoom=0.08,fx=0.5,fy=0.5,extra=""):
    n=int(d*30)
    chain=f"[0:v]scale=-2:3840,crop=2160:3840:(iw-2160)*{fx}:(ih-3840)*{fy},zoompan=z='1+{zoom}*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,setsar=1{extra},{fade(d)}[b]"
    s,last=ov(chain,ovs)
    a=["-loop","1","-t",str(d),"-i",src]
    for o in ovs: a+=["-i",o]
    run(a+["-filter_complex",s,"-map",f"[{last}]","-frames:v",str(n)]+ENC+[out])
segs=[]
def add(fn,*a,**k):
    o=f"seg/{len(segs):02d}.mp4"; fn(o,*a,**k); segs.append(o)
add(vid,V['plasa'],3.0,4.0,crop="fit",ovs=["t1.png"])
add(vid,V['plasa'],0.0,3.0,crop="fit",ovs=["t2.png"])
add(vid,V['stars_up'],0,5.0,crop="scale=1080:1920",ovs=["c_noapte.png"])
add(vid,V['moon'],0,5.0,speed=0.8,crop="scale=1300:-2,crop=1080:ih,pad=1080:1920:0:(oh-ih)/2:black")
add(vid,V['circles'],2,5.0,speed=3.0)
add(vid,V['morning'],1.5,5.0,crop="fit")
add(img,I['iulia1'],3.0,ovs=["t3.png"],fy=0.3)
add(vid,V['terrace'],3,4.0,crop="fit")
add(vid,V['falls'],0,4.7,crop="fit",ovs=["c_cascada.png","t4.png"])
add(img,I['p2'],3.0,ovs=["c_pietre.png","t5.png"])
add(img,I['p3'],3.0,ovs=["c_pietre.png"])
add(img,I['p6'],2.2,ovs=["t6.png"])
add(img,I['p1'],2.2,extra=',eq=brightness=0.06:gamma=1.15')
add(img,I['brazi'],4.5,ovs=["c_end.png"],zoom=0.05,fy=0.35,extra=",eq=brightness=-0.12")
open("list.txt","w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
print(len(segs))
