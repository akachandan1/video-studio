"""'The Brief' — original phonk/trap score, 150 BPM (beat 0.4 s, bar 1.6 s), 45 s.

Cue sheet (seconds) — picture cuts are locked to this grid:
  HOOK      0–3.2   buzz 0.1/0.45, ding 0.3, typing 0.85–1.45, send 1.5, DEADLINE slam 1.6, clock ticks 2.0/2.4/2.8, riser 2.4–3.2 (gap 3.1)
  DROP 1    3.2–16  full beat; section hits 6.4 (type) 9.6 (data) 12.8 (UI)
  BREAK     16–19.2 record scratch + freeze 16.0, filtered loop, client typing 16.5–17.4, silence 17.6–18.4, SMASH "bet." 18.4, roll → 19.2
  DROP 2    19.2–28.8 harder beat; style hits every 0.8 s from 19.2; explainer 26.4
  SOUND     28.8–35.2 groove, VO 29.8–32.3 (ducked), transition hits 32.4 33.1 33.8 34.5
  DELIVERY  35.2–40  build, render ticks, DELIVERED slam 38.4, confetti pops, reverse crash → 40
  END       40–45   808 + bell chord, fade 44–45
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR, DUR = 48000, 45.0
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(150)
B = 0.4            # beat
S16 = B / 4        # 16th


def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, k, fc): return sosfilt(butter(2, fc, k, fs=SR, output="sos"), x)


def add(s, at, g=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= N or i < 0: return
    s = s[: N - i]
    L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
    R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)


# ---------------- instruments ----------------
def kick(g=1.0):
    t = T(.38); f = 48 + 150 * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click = filt(rng.standard_normal(len(t)), "high", 3000) * np.exp(-t * 300) * .5
    return g * np.tanh((body + click) * 1.6)
def clap(g=.5):
    t = T(.3); nz = filt(rng.standard_normal(len(t)), "band", [900, 6000])
    env = sum(np.exp(-np.maximum(0, t - d) * 35) * (t >= d) for d in (0, .01, .02, .032))
    return g * nz * env
def snare(g=.5):
    t = T(.25); return g * (.6 * np.sin(2 * np.pi * 200 * t) * np.exp(-t * 25) + filt(rng.standard_normal(len(t)), "band", [1800, 9000]) * np.exp(-t * 18))
def hat(g=.12, dec=60):
    t = T(.08); return g * filt(rng.standard_normal(len(t)), "high", 8000) * np.exp(-t * dec)
def openhat(g=.1):
    t = T(.3); return g * filt(rng.standard_normal(len(t)), "high", 7000) * np.exp(-t * 9)
def cowbell(m, g=.16, dec=11):
    t = T(.35); f = hz(m)
    s = np.sign(np.sin(2 * np.pi * f * t)) * .6 + np.sign(np.sin(2 * np.pi * f * 1.48 * t)) * .4
    return g * filt(s, "band", [f * .8, f * 6]) * np.exp(-t * dec)
def bass808(m0, m1, d, g=.55):
    t = T(d); f = hz(m0) + (hz(m1) - hz(m0)) * np.clip(t / .12, 0, 1) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6) * np.minimum(1, t / .004)
    return g * np.tanh(s * 2.2) * .8
def stab(ms, g=.12):
    t = T(.5); s = sum(sum(((-1) ** (k + 1)) * np.sin(2 * np.pi * hz(m) * k * t) / k for k in range(1, 10)) for m in ms)
    return g * filt(s / len(ms), "low", 2600) * np.exp(-t * 6)
def impact(g=.6):
    t = T(2.2); f = 34 + 70 * np.exp(-t * 7)
    return g * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8) + .4 * filt(rng.standard_normal(len(t)), "low", 3000) * np.exp(-t * 6))
def whoosh(d, g=.22, up=True):
    t = T(d); nz = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = int(.015 * SR)
    for i in range(0, len(t), seg):
        k = i / len(t); k = k if up else 1 - k; fc = 300 + 7000 * k ** 1.5
        out[i:i + seg] = filt(nz[i:i + seg], "band", [fc * .6, min(fc * 1.6, SR / 2 - 200)])
    return g * out * np.sin(np.pi * np.linspace(0, 1, len(t))) ** 1.3
def riser(d, g=.28): return whoosh(d, g) * np.linspace(0, 1, int(d * SR)) ** 1.8
def revcrash(d, g=.3):
    t = T(d); s = filt(rng.standard_normal(len(t)), "high", 4000) * np.exp(-t[::-1] * 2.5); return g * s * np.linspace(0, 1, len(t)) ** 2
def buzz(d=.25, g=.25):
    t = T(d); return g * filt(np.sign(np.sin(2 * np.pi * 150 * t)), "low", 900) * (0.6 + .4 * np.sign(np.sin(2 * np.pi * 30 * t)))
def ding(g=.18):
    t = T(1.2); return g * (np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 4) + .5 * np.sin(2 * np.pi * 1976 * t) * np.exp(-t * 6))
def key(g=.1):
    t = T(.04); return g * filt(rng.standard_normal(len(t)), "band", [1500, 5000]) * np.exp(-t * 180)
def tick(m=84, g=.1):
    t = T(.05); return g * np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 90)
def scratch(g=.35):
    t = T(.45); ph = np.cumsum(600 * (1 + 2.5 * np.sin(2 * np.pi * 7 * t))) / SR
    return g * filt(np.sin(2 * np.pi * ph) * (rng.standard_normal(len(t)) * .3 + .7), "band", [300, 4000]) * np.exp(-t * 3)
def bell(m, g=.1, d=3.0):
    t = T(d); f = hz(m); return g * sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dd) for k, a, dd in [(1, 1, 1.3), (2.76, .5, 3), (5.4, .25, 6)])
def pop(g=.12):
    t = T(.08); f = 900 * np.exp(-t * 30) + 200; return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
def glitch(d=.14, g=.14):
    t = T(d); s = np.sign(np.sin(2 * np.pi * 330 * t * (1 + 4 * t))); s = np.repeat(s[::30], 30)[:len(t)]
    return g * filt(s.astype(float), "low", 6000) * np.exp(-t * 8)
def chip(m, d=.1, g=.07):
    t = T(d); return g * np.sign(np.sin(2 * np.pi * hz(m) * t)) * np.exp(-t * 7)


# phonk cowbell melody (F minor), 16 steps per bar; None = rest
MEL = [[77, None, 80, None, 77, 75, None, 72, None, 75, 77, None, 80, 82, None, 80],
       [77, None, 80, None, 84, 82, None, 80, None, 77, 75, None, 72, 75, None, 77]]
BASS = [(41, 41), (41, 44), (39, 39), (36, 37)]          # 808 root per half-bar pair (F, F→Ab, Eb, C→Db)
KICK = [0, 6, 10]                                         # 16th steps with kicks (syncopated)


def groove(t0, t1, hard=False, melody=True, filtered=False):
    bar = 0
    for b0 in np.arange(t0, t1 - 1e-6, 1.6):
        for s in range(16):
            at = b0 + s * S16
            if at >= t1: break
            if s in KICK or (hard and s == 14): add(kick(.85), at)
            if s in (4, 12): add(clap(.42), at); add(snare(.18), at)
            if s % 2 == 0: add(hat(.11), at + S16 * .0, pan=.3)
            elif hard: add(hat(.06, 90), at, pan=-.3)
            if melody and MEL[bar % 2][s] is not None:
                m = MEL[bar % 2][s]; add(cowbell(m, .15 if not filtered else .07), at, pan=-.15)
                if hard: add(cowbell(m + 12, .05), at, pan=.25)
        for h in range(2):
            m0, m1 = BASS[(bar * 2 + h) % 4]
            add(bass808(m0 - 12, m1 - 12, .78, .55 if not filtered else .25), b0 + h * .8)
        if hard and bar % 2 == 1:
            for k in range(6): add(hat(.07, 120), b0 + 1.6 - .3 + k * .05, pan=.4)   # roll into next bar
        bar += 1


# ---------------- arrangement ----------------
# HOOK
add(buzz(.22, .3), .1); add(buzz(.22, .3), .45); add(ding(.2), .3)
for i in range(8): add(key(.1), .85 + i * .075)
add(whoosh(.25, .15), 1.48)
add(impact(.7), 1.6); add(stab([53, 56, 60], .14), 1.6)
for t in (2.0, 2.4, 2.8): add(tick(88, .12), t)
add(riser(.7, .3), 2.4); add(revcrash(.7, .25), 2.4)
add(bass808(29, 29, 1.0, .4), 2.4)

# DROP 1
add(impact(.8), 3.2); add(stab([53, 56, 60, 65], .16), 3.2)
groove(3.2, 16.0)
for t in (6.4, 9.6, 12.8): add(impact(.45), t); add(whoosh(.35, .18, False), t - .3)

# BREAK
add(scratch(.4), 16.0); add(impact(.4), 16.0)
groove(16.0, 17.6, melody=True, filtered=True)
for i in range(11): add(key(.08), 16.5 + i * .08)
add(ding(.12), 17.45)
add(impact(.9), 18.4); add(snare(.6), 18.4); add(bass808(29, 29, 1.0, .6), 18.4)
for i in range(16): add(snare(.06 + .02 * i / 16), 18.6 + i * (0.6 / 16))
add(riser(.8, .3), 18.4)

# DROP 2
add(impact(.9), 19.2); add(stab([53, 56, 60, 65], .18), 19.2)
groove(19.2, 28.8, hard=True)
STY = [19.2 + i * .8 for i in range(9)]
for i, t in enumerate(STY):
    [lambda t: add(whoosh(.5, .16), t), lambda t: add(clap(.4), t), lambda t: add(bell(57, .1, 1.2), t),
     lambda t: [add(chip(m, .08, .05), t + k * .1) for k, m in enumerate([72, 76, 79, 84])], lambda t: [add(pop(.1), t + k * .06) for k in range(6)],
     lambda t: add(glitch(.12, .12), t), lambda t: add(snare(.3), t), lambda t: add(whoosh(.4, .12, False), t), lambda t: add(clap(.35), t)][i % 9](t)
add(impact(.5), 26.4); add(whoosh(.8, .15), 26.4)

# SOUND
add(impact(.6), 28.8)
groove(28.8, 35.2, melody=False)
for t in (32.4, 33.1, 33.8, 34.5): add(whoosh(.35, .2), t - .15); add(glitch(.1, .08), t)

# DELIVERY
groove(35.2, 38.4, hard=True)
for i in range(24): add(tick(80 + i, .05), 35.3 + i * .12)
add(riser(1.2, .32), 37.2)
add(impact(1.0), 38.4); add(stab([53, 56, 60, 65, 68], .2), 38.4)
for k in range(10): add(pop(.12), 38.45 + k * .05, pan=-.6 + .12 * k)
groove(38.4, 39.6, hard=True)
add(revcrash(.4, .3), 39.6)

# END
add(impact(.6), 40.0); add(bass808(29, 29, 2.6, .5), 40.0)
for i, m in enumerate([65, 68, 72, 77]): add(bell(m, .11, 4.5), 40.0 + i * .08, pan=-.3 + .2 * i)
add(bell(89, .05, 3), 40.9)

# ---------------- master ----------------
mix = np.stack([L, R], 1)
rev = np.zeros_like(mix)
for d, g in [(.029, .2), (.043, .16), (.067, .12), (.101, .09), (.149, .06)]:
    k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
mix = mix + filt(rev.T, "low", 5000).T
mix = np.tanh(mix * 1.5) / np.tanh(1.5)
f = int(1.0 * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
mix *= .9 / np.abs(mix).max()
wavfile.write(__file__.replace("score.py", "score.wav"), SR, (mix * 32767).astype(np.int16))
print("ok")
