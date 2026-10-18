"""Example score: cinematic showreel — 120 BPM, 60 s, every hit on a picture cue.

Cue sheet (global seconds):
  S0 0–4    dot: pop 0.5, ground contacts 1.30 1.85 2.45 3.05, riser 3.4–4
  S1 4–12   groove in at 4; MOTION 4.15, DESIGN 6.0, EDITING slam 8.32, SOUND 9.75, bounces 10.25/10.5, zoom-through 10.75–12
  S2 12–18  plucks; count-up ticks 12.9–15.5; bar pops 13.4…; exit 16.8
  S3 18–24  clicks 20.12 / 21.27, ripple 21.3, toast chime 21.5, pull-away whoosh 22.5
  S4 24–32  ambient + marimba at each scale level (24.9, 26.0, 27.2, 28.4, 29.6, 31.0)
  S5 32–42  style hits 32 (VG) 34 (pop) 36 (ink) 38 (8-bit) 40 (Kusama), riser 41.1, impact 42
  S6 42–48  star whoosh 42.15, whip 43.25–43.8, liquid 44.4, glitch 45.5–46.4, dolly tone 46.5–48
  S7 48–54  bed only (ducked under the voice in the host via automation)
  S8 54–60  landing chord 55.5, sweep shimmer 56.1, fade 59–60
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 60.0
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(2026)
BEAT = 0.5


def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, k, fc): return sosfilt(butter(2, fc, k, fs=SR, output="sos"), x)


def add(s, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    s = s[: N - i]
    L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)


def kick(g=.8):
    t = T(.45); f = 46 + 110 * np.exp(-t * 30); return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
def snare(g=.35):
    t = T(.3); return g * (.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22) + .9 * filt(rng.standard_normal(len(t)), "band", [1500, 8000]) * np.exp(-t * 15))
def clap(g=.3):
    t = T(.25); nz = filt(rng.standard_normal(len(t)), "band", [900, 5000]); env = sum(np.exp(-np.maximum(0, t - d) * 40) * (t >= d) for d in (0, .012, .024)); return g * nz * env
def hat(g=.12, dec=50):
    t = T(.12); return g * filt(rng.standard_normal(len(t)), "high", 7500) * np.exp(-t * dec)
def sub(m, d, g=.4):
    t = T(d); return g * np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / .01) * np.exp(-t * 2.5)
def bass(m, d, g=.32):
    t = T(d); f = hz(m); s = np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)
    return g * filt(s, "low", 600) * np.minimum(1, t / .005) * np.exp(-t * 4)
def pluck(m, g=.16, dec=6):
    t = T(1.2); f = hz(m); s = sum(((-1) ** (k + 1)) * np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return g * filt(s, "low", 3200) * np.exp(-t * dec)
def piano(m, d=1.6, g=.18):
    t = T(d); f = hz(m); s = sum(a * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * np.exp(-t * dd) for k, (a, dd) in enumerate([(1, 2.5), (.45, 4), (.2, 6), (.1, 8)], 1))
    return g * filt(s, "low", 3600) * np.minimum(1, t / .003)
def marimba(m, g=.18):
    t = T(1.0); f = hz(m); return g * (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + .35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 24))
def bell(m, g=.08):
    t = T(2.2); f = hz(m); return g * sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * d) for k, a, d in [(1, 1, 2), (2.76, .5, 4), (5.4, .25, 7)])
def pad(ms, d, g=.08, bright=1200, att=.6, rel=1.2):
    t = T(d + rel); s = sum(np.sin(2 * np.pi * hz(m) * 2 ** (dd / 12) * t) + .25 * np.sin(4 * np.pi * hz(m) * t) for m in ms for dd in (-.07, 0, .08))
    env = np.minimum(1, t / att) * np.where(t > d, np.exp(-(t - d) * 3 / rel), 1); return g * filt(s / (len(ms) * 3), "low", bright) * env
def impact(g=.5):
    t = T(2.0); f = 38 + 60 * np.exp(-t * 8); return g * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2) + .35 * filt(rng.standard_normal(len(t)), "low", 2500) * np.exp(-t * 7))
def whoosh(d, g=.2, up=True):
    t = T(d); nz = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = int(.02 * SR)
    for i in range(0, len(t), seg):
        k = i / len(t); k = k if up else 1 - k; fc = 300 + 6000 * k ** 1.6; out[i:i + seg] = filt(nz[i:i + seg], "band", [fc * .6, min(fc * 1.6, SR / 2 - 200)])
    return g * out * np.sin(np.pi * np.linspace(0, 1, len(t))) ** 1.4
def riser(d, g=.22):
    return whoosh(d, g, True) * np.linspace(0, 1, int(d * SR)) ** 1.5
def tick(m, g=.06):
    t = T(.05); return g * np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 90)
def click(g=.18):
    t = T(.04); return g * filt(rng.standard_normal(len(t)), "band", [2000, 6000]) * np.exp(-t * 160)
def boing(m, g=.18):
    t = T(.35); f = hz(m) * (1 + .5 * np.exp(-t * 18)); return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def chip(m, d=.12, g=.06):
    t = T(d); return g * np.sign(np.sin(2 * np.pi * hz(m) * t)) * np.exp(-t * 6)
def bitcrush(d, g=.12):
    t = T(d); s = np.sign(np.sin(2 * np.pi * 220 * t * (1 + 3 * t))) * (rng.standard_normal(len(t)) > 0.2); s = np.repeat(s[::40], 40)[:len(t)]
    return g * filt(s.astype(float), "low", 5000) * np.exp(-t * 6)
def gong(m, g=.14):
    t = T(3.0); f = hz(m); return g * sum(a * np.sin(2 * np.pi * f * k * t + k) * np.exp(-t * d) for k, a, d in [(1, 1, 1.0), (1.48, .6, 1.4), (2.31, .4, 2), (3.1, .2, 3)])


KEY = [45, 41, 48, 43]   # Am F C G roots
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]

# ---------- S0 · the dot ----------
add(sub(33, 1.4, .35), .5); add(boing(76, .14), .5)
for t, m in [(1.30, 64), (1.85, 67), (2.45, 69), (3.05, 72)]:
    add(kick(.35), t); add(boing(m, .12), t, pan=.3 * np.sin(t * 3))
add(riser(.6, .2), 3.4)

# ---------- S1 · kinetic type ----------
add(impact(.6), 4.0)
for b0 in np.arange(4.0, 12.0 - 1e-6, 2.0):
    ci = int((b0 - 4) / 2) % 4
    add(pad(CH[ci], 2, .07, 1300, .2, .4), b0)
    for k in range(4):
        bt = b0 + k * BEAT
        if bt >= 10.75: break
        add(kick(.75), bt); add(hat(.1), bt + .25, pan=.3)
        if k in (1, 3): add(clap(.22), bt)
        add(bass(KEY[ci] - 12 + (12 if k == 3 else 0), .3), bt); add(bass(KEY[ci] - 12, .2), bt + .25)
add(pluck(76, .22, 4), 4.15); add(pluck(79, .2, 4), 6.0)
add(impact(.8), 8.32); add(snare(.5), 8.32)
for i, m in enumerate([72, 74, 76, 79, 81]): add(pluck(m, .12, 8), 9.75 + i * .06)
add(tick(84, .1), 10.25); add(tick(88, .1), 10.5)
add(riser(1.2, .28), 10.75)

# ---------- S2 · data ----------
add(piano(72, 2, .16), 12.0); add(piano(76, 2, .12), 12.02); add(piano(79, 2, .1), 12.04)
add(pad([60, 64, 67, 71], 5.5, .06, 1800, .5), 12.0)
for i, t in enumerate(np.linspace(12.9, 15.5, 28)): add(tick(72 + i, .045), t, pan=-.2)
for i in range(6): add(marimba([60, 62, 64, 67, 69, 72][i], .12), 13.4 + i * .09)
for b in np.arange(12.0, 17.0, .5): add(hat(.06, 70), b + .25)
add(whoosh(.6, .12, False), 16.8)

# ---------- S3 · UI ----------
add(pad([53, 57, 60, 64], 6, .06, 1600, .4), 18.0)
add(whoosh(.6, .1), 18.1)
for b in np.arange(18.5, 22.5, .5): add(hat(.05, 80), b, pan=.4)
add(click(.2), 20.12); add(boing(84, .08), 20.18)
add(click(.2), 21.27); add(bell(84, .1), 21.5); add(bell(88, .07), 21.62)
add(whoosh(.8, .16), 22.5); add(sub(36, 1.0, .25), 23.2)

# ---------- S4 · explainer pull-out ----------
add(pad([45, 52, 57, 64], 8.5, .1, 900, 1.5, 2), 24.0)
for t, m in [(24.9, 69), (26.0, 72), (27.2, 74), (28.4, 76), (29.6, 79), (31.0, 81)]:
    add(marimba(m, .16), t, pan=.25 * np.sin(t)); add(marimba(m - 12, .08), t + .04)
for t in [24.9, 26.0, 27.2, 28.4, 29.6]: add(whoosh(1.0, .07), t)
add(riser(1.0, .14), 31.0)

# ---------- S5 · art styles ----------
for b0 in np.arange(32.0, 41.0 - 1e-6, 2.0):
    ci = int((b0 - 32) / 2) % 4
    add(pad(CH[ci], 2, .07, 1500, .1, .4), b0)
    for k in range(4):
        bt = b0 + k * BEAT
        add(kick(.7), bt); add(hat(.09), bt + .25, pan=.3)
        if k in (1, 3): add(snare(.2), bt)
        add(bass(KEY[ci] - 12, .28), bt)
add(impact(.5), 32.0); add(whoosh(.7, .14), 32.0)                     # Van Gogh swirl
add(snare(.5), 34.0); add(clap(.4), 34.0); add(chip(84, .08, .05), 34.05)  # pop BAM
add(gong(57, .16), 36.0)                                               # ink
for i, m in enumerate([72, 76, 79, 84, 79, 84, 88]): add(chip(m, .1, .045), 38.0 + i * .125, pan=.3)  # 8-bit
for i in range(8): add(boing(80 + (i * 5) % 12, .07), 40.0 + i * .11, pan=-.4 + .1 * i)               # Kusama
add(riser(.9, .3), 41.1); add(impact(.7), 42.0)

# ---------- S6 · transitions ----------
add(whoosh(.7, .22), 42.15)
add(whoosh(.55, .3), 43.25); add(kick(.5), 43.53)
for k in range(10): add(boing(55 + k * 2, .05), 44.4 + k * .09, pan=-.5 + .1 * k)
add(whoosh(.9, .12, False), 44.45)
for t in [45.5, 45.78, 46.22]: add(bitcrush(.18, .12), t)
t = T(1.5); tone = np.sin(2 * np.pi * np.cumsum(110 * (1 + t * 1.2)) / SR) * np.linspace(0, 1, len(t)) ** 1.5 * .1
add(tone, 46.5); add(riser(1.4, .18), 46.5)
for b in np.arange(42.0, 46.5, .5): add(kick(.5), b); add(hat(.08), b + .25)

# ---------- S7 · voice bed (ducked in host) ----------
add(impact(.3), 48.0)
add(pad([45, 52, 57, 60, 64], 6.2, .045, 900, .8), 48.0)
for b in np.arange(48.0, 54.0, 2.0): add(sub(33, .8, .07), b)

# ---------- S8 · end ----------
add(pad([41, 53, 60, 64, 67, 72], 5.5, .13, 1700, .3, 1.5), 54.0)
add(impact(.45), 55.5)
for i, m in enumerate([72, 76, 79, 84]): add(piano(m, 3.5, .14), 55.5 + i * .09, pan=-.3 + .2 * i)
add(bell(96, .05), 56.1); add(bell(100, .04), 56.25)

mix = np.stack([L, R], 1)
rev = np.zeros_like(mix)
for d, g in [(.031, .26), (.047, .21), (.073, .16), (.109, .12), (.157, .09), (.223, .06), (.31, .04)]:
    k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 3800).T
mix = np.tanh(mix * 1.35) / np.tanh(1.35)
f = int(1.2 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix *= .89 / np.abs(mix).max()
import os, sys  # out: argv[1] or <this file>.wav
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else os.path.splitext(os.path.abspath(__file__))[0] + ".wav", SR, (mix * 32767).astype(np.int16))
print("ok")
