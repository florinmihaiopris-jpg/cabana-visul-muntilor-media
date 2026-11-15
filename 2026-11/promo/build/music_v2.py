"""Muzică originală pentru promo v2, sintetizată integral în cod (fără mostre, fără melodii existente).

Rulare:  python3 music_v2.py <iesire.wav> [durata_secunde] [masura_de_zi]
Chitară ciupită (Karplus-Strong), pad cald, bas, clopoței și percuție ușoară; Re major, 100 bpm.
Structură după montaj: intro lejer (sub replica gazdei), noapte (rar, aerisit) de la 7 s până la
măsura de zi, apoi zi (plin, cu ritm) și un acord final care se stinge.
"""
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter

SR = 44100
OUT = sys.argv[1]
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 53.6
DAY_BAR = int(sys.argv[3]) if len(sys.argv) > 3 else 11   # măsura la care începe partea de zi
BEAT = 0.6                      # 100 bpm
BAR = 4 * BEAT
N = int(SR * (DUR + 3))
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

NOTE = {"G2": 98.00, "A2": 110.00, "B2": 123.47, "D3": 146.83, "E3": 164.81, "F#3": 185.00, "G3": 196.00,
        "A3": 220.00, "B3": 246.94, "C#4": 277.18, "D4": 293.66, "E4": 329.63, "F#4": 369.99, "A4": 440.00,
        "B4": 493.88, "C#5": 554.37, "D5": 587.33, "E5": 659.26, "F#5": 739.99, "A5": 880.00}
CHORDS = {
    "D": ["D3", "A3", "D4", "F#4", "A4"],
    "A": ["A2", "E3", "A3", "C#4", "E4"],
    "Bm": ["B2", "F#3", "B3", "D4", "F#4"],
    "G": ["G2", "D3", "G3", "B3", "D4"],
}
PROG = ["D", "A", "Bm", "G"]
BARS = int(DUR // BAR)          # 22 măsuri


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** 0.5
    R[i:i + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** 0.5


def pluck(freq, dur=2.2, bright=0.5):
    """Coardă ciupită Karplus-Strong."""
    n = int(SR * dur); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    b, a = butter(1, 0.15 + 0.5 * bright); buf = lfilter(b, a, buf)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.exp(-np.arange(n) / (SR * dur * 0.45))


def bell(freq, dur=1.6):
    t = np.arange(int(SR * dur)) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) + 0.12 * np.sin(2 * np.pi * 3.01 * freq * t)
    return s * np.exp(-t * 3.2) * np.minimum(1, t / 0.004)


def pad(freqs, dur):
    t = np.arange(int(SR * dur)) / SR; s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.25, 0.25):
            s += np.sin(2 * np.pi * (f + det) * t) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * t)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9)
    return s / len(freqs) * env


def bass(freq, dur=1.0):
    t = np.arange(int(SR * dur)) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * 2 * freq * t)) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)


def kick():
    t = np.arange(int(SR * 0.25)) / SR
    return np.sin(2 * np.pi * (45 * t + 60 * (1 - np.exp(-t * 28)) / 28)) * np.exp(-t * 16)


def shaker():
    n = int(SR * 0.07); b, a = butter(2, 0.45, "high")
    return lfilter(b, a, rng.uniform(-1, 1, n)) * np.exp(-np.arange(n) / (SR * 0.018))


cache = {}


def P(name, bright):
    key = (name, bright)
    if key not in cache:
        cache[key] = pluck(NOTE[name], bright=bright)
    return cache[key]


ARP_FULL = [0, 2, 3, 4, 2, 3, 4, 3]          # optimi
ARP_SPARSE = [0, None, 2, None, 3, None, 4, None]
MELODY = {  # (timp în bătăi, notă) pe măsură, în secțiunea de zi
    "D": [(0, "F#5"), (2, "A5"), (3, "F#5")],
    "A": [(0, "E5"), (2, "C#5"), (3, "E5")],
    "Bm": [(0, "D5"), (2, "F#5"), (3, "D5")],
    "G": [(0, "B4"), (1.5, "D5"), (3, "E5")],
}

for bar in range(BARS):
    t0 = bar * BAR
    last = bar >= BARS - 2                      # ultimele două măsuri: acord final pe Re
    ch = "D" if last else PROG[bar % 4]
    tones = CHORDS[ch]
    night = 3 <= bar < DAY_BAR                       # ~7–27 s
    day = bar >= DAY_BAR and not last                # ~27–49 s
    intro = bar < 3

    add(pad([NOTE[x] for x in tones[1:4]], BAR + 0.8), t0, gain=0.13 if night else 0.09)

    if last:
        if bar == BARS - 2:
            for k, x in enumerate(tones + ["D5"]):   # acord desfăcut, lăsat să sune
                add(pluck(NOTE[x], dur=5.5, bright=0.6), t0 + k * 0.045, gain=0.95, pan=-0.3 + 0.12 * k)
            add(bass(NOTE["D3"] / 2, 3.0), t0, gain=0.30)
            add(bell(NOTE["F#5"], 3.0), t0 + 0.3, gain=0.16, pan=0.2)
        continue

    pattern = ARP_SPARSE if night else ARP_FULL
    for k, idx in enumerate(pattern):
        if idx is None:
            continue
        g = (0.60 if intro else 0.66 if night else 0.74) * (1.0 if k % 2 == 0 else 0.8)
        add(P(tones[idx], 0.35 if night else 0.6), t0 + k * BEAT / 2, gain=g, pan=-0.35 if k % 2 == 0 else 0.35)

    if not intro:
        root = NOTE[tones[0]] / (2 if tones[0].endswith("3") else 1)
        add(bass(root), t0, gain=0.26)
        if day:
            add(bass(root, 0.7), t0 + 2 * BEAT, gain=0.20)

    if night and bar % 2 == 1:                  # clopoței rari, „stele”
        add(bell(NOTE[tones[4]] * 2, 2.4), t0 + BEAT, gain=0.10, pan=0.4)
    if day:
        for b_, n_ in MELODY[ch]:
            add(bell(NOTE[n_]), t0 + b_ * BEAT, gain=0.24, pan=0.15)
        for b_ in (0, 2):
            add(kick(), t0 + b_ * BEAT, gain=0.34)
        for k in range(8):
            add(shaker(), t0 + k * BEAT / 2, gain=0.10 if k % 2 else 0.06, pan=0.25)

# Reverb scurt de cameră, apoi limitare blândă și fade la final.
ir_n = int(SR * 1.6)
ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / (SR * 0.35)); ir /= np.sqrt((ir ** 2).sum())
mix = []
for ch_ in (L, R):
    wet = fftconvolve(ch_, ir)[:N]
    b, a = butter(2, 0.25); wet = lfilter(b, a, wet)
    mix.append(ch_ + 0.22 * wet)
x = np.stack(mix, axis=1)[: int(SR * DUR)]
b, a = butter(2, 35 / (SR / 2), "high"); x = lfilter(b, a, x, axis=0)
x /= np.sqrt((x ** 2).mean()) * 8.0             # RMS ≈ -18 dBFS
x = np.tanh(x * 1.1) / 1.1
t = np.arange(len(x)) / SR
x *= (np.minimum(1, t / 0.05) * np.minimum(1, np.maximum(0, (DUR - t) / 2.5)) ** 0.7)[:, None]
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
print(OUT)
