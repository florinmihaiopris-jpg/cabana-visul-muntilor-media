"""Story-uri 9:16 (5 s) din clipurile v6, cu text animat și muzică în fișier (story-urile publicate prin API
nu pot primi muzică din aplicație). Rulare: python3 stories_v6.py <dir_clipuri> <dir_ieșire> <muzică>"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CL, OUT, MUSIC = (os.path.abspath(a) for a in sys.argv[1:4]); os.makedirs(OUT, exist_ok=True)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
WH, AC = (255, 255, 255), (242, 196, 109)
GRADE = ("eq=contrast=1.04:saturation=0.92,colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.04,"
         "curves=all='0/0.02 0.5/0.5 1/0.96',noise=alls=3:allf=t")
STORIES = {
    "S1_plasa": ("hook_plasa", [("Ai dormi deasupra", 84, WH, FB), ("livingului?", 84, AC, FB),
                                ("Cabana Visul Munților · Beliș", 44, WH, FS)]),
    "S2_liber_dec": ("test_cabana_brazi", [("LIBER", 110, AC, FB), ("11–13 și 18–20 dec", 76, WH, FB),
                                           ("Scrie-ne pe WhatsApp", 50, WH, FS), ("0733 117 686", 50, AC, FB)]),
    "S3_pret_persoana": ("living", [("≈ 320 lei", 104, AC, FB), ("de persoană, tot weekendul", 52, WH, FS),
                                    ("14 prieteni · 4.500 lei · saună + ciubăr", 40, WH, FS)]),
    "S4_imprejurimi": ("pietrele", [("Pietrele Albe", 84, WH, FB), ("& Cascada Vălul Miresei", 56, AC, FB),
                                    ("la câțiva km de cabană · 1h30 de Cluj", 40, WH, FS)]),
    "S5_saptamana": ("dormitor_matr", [("În timpul săptămânii", 68, WH, FB), ("1.500 lei / noapte", 84, AC, FB),
                                       ("cabana întreagă · minim 2 nopți", 44, WH, FS)]),
}


def card(lines, path):
    txt = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); sh = txt.copy()
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(sh)
    fonts = [ImageFont.truetype(f, s) for _, s, _, f in lines]
    hs = [f.getbbox(t)[3] for (t, *_), f in zip(lines, fonts)]
    y = 1450 - sum(hs) - 18 * (len(lines) - 1)
    for (t, s, c, _), f, h in zip(lines, fonts, hs):
        dt.text((96, y), t, font=f, fill=c + (255,)); ds.text((96, y + 4), t, font=f, fill=(0, 0, 0, 120)); y += h + 18
    g = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for yy in range(950, 1920):
        gd.line([(0, yy), (1080, yy)], fill=(0, 0, 0, int(((yy - 950) / 970) ** 1.6 * 170)))
    Image.alpha_composite(Image.alpha_composite(g, sh.filter(ImageFilter.GaussianBlur(8))), txt).save(path)


for i, (name, (clip, lines)) in enumerate(STORIES.items()):
    png = os.path.join(OUT, f"{name}.png"); card(lines, png)
    out = os.path.join(OUT, f"{name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.3", "-i", os.path.join(CL, f"{clip}.mp4"),
                    "-loop", "1", "-i", png, "-ss", str(2 + 4 * i), "-i", MUSIC, "-filter_complex",
                    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,{GRADE}[v];"
                    "[1:v]format=rgba,fade=t=in:st=0.2:d=0.4:alpha=1[t];[v][t]overlay=0:0:shortest=1,format=yuv420p[o];"
                    "[2:a]atrim=0:4.7,asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.2,afade=t=out:st=4.1:d=0.6[a]",
                    "-map", "[o]", "-map", "[a]", "-t", "4.7", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print(out)
