"""Promo v5: reel de ~17 s doar din material real, pe recomandările specialiștilor
(editor, TikTok, Meta, growth, copywriter). Plasa în prima secundă, preț și date libere pe ecran,
CTA WhatsApp. Fără AI, fără zăpadă, fără piscină.

Rulare (din rădăcina repo-ului):
    python3 2026-11/promo/build/build_v5.py <dir_de_lucru> <muzică> [A|B]
A = hook „Ai dormi DEASUPRA livingului?” (organic TikTok/Reels)
B = hook „LIBER 11–13 DECEMBRIE” (reclamă Meta click-to-WhatsApp)
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = os.path.join(R, "2026-11", "promo")
W = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(W, "seg"), exist_ok=True)
MUSIC = os.path.abspath(sys.argv[2])
V = sys.argv[3] if len(sys.argv) > 3 else "A"
OUT = os.path.join(P, f"promo_v5_{V}.mp4")

PLASA = os.path.join(R, "2026-11/poze-reale/plasa/plasa_c.mp4")
DIM = os.path.join(P, "materiale/dimineata_cabana.mp4")
CASC = os.path.join(P, "materiale/cascada_valul_miresei.mp4")
FOTO = lambda p: os.path.join(R, p)

FB = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
WH, YE = (255, 255, 255, 255), (255, 214, 64, 255)
ENC = ["-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30"]
GRADE = ("eq=contrast=1.05:saturation=1.10:brightness=0.01,"
         "colorbalance=rm=0.04:bm=-0.03:rh=0.03:bh=-0.03,"
         "curves=all='0/0.03 0.5/0.5 1/0.97',vignette=PI/5")
LOWRES = "hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.7:5:5:0,noise=alls=5:allf=t"


def run(a):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + a, check=True)


def card(name, lines, y0=None):
    """Text mare pe fundal semitransparent, în zona sigură (y 380–1400)."""
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rows = []
    for t, size, col in lines:
        f = ImageFont.truetype(FB if size >= 70 else FX, size)
        bb = d.textbbox((0, 0), t, font=f, stroke_width=4)
        rows.append((t, f, col, bb[2] - bb[0], bb[3] - bb[1], size))
    total = sum(h for *_, h, _ in rows) + 22 * (len(rows) - 1)
    y = y0 if y0 is not None else 620 - total // 2
    wmax = max(w for *_, w, _, _ in rows)
    d.rounded_rectangle((540 - wmax / 2 - 36, y - 26, 540 + wmax / 2 + 36, y + total + 34), radius=28, fill=(0, 0, 0, 120))
    for t, f, col, w, h, size in rows:
        d.text(((1080 - w) / 2, y), t, font=f, fill=col, stroke_width=4, stroke_fill=(0, 0, 0, 255)); y += h + 22
    p = os.path.join(W, name); im.save(p); return p


segs = []


def vid(src, ss, d, speed=1.0, pre="", lowres=False, ov=None, crop=None):
    out = os.path.join(W, "seg", f"{len(segs):02d}.mp4")
    cf = crop or "scale=1080:1920:flags=lanczos"
    ch = (f"[0:v]trim=0:{d * speed},setpts=PTS/{speed},fps=30,{pre + ',' if pre else ''}{cf},"
          f"{LOWRES + ',' if lowres else ''}{GRADE},setsar=1[b]")
    a = ["-ss", str(ss), "-i", src]; last = "b"
    if ov:
        a += ["-i", ov]; ch += ";[b][1:v]overlay=0:0[o]"; last = "o"
    run(a + ["-filter_complex", ch, "-map", f"[{last}]", "-t", str(d)] + ENC + [out]); segs.append(out)


def foto(path, d, ov=None, fx=0.5, fy=0.5, z0=1.12, z1=1.0):
    """Poză cu zoom scurt pe beat (punch-in), nu Ken Burns lent."""
    out = os.path.join(W, "seg", f"{len(segs):02d}.mp4"); n = int(round(d * 30))
    ch = (f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,"
          f"crop=2160:3840:(iw-2160)*{fx}:(ih-3840)*{fy},"
          f"zoompan=z='max({z1},{z0}-({z0}-{z1})*on/6)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,"
          f"{GRADE},setsar=1[b]")
    a = ["-loop", "1", "-t", str(d), "-i", FOTO(path)]; last = "b"
    if ov:
        a += ["-i", ov]; ch += ";[b][1:v]overlay=0:0[o]"; last = "o"
    run(a + ["-filter_complex", ch, "-map", f"[{last}]", "-frames:v", str(n)] + ENC + [out]); segs.append(out)


# --- texte ---
if V == "B":
    t1 = card("t1.png", [("LIBER", 120, YE), ("11–13 DECEMBRIE", 88, YE), ("cabană întreagă · 14 persoane", 54, WH)])
else:
    t1 = card("t1.png", [("Ai dormi", 96, WH), ("DEASUPRA", 112, YE), ("livingului?", 96, WH)])
t2 = card("t2.png", [("Plasă de catamaran", 66, WH), ("peste șemineu", 66, YE)])
t3 = card("t3.png", [("Toată cabana,", 66, WH), ("doar a voastră", 66, YE), ("până la 14 persoane", 50, WH)])
t4 = card("t4.png", [("5 dormitoare · 3 băi", 62, WH)])
t5 = card("t5.png", [("Saună + ciubăr", 66, WH), ("o zi inclusă", 56, YE)])
t6 = card("t6.png", [("Beliș, Apuseni", 66, WH), ("1h30 de Cluj", 56, YE)])
t7 = card("t7.png", [("Foișor cu grătar", 62, WH), ("terasă 60 m²", 56, YE)])
t8 = card("t8.png", [("Cascada Vălul Miresei", 58, WH), ("aproape", 50, YE)])
t9 = card("t9.png", [("Pietrele Albe", 66, WH), ("aproape", 50, YE)])
t10 = card("t10.png", [("4.500 lei", 104, YE), ("weekend vineri–duminică", 52, WH), ("≈ 320 lei de persoană", 58, WH)])
t11 = card("t11.png", [("Libere:", 56, WH), ("11–13 dec · 18–20 dec", 70, YE), ("Scrie-ne pe WhatsApp", 62, WH), ("0733 117 686", 70, YE)])

# --- montaj (120 BPM: o bătaie = 0,5 s) ---
PL = "eq=gamma=1.18:saturation=0.95"
vid(PLASA, 0.0, 1.5, pre=PL, ov=t1)                                    # 0,0  plasa de jos, candelabru
vid(PLASA, 2.0, 2.0, speed=1.5, pre=PL, ov=t2)                         # 1,5  coborâre spre șemineu
foto("listari/poze/04-bucatarie-sufragerie.jpg", 1.0, ov=t3, fx=0.35)  # 3,5  masa mare
foto("listari/poze/06-dormitor-mansarda.jpg", 1.0, ov=t4, fx=0.4)     # 4,5  dormitor
vid(PLASA, 5.0, 1.0, pre=PL, ov=t5,
    crop="crop=iw/1.2:ih/1.2,scale=1080:1920:flags=lanczos")           # 5,5  focul, aproape
vid(os.path.join(P, "materiale/terasa_soare.mp4"), 4.0, 1.5, pre="colortemperature=temperature=5800", lowres=True, ov=t6)  # 6,5 soare și brumă
foto("2026-11/poze-reale/toamna/foisor-gratar.jpg", 1.0, ov=t7, fx=0.45)  # 8,0
vid(CASC, 0.0, 1.5, lowres=True, ov=t8)                                # 9,0  cascada
foto("2026-11/promo/materiale/pietrele_albe_1.jpg", 1.0, ov=t9)        # 10,5
foto("2026-11/poze-reale/toamna/cabana-intre-brazi.jpg", 2.5, ov=t10, z0=1.08)  # 11,5 cabana + preț
vid(PLASA, 5.0, 3.0, speed=0.5, pre=PL + ",boxblur=10:2,eq=brightness=-0.15", ov=t11)  # 14,0 CTA pe focul blurat

lst = os.path.join(W, "list.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
silent = os.path.join(W, "video.mp4")
run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent])
T = 17.0
run(["-i", silent, "-i", MUSIC, "-filter_complex",
     f"[1:a]atrim=0:{T},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=44100,"
     f"afade=t=in:d=0.05,afade=t=out:st={T - 1.2}:d=1.2[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
     "-movflags", "+faststart", "-shortest", OUT])
print(OUT)
