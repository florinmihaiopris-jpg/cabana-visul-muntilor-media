"""Promo v2: schița v1 cu cadrele „GAZDA AI” înlocuite de clipurile G1–G6.

Rulare (din rădăcina repo-ului):  python3 2026-11/promo/build/build_v2.py <dir_de_lucru>
Segmentele fără gazdă se taie direct din promo_draft_v1.mp4 (clipurile stock nu sunt în repo).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = os.path.join(R, "2026-11", "promo")
W = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(W, "seg"), exist_ok=True)
DRAFT = os.path.join(P, "promo_draft_v1.mp4")
G = lambda n: os.path.join(P, "gazda", n)
ENC = ["-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30"]
FS, FB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
WH, YE = (255, 255, 255), (247, 215, 140)


def run(a):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + a, check=True)


def caption(name, lines, y):
    path = os.path.join(W, name)
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for t, s, c in lines:
        f = ImageFont.truetype(FS if s < 60 else FB, s); w = d.textlength(t, font=f)
        d.text(((1080 - w) / 2, y), t, font=f, fill=c, stroke_width=3, stroke_fill=(0, 0, 0, 170)); y += int(s * 1.35)
    im.save(path); return path


def fade(d):
    return f"fade=t=in:st=0:d=0.35,fade=t=out:st={d - 0.35}:d=0.35"


segs = []


def clip(src, ss, d, speed=1.0, ov=None, fit="scale=1080:1920:flags=lanczos"):
    """Un segment de d secunde din src, începând la ss; speed>1 accelerează."""
    out = os.path.join(W, "seg", f"{len(segs):02d}.mp4")
    chain = f"[0:v]trim=0:{d * speed},setpts=PTS/{speed},{fit},fps=30,setsar=1,{fade(d)}[b]"
    a = ["-ss", str(ss), "-i", src]; last = "b"
    if ov:
        a += ["-i", ov]; chain += ";[b][1:v]overlay=0:0[o]"; last = "o"
    run(a + ["-filter_complex", chain, "-map", f"[{last}]", "-t", str(d)] + ENC + [out]); segs.append(out)


def keep(ss, d):
    """Segment neschimbat, tăiat din schița v1 (are deja fade-urile și textele)."""
    out = os.path.join(W, "seg", f"{len(segs):02d}.mp4")
    run(["-ss", str(ss), "-i", DRAFT, "-t", str(d)] + ENC + [out]); segs.append(out)


c_cascada = caption("c_cascada.png", [("Cascada Vălul Miresei", 58, WH), ("în apropiere", 40, YE)], 1480)
c_pietre = caption("c_pietre.png", [("Pietrele Albe", 64, WH), ("în apropiere", 40, YE)], 1480)

clip(G("G1_semineu.mp4"), 0.9, 4.0)                       # 0.0  gazda la șemineu (replica)
clip(G("G2_plasa_seara.mp4"), 0.2, 3.0, speed=1.15)       # 4.0  se întinde pe plasă
keep(7.0, 20.0)                                           # 7.0  stele, lună, dimineață (material real/stock)
clip(G("G3_plasa_dimineata.mp4"), 1.3, 3.0)               # 27.0 se trezește pe plasă
keep(30.0, 4.0)                                           # 30.0 terasa
clip(os.path.join(P, "materiale", "cascada_valul_miresei.mp4"), 0.0, 2.2, ov=c_cascada)  # 34.0 cascada reală
clip(G("G4_cascada.mp4"), 0.3, 2.5, ov=c_cascada)         # 36.2 gazda la cascadă
clip(G("G5_pietrele_albe.mp4"), 3.6, 3.0, ov=c_pietre)    # 38.7 gazda la Pietrele Albe
keep(41.7, 3.0)                                           # 41.7 Pietrele Albe (poză reală)
clip(G("G6_cabana.mp4"), 0.3, 2.2, speed=1.3)             # 44.7 se întoarce la cabană
keep(46.9, 6.7)                                           # 46.9 final

lst = os.path.join(W, "list.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
silent = os.path.join(W, "video.mp4")
run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])

# Sunet: muzică originală sintetizată de music_v2.py (nicio melodie existentă), coborâtă sub
# replica gazdei (G1 0.9–3.4 s -> 0–2.5 s în montaj).
music = os.path.join(W, "muzica_v2.wav")
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_v2.py"), music, "53.6"], check=True)
out = os.path.join(P, "promo_v2.mp4")
af = ("[1:a]volume='0.85*if(lt(t,2.6),0.35,if(lt(t,3.4),0.35+0.65*(t-2.6)/0.8,1))':eval=frame[m];"
      "[2:a]atrim=0.9:3.4,asetpts=PTS-STARTPTS,highpass=f=90,dynaudnorm=f=150:g=7,volume=2.2,"
      "afade=t=in:d=0.08,afade=t=out:st=2.2:d=0.3[v];[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]")
run(["-i", silent, "-i", music, "-i", G("G1_semineu.mp4"), "-filter_complex", af, "-map", "0:v", "-map", "[a]",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out])
print(out)
