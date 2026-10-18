"""Ambient score for the Great Pyramid sample (16 s), cue-locked to demos/pyramid/pyramid.js.
Warm pads in D Phrygian, soft marimba plinks on every label pop, rising air on each dive,
a glassy shimmer under the x-ray scan, a low bloom on the graffiti reveal and a resolve at the end line."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 16.0
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(3)


def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, kind, fc): return sosfilt(butter(2, fc, kind, fs=SR, output="sos"), x)


def add(s, at, g=1.0, pan=0.0):
    i = int(at * SR)
    s = s[: max(0, N - i)]
    L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)


def pad(ms, dur, g=0.1, bright=900, att=1.5, rel=2.0):
    t = T(dur + rel); s = np.zeros_like(t)
    for m in ms:
        for d in (-0.08, 0, 0.09):
            f = hz(m) * 2 ** (d / 12); s += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / att) * np.where(t > dur, np.exp(-(t - dur) * 3 / rel), 1)
    return g * filt(s / (len(ms) * 3), "low", bright) * env


def marimba(m, g=0.18):
    t = T(1.2); f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 22)
    return g * s * np.minimum(1, t / 0.002)


def air(dur, g=0.16):
    t = T(dur); nz = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = int(0.02 * SR)
    for i in range(0, len(t), seg):
        fc = 300 + 4500 * (i / len(t)) ** 2
        out[i:i + seg] = filt(nz[i:i + seg], "band", [fc * 0.6, fc * 1.5])
    return g * out * np.linspace(0, 1, len(t)) ** 1.8


def shimmer(dur, g=0.05):
    t = T(dur); s = np.zeros_like(t)
    for k, m in enumerate([86, 89, 93, 98]):
        s += np.sin(2 * np.pi * hz(m) * t + k) * (0.5 + 0.5 * np.sin(2 * np.pi * (3 + k) * t))
    return g * s * np.sin(np.pi * t / dur)


def boom(g=0.5):
    t = T(2.5); f = 40 + 30 * np.exp(-t * 6)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)


# bed: D Phrygian (D Eb F G A Bb C)
add(pad([38, 50, 57], 7.5, 0.13, 600, 2.5), 0.0)
add(pad([39, 51, 58, 62], 4.5, 0.1, 800, 1.0), 7.2)          # Eb colour while diving into the granite
add(pad([41, 53, 60, 65], 3.0, 0.1, 1000, 0.8), 11.0)
add(pad([38, 50, 57, 62, 69], 4.0, 0.14, 1400, 0.5, 2.5), 13.0)
# title plinks
for i, m in enumerate([74, 77, 81]): add(marimba(m, 0.12), 0.3 + i * 0.32, pan=-0.2 + 0.2 * i)
# x-ray scan
add(shimmer(1.4), 3.0)
# label pops
for at, m in [(4.1, 69), (4.6, 74), (5.0, 72), (5.4, 70), (5.7, 69), (6.0, 77), (9.25, 74), (9.45, 77), (11.4, 81)]:
    add(marimba(m), at, pan=0.25 * np.sin(at))
# light-up + dives
add(marimba(86, 0.1), 6.95); add(marimba(81, 0.1), 7.05)
add(air(1.9, 0.18), 7.4); add(air(1.0, 0.18), 12.0)
add(boom(0.35), 9.3)
# graffiti reveal + pull back
add(boom(0.5), 13.0); add(marimba(74, 0.16), 13.05); add(marimba(81, 0.12), 13.2)
add(air(1.2, 0.1)[::-1], 13.6)
# end line resolve
for i, m in enumerate([62, 69, 74, 77]): add(marimba(m, 0.13), 14.6 + i * 0.12, pan=-0.3 + 0.2 * i)

mix = np.stack([L, R], 1)
rev = np.zeros_like(mix)
for d, g in [(0.037, .3), (0.059, .24), (0.089, .19), (0.131, .14), (0.197, .1), (0.29, .07), (0.41, .05)]:
    k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 3500).T
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
f = int(1.0 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix *= 0.89 / np.abs(mix).max()
wavfile.write(__file__.replace("score.py", "score.wav"), SR, (mix * 32767).astype(np.int16))
print("ok")
