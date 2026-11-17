"""Promo v6: reel profesionist din poze reale animate cu mișcare de cameră (Kling 3.0 Pro pe RunComfy)
+ un cadru AI de deschidere (prieteni pe plasă, văzuți de jos). Rețeta editorului:
- fiecare cadru are mișcare de cameră continuă, tăieturi simple pe beat, un singur whip (interior -> exterior);
- o singură colorizare pentru tot clipul;
- max. 5 mesaje, text curat aliniat la stânga, cu umbră moale, animat (fade + slide, ease-out), care trece peste tăieturi.

Rulare (din rădăcina repo-ului):
    python3 2026-11/promo/build/build_v6.py <dir_clipuri> <dir_lucru> <muzică> [A|B]
"""
import math, os, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
P = os.path.join(R, "2026-11", "promo")
CL, W, MUSIC = (os.path.abspath(a) for a in sys.argv[1:4])
V = sys.argv[4] if len(sys.argv) > 4 else "A"
OUT = os.path.join(P, f"promo_v6_{V}.mp4")
os.makedirs(os.path.join(W, "seg"), exist_ok=True)
FPS = 30
GRADE = ("eq=contrast=1.04:saturation=0.92,colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.04,"
         "curves=all='0/0.02 0.5/0.5 1/0.96',noise=alls=3:allf=t")
ENC = ["-an", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def run(a):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + a, check=True)


# --- grila de beat a piesei: tempo din autocorelație, faza din energia atacurilor ---
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", MUSIC, "-t", "24", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32); env = np.abs(x[: len(x) // 80 * 80]).reshape(-1, 80).mean(1)  # 100 Hz
on = np.diff(env).clip(0); on -= on.mean()
ac = np.correlate(on, on, "full")[len(on) - 1:]; lag = np.arange(len(ac)); m = (lag >= 40) & (lag <= 80)
period = lag[m][np.argmax(ac[m])] / 100.0                      # secunde pe bătaie
phase = max(range(int(period * 100)), key=lambda p: on[p::int(round(period * 100))].sum()) / 100.0
B = period
print(f"tempo ~{60 / B:.1f} BPM, prima bătaie la {phase:.2f} s")

# (clip, bătăi, secunda de start în clipul sursă)
SHOTS = [("hook_plasa", 3, 0.4), ("plasa_real", 2, 0.0), ("living", 2, 0.5), ("test_dormitor", 2, 0.5),
         ("dormitor_matr", 2, 0.5), ("terasa", 2, 0.5), ("foisor", 2, 0.5), ("cabana_iarba", 2, 0.5),
         ("pietrele", 2, 0.5), ("drona", 3, 0.5), ("test_cabana_brazi", 2, 0.8), ("cabana_fata", 5, 0.5)]
WHIP_AT = 5          # indexul cadrului care intră cu whip (primul cadru exterior)
XF = 0.2

segs = []
for i, (name, beats, ss) in enumerate(SHOTS):
    d = beats * B + (XF if i == WHIP_AT - 1 else 0)
    src = os.path.join(R, "2026-11/poze-reale/plasa/plasa_c.mp4") if name == "plasa_real" else os.path.join(CL, f"{name}.mp4")
    out = os.path.join(W, "seg", f"{i:02d}.mp4")
    run(["-ss", str(ss), "-i", src, "-vf",
         f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps={FPS},{GRADE},setsar=1",
         "-t", f"{d:.3f}"] + ENC + [out])
    segs.append(out)

def concat(lst, out):
    f = os.path.join(W, os.path.basename(out) + ".txt")
    open(f, "w").write("".join(f"file '{s}'\n" for s in lst))
    run(["-f", "concat", "-safe", "0", "-i", f, "-c", "copy", out])

a, b = os.path.join(W, "partA.mp4"), os.path.join(W, "partB.mp4")
concat(segs[:WHIP_AT], a); concat(segs[WHIP_AT:], b)
dur_a = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a],
                             capture_output=True, text=True).stdout)
body = os.path.join(W, "body.mp4")
run(["-i", a, "-i", b, "-filter_complex", f"[0][1]xfade=transition=hblur:duration={XF}:offset={dur_a - XF:.3f},format=yuv420p",
     ] + ENC + [body])
T = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", body],
                         capture_output=True, text=True).stdout)

# --- text animat, randat cadru cu cadru ---
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
WH, AC = (255, 255, 255), (242, 196, 109)
t_cut = lambda k: sum(s[1] for s in SHOTS[:k]) * B          # începutul cadrului k
if V == "B":
    m1 = [("LIBER 11–13 DECEMBRIE", 84, AC, FB), ("cabană întreagă · 14 persoane", 46, WH, FS)]
elif V == "C":
    m1 = [("Revelionul e dat.", 84, WH, FB), ("11–13 dec e LIBER.", 84, AC, FB)]
elif V == "D":
    m1 = [("≈ 320 lei de persoană", 80, AC, FB), ("weekend cu saună + ciubăr", 50, WH, FS)]
else:
    m1 = [("Ai dormi deasupra", 84, WH, FB), ("livingului?", 84, AC, FB)]
MSGS = [(0.15, t_cut(2) - 0.15, m1),
        (t_cut(2) + 0.15, t_cut(5) - 0.15, [("Toată cabana e a voastră", 72, WH, FB), ("până la 14 persoane · 5 dormitoare", 46, WH, FS)]),
        (t_cut(5) + 0.15, t_cut(9) - 0.15, [("Saună + ciubăr incluse", 72, WH, FB), ("Beliș, Apuseni · 1h30 de Cluj", 46, WH, FS)]),
        (t_cut(9) + 0.15, t_cut(11) - 0.15, [("4.500 lei", 104, AC, FB), ("weekend vineri–duminică", 46, WH, FS)]),
        (t_cut(11) + 0.15, T - 0.1, [("Libere 11–13 și 18–20 dec", 64, AC, FB), ("Scrie-ne pe WhatsApp", 56, WH, FB),
                                     ("0733 117 686", 56, WH, FB)])]
fonts = {}
def font(p, s):
    return fonts.setdefault((p, s), ImageFont.truetype(p, s))

def layer(lines, alphas, dys):
    """Randează rândurile aliniate la stânga, de jos în sus până la y=1400, cu umbră moale."""
    txt = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); sh = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(sh)
    hs = [font(f, s).getbbox(t)[3] for t, s, c, f in lines]
    y = 1400 - sum(hs) - 18 * (len(lines) - 1)
    for (t, s, c, f), h, al, dy in zip(lines, hs, alphas, dys):
        if al > 0:
            dt.text((96, y + dy), t, font=font(f, s), fill=c + (int(255 * al),))
            ds.text((96, y + dy + 4), t, font=font(f, s), fill=(0, 0, 0, int(110 * al)))
        y += h + 18
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), txt)

tdir = os.path.join(W, "txt"); shutil.rmtree(tdir, ignore_errors=True); os.makedirs(tdir)
ease = lambda u: 1 - (1 - min(max(u, 0), 1)) ** 3
blank = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
for n in range(int(math.ceil(T * FPS))):
    t = n / FPS; img = blank
    for t0, t1, lines in MSGS:
        if t0 <= t <= t1:
            al, dys = [], []
            for k in range(len(lines)):
                u = ease((t - t0) * FPS / 10 - k * 0.4)
                out_a = min(1, (t1 - t) * FPS / 6)
                al.append(u * out_a); dys.append(int(36 * (1 - u)))
            img = layer(lines, al, dys)
    img.save(os.path.join(tdir, f"{n:04d}.png"), compress_level=1)

# gradient discret jos, ca textul alb să se citească și pe cer deschis
g = np.zeros((1920, 1080, 4), np.uint8); yy = np.arange(1920)[:, None]
g[..., 3] = (np.clip((yy - 950) / 970, 0, 1) ** 1.6 * 170).astype(np.uint8).repeat(1080, 1)
grad = os.path.join(W, "grad.png"); Image.fromarray(g, "RGBA").save(grad)
vid = os.path.join(W, "video.mp4")
run(["-i", body, "-loop", "1", "-i", grad, "-framerate", str(FPS), "-i", os.path.join(tdir, "%04d.png"), "-filter_complex",
     "[0][1]overlay=0:0:format=auto:shortest=1[g];[g][2]overlay=0:0:format=auto,format=yuv420p"] + ENC + [vid])

# --- muzica aliniată pe prima bătaie ---
run(["-i", vid, "-ss", f"{phase:.3f}", "-i", MUSIC, "-filter_complex",
     f"[1:a]atrim=0:{T:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=44100,"
     f"afade=t=out:st={T - 1.5:.3f}:d=1.5[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
     "-b:a", "256k", "-movflags", "+faststart", "-shortest", OUT])
print(OUT, f"{T:.2f}s")
