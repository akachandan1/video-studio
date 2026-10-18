"""Score for the 12-painter reel — 128 BPM, 25.3 s, one hit on every style change.
Segments are 9 eighths (2.109375 s); boundaries at i * 2.109375. A light piano/pizzicato groove
moves one chord per segment (I–vi–IV–V cycle in F), each transition gets a soft impact + sparkle,
and the last segment resolves into a held chord."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 25.3
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(12)
E8 = 60 / 128 / 2
SEG = 9 * E8
BOUNDS = [i * SEG for i in range(1, 12)]


def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, k, fc): return sosfilt(butter(2, fc, k, fs=SR, output="sos"), x)


def add(s, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    s = s[: N - i]
    L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)


def piano(m, dur=1.6, g=0.2):
    t = T(dur); f = hz(m); s = np.zeros_like(t)
    for k, (a, d) in enumerate([(1, 2.5), (.45, 4), (.2, 6), (.1, 8)], 1):
        s += a * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * np.exp(-t * d)
    return g * filt(s * np.minimum(1, t / .003), "low", 3500)


def pizz(m, g=0.16):
    t = T(0.5); f = hz(m)
    return g * (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 12)


def pad(ms, dur, g=0.08):
    t = T(dur + .6); s = sum(np.sin(2 * np.pi * hz(m) * 2 ** (d / 12) * t) for m in ms for d in (-.07, 0, .08))
    env = np.minimum(1, t / .4) * np.where(t > dur, np.exp(-(t - dur) * 5), 1)
    return g * filt(s / (len(ms) * 3), "low", 1500) * env


def kick(g=.5):
    t = T(.35); f = 50 + 80 * np.exp(-t * 30)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)


def tick(g=.05):
    t = T(.06); return g * filt(rng.standard_normal(len(t)), "high", 7000) * np.exp(-t * 70)


def impact(g=.35):
    t = T(1.4); f = 45 + 50 * np.exp(-t * 8)
    nz = filt(rng.standard_normal(len(t)), "low", 2500) * np.exp(-t * 9)
    return g * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) + .4 * nz)


def sparkle(g=.06):
    t = T(.9); s = sum(np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * (5 + i)) for i, m in enumerate([96, 100, 103, 108]))
    return g * s


CH = [[65, 69, 72], [62, 65, 69], [58, 62, 65], [60, 64, 67]]   # F Dm Bb C
ROOT = [41, 38, 46, 36]
for i in range(12):
    t0, ci = i * SEG, i % 4
    last = i == 11
    add(pad(CH[ci], SEG if not last else 3.5, .09 if not last else .12), t0)
    for k in range(9):                                    # eighth-note pizzicato pulse
        at = t0 + k * E8
        add(pizz(ROOT[ci] + 12 + (7 if k % 3 == 2 else 0)), at, pan=-.3)
        if i >= 2: add(tick(), at + E8 / 2, pan=.4)
        if i >= 4 and k % 2 == 0: add(kick(.45), at)
    for k, m in enumerate(CH[ci]):                        # piano answer on beat 1
        add(piano(m + 12, 1.4, .1), t0 + .02 + k * .03, pan=.2)
    add(piano(CH[ci][-1] + 24, 1.0, .08), t0 + 4 * E8, pan=.3)
for b in BOUNDS:
    add(impact(.3), b); add(sparkle(), b, pan=.2)
# end: held F add9 + bell
for k, m in enumerate([53, 65, 69, 72, 79]): add(piano(m, 3.5, .14), 23.4 + k * .06)

mix = np.stack([L, R], 1)
rev = np.zeros_like(mix)
for d, g in [(.031, .25), (.047, .2), (.073, .16), (.11, .12), (.16, .08), (.23, .05)]:
    k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 4000).T
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
f = int(1.0 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix *= .89 / np.abs(mix).max()
wavfile.write(__file__.replace("score.py", "score.wav"), SR, (mix * 32767).astype(np.int16))
print("ok")
