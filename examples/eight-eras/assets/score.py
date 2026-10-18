"""Score for the eight-eras reel — 128 BPM, 20.63 s, one hit on every era change.
Segments are 11 eighths (2.578125 s). D Dorian drone with a breathy flute, plucked-string ostinato
(oud/guqin-like Karplus–Strong), frame drum on the pulse from the third era, an impact + bell on each
boundary, and a final open fifth under the ink painting."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 20.633
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(21)
E8 = 60 / 128 / 2
SEG = 11 * E8
BOUNDS = [i * SEG for i in range(1, 8)]


def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, k, fc): return sosfilt(butter(2, fc, k, fs=SR, output="sos"), x)


def add(s, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    s = s[: N - i]
    L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)


def pluck(m, dur=1.2, g=0.22, damp=0.996):
    n = int(dur * SR); p = max(2, int(SR / hz(m)))
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return g * filt(out, "low", 4000)


def drone(ms, dur, g=0.07):
    t = T(dur + 1); s = sum(np.sin(2 * np.pi * hz(m) * 2 ** (d / 12) * t) for m in ms for d in (-.06, 0, .07))
    env = np.minimum(1, t / 1.2) * np.where(t > dur, np.exp(-(t - dur) * 4), 1)
    return g * filt(s / (len(ms) * 3), "low", 900) * env


def flute(m, dur, g=0.06):
    t = T(dur); f = hz(m) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    breath = filt(rng.standard_normal(len(t)), "band", [hz(m) * 0.8, hz(m) * 3]) * 0.25
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.3)
    return g * (tone + breath) * env


def drum(g=0.35, low=True):
    t = T(0.4); f = (70 if low else 180) + 60 * np.exp(-t * 25)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (9 if low else 18))
    slap = filt(rng.standard_normal(len(t)), "band", [800, 4000]) * np.exp(-t * 60) * 0.3
    return g * (body + slap)


def impact(g=0.3):
    t = T(1.5); f = 42 + 40 * np.exp(-t * 7)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)


def bell(m, g=0.08):
    t = T(2.0); f = hz(m)
    return g * sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * d) for k, a, d in [(1, 1, 2), (2.76, .5, 4), (5.4, .25, 7)])


# drone bed, root shifts with the eras (D – D – A – G – D – F – C – D)
ROOTS = [38, 38, 45, 43, 38, 41, 36, 38]
for i, r in enumerate(ROOTS):
    add(drone([r, r + 7, r + 12], SEG if i < 7 else 3.5, 0.08), i * SEG)
# flute phrases (Dorian)
for at, m, d in [(0.3, 74, 1.8), (2.7, 72, 1.0), (3.8, 69, 1.3), (5.4, 76, 1.6), (10.5, 77, 1.4), (15.6, 74, 1.4), (18.2, 69, 2.2)]:
    add(flute(m, d), at, pan=0.25)
# plucked ostinato from era 2
PAT = [0, 7, 12, 10, 7, 12, 14, 12, 7, 10, 5]
for i in range(1, 8):
    r = ROOTS[i] + 12
    for k in range(11):
        if (k % 2 == 0) or i >= 4:
            add(pluck(r + PAT[k], 0.8, 0.13), i * SEG + k * E8, pan=-0.3 + 0.06 * k)
# frame drum from era 3
for i in range(2, 8):
    for k in range(11):
        at = i * SEG + k * E8
        if k in (0, 4, 7): add(drum(0.32, True), at)
        elif i >= 5 and k in (2, 6, 9): add(drum(0.12, False), at, pan=0.3)
# era changes
for j, b in enumerate(BOUNDS):
    add(impact(0.28), b); add(bell([81, 79, 76, 81, 77, 79, 74][j]), b, pan=0.2)
# ending: open fifth + bell under the ink painting
add(pluck(50, 3.0, 0.18), 18.1); add(pluck(57, 3.0, 0.15), 18.16); add(bell(86, 0.07), 18.6)

mix = np.stack([L, R], 1)
rev = np.zeros_like(mix)
for d, g in [(.037, .3), (.061, .24), (.091, .19), (.137, .14), (.203, .1), (.3, .07), (.43, .05)]:
    k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 3800).T
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
f = int(1.2 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix *= .89 / np.abs(mix).max()
wavfile.write(__file__.replace("score.py", "score.wav"), SR, (mix * 32767).astype(np.int16))
print("ok")
