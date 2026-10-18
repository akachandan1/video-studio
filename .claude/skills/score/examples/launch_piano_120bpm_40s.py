"""Example score: launch-film felt piano — synthesized, 120 BPM, 40 s (from a product spec ad).

Felt-piano motif over a warm pulse; every fold transition gets a soft
magnetic "clack" (the hinge's magnet closure). Cue times mirror index.html:
  0-4 intro motif | 4-12 pulse + snaps | 12 unfold swell, full groove
  15/21/27/30/33 folds (clack) | 33 lockup: groove drops, final chord to 40
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 40.0
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N)
R = np.zeros(N)
BEAT = 0.5

FOLDS = [15.0, 21.0, 27.0, 30.0, 33.0]
UNFOLD = 12.0


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(sig)] += sig * gain * np.sin((pan + 1) * np.pi / 4)


def filt(x, kind, fc, order=2):
    return sosfilt(butter(order, fc, kind, fs=SR, output="sos"), x)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def piano(m, dur=2.0, g=0.3, bright=1.0):
    """Felt-piano-ish: a few decaying partials with slight inharmonicity + hammer thump."""
    t = t_arr(dur)
    f = hz(m)
    s = np.zeros_like(t)
    for k, (a, d) in enumerate([(1.0, 2.2), (0.45, 3.5), (0.22, 5.0), (0.12, 7.0), (0.06, 9.0)], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        s += a * (bright if k > 2 else 1) * np.sin(2 * np.pi * fk * t) * np.exp(-t * d)
    thump = filt(rng.standard_normal(len(t)), "low", 900) * np.exp(-t * 60) * 0.15
    env = np.minimum(1, t / 0.004)
    return g * filt((s + thump) * env, "low", 3200)


def pad(ms, dur, g=0.12, bright=1400, attack=0.8, release=1.2):
    t = t_arr(dur + release)
    s = np.zeros_like(t)
    for m in ms:
        for det in (-0.06, 0.0, 0.07):
            f = hz(m) * 2 ** (det / 12)
            s += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    s = filt(s, "low", bright) / (len(ms) * 3)
    env = np.minimum(1, t / attack) * np.where(t > dur, np.exp(-(t - dur) * 3.0 / release), 1)
    return g * s * env


def kick(g=0.8):
    t = t_arr(0.4)
    f = 48 + 90 * np.exp(-t * 30)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def snap(g=0.22):
    t = t_arr(0.18)
    nz = filt(rng.standard_normal(len(t)), "band", [1800, 6500])
    return g * nz * (np.exp(-t * 45) + 0.4 * np.exp(-np.maximum(0, t - 0.012) * 45) * (t > 0.012))


def shaker(g=0.05):
    t = t_arr(0.09)
    return g * filt(rng.standard_normal(len(t)), "high", 6000) * np.sin(np.pi * t / 0.09)


def bass(m, dur, g=0.3):
    t = t_arr(dur)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2)
    return g * filt(s, "low", 400) * env


def clack(g=0.5):
    """Magnetic closure: short low thud + bright metallic tick, tiny room."""
    t = t_arr(0.35)
    thud = np.sin(2 * np.pi * (120 + 60 * np.exp(-t * 60)) * t) * np.exp(-t * 28)
    tick = filt(rng.standard_normal(len(t)), "band", [3000, 9000]) * np.exp(-t * 180)
    ring = (np.sin(2 * np.pi * 2350 * t) + 0.6 * np.sin(2 * np.pi * 3710 * t)) * np.exp(-t * 40) * 0.12
    return g * (0.9 * thud + 0.55 * tick + ring)


def swoosh(dur=0.45, g=0.18, rising=False):
    t = t_arr(dur)
    nz = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    seg = int(0.02 * SR)
    for i in range(0, len(t), seg):
        k = i / len(t)
        k = k if rising else 1 - k
        fc = 500 + 5000 * k ** 1.5
        out[i:i + seg] = filt(nz[i:i + seg], "band", [fc * 0.6, min(fc * 1.6, SR / 2 - 200)])
    env = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 1.5
    return g * out * env


# ---------- harmony: Dm - Bb - F - C (one chord per bar = 2 s) ----------
CH = [[62, 65, 69], [58, 62, 65], [57, 60, 65], [55, 60, 64]]
ROOT = [38, 34, 41, 36]
MOTIF = [(0.0, 74), (0.5, 72), (1.0, 69), (1.5, 72)]  # per-bar top line, varied by chord


def bar_at(t):
    return int(t // 2.0) % 4


# intro 0-4: sparse motif + airy pad
add(pad([50, 57, 62, 65], 4.2, g=0.10, bright=900, attack=1.5), 0.0)
for b0 in (0.5, 2.5):
    for dt, m in [(0, 74), (0.5, 69), (1.0, 72)]:
        add(piano(m, 2.0, 0.22), b0 + dt, pan=0.15)

# body 4-33
for b0 in np.arange(4.0, 33.0 - 1e-6, 2.0):
    ci = bar_at(b0)
    lift = b0 >= 12.0
    add(pad(CH[ci], 2.0, g=0.10 if not lift else 0.13, bright=1200 if not lift else 1800, attack=0.3, release=0.5), b0)
    # piano chord stabs on 1 and the "and" of 2
    for dt in (0.0, 0.75):
        for m in CH[ci]:
            add(piano(m, 1.5, 0.11), b0 + dt, pan=-0.2)
    # motif (transposed to fit chord)
    shift = [0, -2, -2, -2][ci] if ci else 0
    for dt, m in MOTIF:
        add(piano(m + shift, 1.6, 0.16 if lift else 0.13, bright=1.2), b0 + 1.0 + dt * 0.5, pan=0.2)
    for k in range(4):
        bt = b0 + k * BEAT
        add(bass(ROOT[ci] + (12 if k == 3 else 0), 0.45, 0.28), bt)
        if b0 >= 8.0 and k in (1, 3):
            add(snap(0.2 if lift else 0.15), bt, pan=0.1)
        if lift:
            add(kick(0.7), bt)
            add(shaker(0.045), bt + BEAT / 2, pan=0.35)
            add(shaker(0.03), bt + BEAT / 4, pan=-0.35)

# unfold swell at 12 and fold clacks
add(swoosh(0.9, 0.2, rising=True), UNFOLD - 0.9)
add(pad([62, 69, 74, 77], 1.6, g=0.12, bright=2600, attack=0.05, release=0.8), UNFOLD)
for tf in FOLDS:
    add(swoosh(0.42, 0.16), tf - 0.42, pan=0.0)
    add(clack(0.55), tf)

# lockup 33-40: groove drops, final chord (F add9) + bell motif
add(pad([41, 53, 60, 65, 67, 69], 6.2, g=0.16, bright=2000, attack=0.08, release=0.8), 33.0)
add(bass(29, 3.0, 0.35), 33.0)
for i, m in enumerate([77, 81, 84, 79]):
    add(piano(m, 3.0, 0.2, bright=1.4), 33.4 + i * 0.5, pan=-0.2 + 0.15 * i)
add(piano(72, 4.0, 0.18), 35.6)
add(piano(77, 4.0, 0.16), 35.6)

# ---------- master ----------
mix = np.stack([L, R], axis=1)
rev = np.zeros_like(mix)
for d, g in [(0.029, 0.28), (0.043, 0.22), (0.067, 0.18), (0.101, 0.14), (0.149, 0.1), (0.223, 0.07), (0.31, 0.05)]:
    k = int(d * SR)
    rev[k:, 0] += mix[:-k, 1] * g
    rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 4000).T * 0.9
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
fade = int(1.5 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix *= 0.89 / np.max(np.abs(mix))
import os, sys  # out: argv[1] or <this file>.wav
wavfile.write(sys.argv[1] if len(sys.argv) > 1 else os.path.splitext(os.path.abspath(__file__))[0] + ".wav", SR, (mix * 32767).astype(np.int16))
print("ok", mix.shape[0] / SR, "s")
