"""Promo v4: avatarul cu ochi verzi (V1–V6), fără cer înstelat (doar luna, apoi dimineața), cu aceeași
colorizare pe tot clipul.

Rulare (din rădăcina repo-ului):
    python3 2026-11/promo/build/build_v4.py <dir_de_lucru> [fișier_muzică] [nume_ieșire]
Segmentele fără gazdă se taie din promo_draft_v1.mp4 (clipurile stock nu sunt în repo).
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = os.path.join(R, "2026-11", "promo")
W = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(W, "seg"), exist_ok=True)
MUSIC = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(P, "muzica", "A_indie_folk.mp3")
OUT = os.path.join(P, sys.argv[3] if len(sys.argv) > 3 else "promo_v4.mp4")
DRAFT = os.path.join(P, "promo_draft_v1.mp4")
N = lambda n: os.path.join(P, "gazda", "v4", n)
ENC = ["-an", "-c:v", "libx264", "-crf", "24", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30"]
FS, FB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
WH, YE = (255, 255, 255), (247, 215, 140)

# Aceeași colorizare pe toate cadrele: saturație puțin redusă, umbre spre albastru-verzui,
# lumini calde, negru ușor ridicat, vignetă discretă și granulație de film.
GRADE = ("eq=saturation=0.86:contrast=1.05,"
         "colorbalance=rs=-0.04:gs=0.00:bs=0.05:rm=0.02:bm=-0.02:rh=0.06:gh=0.02:bh=-0.07,"
         "curves=all='0/0.035 0.25/0.24 0.75/0.77 1/0.965',"
         "vignette=angle=PI/6.5,noise=alls=5:allf=t")


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
    return f"fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.3}:d=0.3"


segs = []; total = 0.0


def clip(src, ss, d, speed=1.0, ov=None, fades=True):
    """Un segment de d secunde din src, de la ss; colorizat, apoi (opțional) cu text deasupra."""
    global total
    out = os.path.join(W, "seg", f"{len(segs):02d}.mp4")
    chain = (f"[0:v]trim=0:{d * speed},setpts=PTS/{speed},scale=1080:1920:flags=lanczos,fps=30,setsar=1,"
             f"{GRADE}{',' + fade(d) if fades else ''}[b]")
    a = ["-ss", str(ss), "-i", src]; last = "b"
    if ov:
        a += ["-i", ov]; chain += ";[b][1:v]overlay=0:0[o]"; last = "o"
    run(a + ["-filter_complex", chain, "-map", f"[{last}]", "-t", str(d)] + ENC + [out])
    segs.append(out); total += d


def keep(ss, d):
    """Segment din schița v1 (are deja fade-urile și textele), trecut prin aceeași colorizare."""
    clip(DRAFT, ss, d, fades=False)


c_cascada = caption("c_cascada.png", [("Cascada Vălul Miresei", 58, WH), ("în apropiere", 40, YE)], 1480)
c_pietre = caption("c_pietre.png", [("Pietrele Albe", 64, WH), ("în apropiere", 40, YE)], 1480)

clip(N("V1_semineu.mp4"), 0.3, 4.0)                       # gazda la șemineu (replica)
clip(N("V2_plasa_seara.mp4"), 0.8, 3.0)                   # sare și se întinde pe plasă
clip(DRAFT, 12.4, 3.0)                                    # luna răsare
keep(22.0, 5.0)                                           # dimineața, soarele peste curte
clip(N("V3_plasa_dimineata.mp4"), 3.5, 3.0)               # se trezește veselă pe plasă
keep(30.0, 4.0)                                           # terasa
clip(os.path.join(P, "materiale", "cascada_valul_miresei.mp4"), 0.0, 2.2, ov=c_cascada)   # cascada reală
clip(N("V4_cascada.mp4"), 0.3, 2.5, ov=c_cascada)         # gazda la cascadă
clip(N("V5_pietrele_albe.mp4"), 0.8, 3.0, ov=c_pietre)    # gazda la Pietrele Albe
keep(41.7, 3.0)                                           # Pietrele Albe (poză reală)
clip(N("V6_cabana.mp4"), 0.3, 2.2)                        # se întoarce la cabană
keep(46.9, 6.7)                                           # cafea + final

lst = os.path.join(W, "list.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
silent = os.path.join(W, "video.mp4")
run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])

# Sunet: muzica e coborâtă sub replica gazdei (N1 0.3–3.7 s -> 0–3.4 s în montaj).
T = round(total, 2)
af = (f"[1:a]atrim=0:{T},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100,afade=t=out:st={T - 2.2}:d=2.2,"
      "volume='0.85*if(lt(t,3.8),0.32,if(lt(t,4.4),0.32+0.68*(t-3.8)/0.6,1))':eval=frame[m];"
      "[2:a]atrim=0.3:4.3,asetpts=PTS-STARTPTS,highpass=f=90,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=44100,"
      "afade=t=in:d=0.05,afade=t=out:st=3.7:d=0.3[v];[m][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]")
run(["-i", silent, "-i", MUSIC, "-i", N("V1_semineu.mp4"), "-filter_complex", af, "-map", "0:v", "-map", "[a]",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT])
print(OUT, T)
