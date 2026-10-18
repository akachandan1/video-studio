"""Shared synth kit for original scores: instruments, a stereo mixer, master bus and loudness.

Every sound is generated from numpy, so there are no samples, no licences and no downloads. Typical use:

    import sys; sys.path.insert(0, "<studio>/.claude/skills/score/scripts")
    from synth import *
    mix = Mix(45.0)                       # seconds
    for b in range(16): mix.add(kick(), b * 0.4)
    mix.add(impact(), 3.2); mix.add(riser(1.6), 1.6)
    mix.write("assets/audio/score.wav")   # master bus + peak normalise
    loudnorm("assets/audio/score.wav", "assets/audio/score_-14.wav")   # optional, delivery loudness

Pitches are MIDI numbers (60 = middle C). Gains are linear, roughly 0..1. Pan is -1 (left) .. 1 (right).
The examples/ folder has three full scores built from the same instruments.
"""
import os
import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)

__all__ = ["SR", "T", "hz", "filt", "Mix", "loudnorm", "grid",
           "kick", "snare", "clap", "hat", "openhat", "cowbell", "bass808", "sub", "pluck", "piano", "marimba",
           "bell", "pad", "stab", "impact", "whoosh", "riser", "revcrash", "tick", "click", "pop", "ding",
           "key", "scratch", "glitch", "chip", "clack"]


# ---------------- helpers ----------------
def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def filt(x, kind, fc): return sosfilt(butter(2, fc, kind, fs=SR, output="sos"), x)


def grid(bpm, beats, start=0.0):
    """Beat times: grid(150, 16) -> [0, .4, .8, ...]. Lock picture cuts to these."""
    return [start + i * 60 / bpm for i in range(beats)]


class Mix:
    """Stereo bus. add() places a mono signal at a time with gain and constant-power pan."""

    def __init__(self, dur):
        self.n = int(SR * dur)
        self.L, self.R = np.zeros(self.n), np.zeros(self.n)

    def add(self, s, at, g=1.0, pan=0.0):
        i = int(round(at * SR))
        if i < 0 or i >= self.n:
            return
        s = s[: self.n - i]
        self.L[i:i + len(s)] += s * g * np.cos((pan + 1) * np.pi / 4)
        self.R[i:i + len(s)] += s * g * np.sin((pan + 1) * np.pi / 4)

    def master(self, room=True, drive=1.5, fade=1.0):
        mix = np.stack([self.L, self.R], 1)
        if room:                                   # short cross-fed early reflections = "in a room"
            rev = np.zeros_like(mix)
            for d, g in [(.029, .2), (.043, .16), (.067, .12), (.101, .09), (.149, .06)]:
                k = int(d * SR); rev[k:, 0] += mix[:-k, 1] * g; rev[k:, 1] += mix[:-k, 0] * g
            mix = mix + filt(rev.T, "low", 5000).T
        mix = np.tanh(mix * drive) / np.tanh(drive)  # soft clip glue
        if fade:
            f = int(fade * SR); mix[-f:] *= np.linspace(1, 0, f)[:, None]
        return mix * (.9 / max(1e-9, np.abs(mix).max()))

    def write(self, path, **kw):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        wavfile.write(path, SR, (self.master(**kw) * 32767).astype(np.int16))
        return path


def loudnorm(src, dst, lufs=-14):
    """Delivery loudness (social platforms ~ -14 LUFS) via ffmpeg two-pass-ish single pass."""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", f"loudnorm=I={lufs}:TP=-1.0:LRA=11",
                    "-ar", str(SR), dst], check=True)
    return dst


# ---------------- drums ----------------
def kick(g=1.0):
    t = T(.38); f = 48 + 150 * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    click_ = filt(rng.standard_normal(len(t)), "high", 3000) * np.exp(-t * 300) * .5
    return g * np.tanh((body + click_) * 1.6)
def snare(g=.5):
    t = T(.25); return g * (.6 * np.sin(2 * np.pi * 200 * t) * np.exp(-t * 25) + filt(rng.standard_normal(len(t)), "band", [1800, 9000]) * np.exp(-t * 18))
def clap(g=.5):
    t = T(.3); nz = filt(rng.standard_normal(len(t)), "band", [900, 6000])
    env = sum(np.exp(-np.maximum(0, t - d) * 35) * (t >= d) for d in (0, .01, .02, .032))
    return g * nz * env
def hat(g=.12, dec=60):
    t = T(.08); return g * filt(rng.standard_normal(len(t)), "high", 8000) * np.exp(-t * dec)
def openhat(g=.1):
    t = T(.3); return g * filt(rng.standard_normal(len(t)), "high", 7000) * np.exp(-t * 9)
def cowbell(m, g=.16, dec=11):
    t = T(.35); f = hz(m)
    s = np.sign(np.sin(2 * np.pi * f * t)) * .6 + np.sign(np.sin(2 * np.pi * f * 1.48 * t)) * .4
    return g * filt(s, "band", [f * .8, f * 6]) * np.exp(-t * dec)


# ---------------- bass & tonal ----------------
def bass808(m0, m1, d, g=.55):
    """808 with a pitch glide m0 -> m1 over the first 120 ms."""
    t = T(d); f = hz(m0) + (hz(m1) - hz(m0)) * np.clip(t / .12, 0, 1) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6) * np.minimum(1, t / .004)
    return g * np.tanh(s * 2.2) * .8
def sub(m, d, g=.4):
    t = T(d); return g * np.sin(2 * np.pi * hz(m) * t) * np.minimum(1, t / .01) * np.exp(-t * .8)
def pluck(m, g=.16, dec=6):
    t = T(1.2); f = hz(m); s = sum(((-1) ** (k + 1)) * np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
    return g * filt(s, "low", 3200) * np.exp(-t * dec)
def piano(m, d=2.0, g=.3, bright=1.0):
    """Felt-piano: decaying slightly inharmonic partials + hammer thump."""
    t = T(d); f = hz(m); s = np.zeros_like(t)
    for k, (a, dd) in enumerate([(1.0, 2.2), (.45, 3.5), (.22, 5.0), (.12, 7.0), (.06, 9.0)], start=1):
        s += a * (bright if k > 2 else 1) * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * np.exp(-t * dd)
    thump = filt(rng.standard_normal(len(t)), "low", 900) * np.exp(-t * 60) * .15
    return g * filt((s + thump) * np.minimum(1, t / .004), "low", 3200)
def marimba(m, g=.18):
    t = T(1.0); f = hz(m); return g * (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + .35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 24))
def bell(m, g=.1, d=3.0):
    t = T(d); f = hz(m); return g * sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dd) for k, a, dd in [(1, 1, 1.3), (2.76, .5, 3), (5.4, .25, 6)])
def pad(ms, d, g=.1, bright=1300, att=.7, rel=1.2):
    """Detuned chord pad. ms = list of MIDI notes."""
    t = T(d + rel)
    s = sum(np.sin(2 * np.pi * hz(m) * 2 ** (dd / 12) * t) + .28 * np.sin(4 * np.pi * hz(m) * t) for m in ms for dd in (-.07, 0, .08))
    env = np.minimum(1, t / att) * np.where(t > d, np.exp(-(t - d) * 3 / rel), 1)
    return g * filt(s / (len(ms) * 3), "low", bright) * env
def stab(ms, g=.12):
    t = T(.5); s = sum(sum(((-1) ** (k + 1)) * np.sin(2 * np.pi * hz(m) * k * t) / k for k in range(1, 10)) for m in ms)
    return g * filt(s / len(ms), "low", 2600) * np.exp(-t * 6)


# ---------------- transitions & sound design ----------------
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
def tick(m=84, g=.1):
    t = T(.05); return g * np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 90)
def click(g=.18):
    t = T(.035); return g * (np.sin(2 * np.pi * 2600 * t) * .5 + rng.standard_normal(len(t)) * .25) * np.exp(-t * 140)
def pop(g=.12):
    t = T(.08); f = 900 * np.exp(-t * 30) + 200; return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
def ding(g=.18):
    t = T(1.2); return g * (np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 4) + .5 * np.sin(2 * np.pi * 1976 * t) * np.exp(-t * 6))
def key(g=.1):
    """One keyboard keystroke (typing on screen)."""
    t = T(.04); return g * filt(rng.standard_normal(len(t)), "band", [1500, 5000]) * np.exp(-t * 180)
def scratch(g=.35):
    t = T(.45); ph = np.cumsum(600 * (1 + 2.5 * np.sin(2 * np.pi * 7 * t))) / SR
    return g * filt(np.sin(2 * np.pi * ph) * (rng.standard_normal(len(t)) * .3 + .7), "band", [300, 4000]) * np.exp(-t * 3)
def glitch(d=.14, g=.14):
    t = T(d); s = np.sign(np.sin(2 * np.pi * 330 * t * (1 + 4 * t))); s = np.repeat(s[::30], 30)[:len(t)]
    return g * filt(s.astype(float), "low", 6000) * np.exp(-t * 8)
def chip(m, d=.1, g=.07):
    t = T(d); return g * np.sign(np.sin(2 * np.pi * hz(m) * t)) * np.exp(-t * 7)
def clack(g=.5):
    """Soft magnetic closure — good under a fold / snap transition."""
    t = T(.18); body = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 45)
    return g * np.tanh((body + filt(rng.standard_normal(len(t)), "band", [1200, 5000]) * np.exp(-t * 120) * .6) * 1.4)


if __name__ == "__main__":                      # 4-bar demo: python3 synth.py demo.wav
    import sys
    m = Mix(7.0); bpm = 120
    for i, b in enumerate(grid(bpm, 12)):
        m.add(kick(.9), b); m.add(hat(), b + .25)
        if i % 2: m.add(clap(.4), b)
    for i, ch in enumerate([[57, 60, 64], [53, 57, 60], [55, 59, 62]]):
        m.add(pad(ch, 2.0), i * 2.0)
    m.add(riser(1.0), 5.0); m.add(impact(), 6.0)
    print("wrote", m.write(sys.argv[1] if len(sys.argv) > 1 else "synth_demo.wav"))
