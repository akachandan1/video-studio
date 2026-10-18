#!/usr/bin/env python3
"""Polish a caption project's footage before building captions: trim dead air, colour grade,
clean the voice, and lay a soft music bed under it.

  python3 polish.py <name> [--grade clean|cinematic|none] [--music calm|none] [--music-level 0.5]
                           [--denoise 0-100] [--head 0.3] [--tail 0.9] [--no-trim]

The first run keeps the untouched files as source_orig.mp4 / transcript_orig.json and every later run
starts from those, so it can be re-run with different settings. Afterwards: caption.py build + render
(render normalises the final mix to -14 LUFS).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

KIT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("STUDIO_ROOT") or os.path.abspath(os.path.join(KIT, "..", "..", "..", ".."))
PROJECTS = os.path.join(ROOT, "videos", "captions")
DFN = os.path.expanduser("~/.venvs/dfn/bin/deepFilter")   # DeepFilterNet3 in its own venv (needs numpy<2)
SR = 48000

GRADES = {
    # warm, clean, healthy skin; gentle contrast and a soft vignette (default)
    "clean": "colortemperature=temperature=5800:mix=0.55,curves=master='0/0.015 0.3/0.275 0.7/0.735 1/1',"
             "eq=saturation=1.12:brightness=0.012,unsharp=5:5:0.35,vignette=angle=PI/6",
    # deeper contrast, cool shadows / warm highlights
    "cinematic": "curves=master='0/0 0.25/0.21 0.5/0.5 0.78/0.82 1/1',eq=saturation=1.06,"
                 "colorbalance=rs=-0.03:bs=0.04:rh=0.03:bh=-0.02,vignette=angle=PI/5",
    "none": "null",
}


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def calm_bed(dur, seed=11):
    """Soft felt-piano arpeggio + warm pad + room reverb. Deterministic. A minor-ish, unhurried, reassuring."""
    rng = np.random.default_rng(seed)
    N = int(dur * SR)
    spb = 60 / 68
    bar = 4 * spb
    mid = lambda n: 440 * 2 ** ((n - 69) / 12)
    prog = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]   # C, Am, F, G

    def piano(f, L, vel):
        tt = np.arange(L) / SR
        y = np.zeros(L)
        for h in range(1, 8):
            fh = f * h * np.sqrt(1 + 0.0004 * h * h)
            y += (vel / h ** 1.5) * np.exp(-tt * (1.0 + 0.8 * h)) * np.sin(2 * np.pi * fh * tt + rng.uniform(0, 6.28))
        return y * (1 - np.exp(-tt * 120))

    pianoT = np.zeros(N + 6 * SR)
    pad = np.zeros(N + 6 * SR)
    for i in range(int(dur / bar) + 1):
        ch = prog[i % 4]
        b0 = int(i * bar * SR)
        for k, p in enumerate([0, 2, 3, 1]):                       # sparse quarter-note arpeggio
            a0 = b0 + int(k * spb * SR)
            L = int(2.6 * SR)
            pianoT[a0:a0 + L] += piano(mid(ch[p] + 12), L, 0.045 if k == 0 else 0.03)
        L = int(3 * SR)
        pianoT[b0:b0 + L] += piano(mid(ch[0] - 12), L, 0.05)      # bass on the 1
        L = int(bar * SR) + int(0.8 * SR)
        tt = np.arange(L) / SR
        env = np.minimum(1, tt / 1.2) * np.minimum(1, (L / SR - tt) / 0.8)
        for n in ch:
            for d in (-0.07, 0.07):
                ph = (mid(n) * (1 + d / 100 * 12) * tt) % 1
                pad[b0:b0 + L] += 0.01 * env * (2 * ph - 1)
    pad = lowpass(lowpass(pad, 800), 800)
    dry = pianoT + pad
    ir_t = np.arange(int(2.8 * SR)) / SR
    ir = lowpass(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.2), 4500)
    ir /= np.abs(ir).sum() ** 0.5 * 9
    bed = (0.75 * dry + 0.4 * fftconvolve(dry, ir)[:len(dry)])[:N]
    bed = sosfilt(butter(4, 160, "highpass", fs=SR, output="sos"), bed)   # stay out of the voice's low end
    return bed / (np.sqrt(np.mean(bed ** 2)) + 1e-9)          # unit RMS


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name")
    p.add_argument("--grade", default="clean", choices=list(GRADES))
    p.add_argument("--music", default="calm", choices=["calm", "none"])
    p.add_argument("--music-level", type=float, default=1.0, help="bed level: 1 = -18 dB under speech in pauses; 0.5 = 6 dB quieter")
    p.add_argument("--denoise", type=float, default=100, help="DeepFilterNet strength 0-100 (0 = off)")
    p.add_argument("--head", type=float, default=0.3, help="seconds kept before the first word")
    p.add_argument("--tail", type=float, default=0.9, help="seconds kept after the last word")
    p.add_argument("--no-trim", action="store_true")
    a = p.parse_args()

    proj = os.path.join(PROJECTS, a.name)
    src, tj = os.path.join(proj, "source.mp4"), os.path.join(proj, "transcript.json")
    osrc, otj = os.path.join(proj, "source_orig.mp4"), os.path.join(proj, "transcript_orig.json")
    if not os.path.exists(osrc):
        shutil.copy(src, osrc)
        shutil.copy(tj, otj)
    work = os.path.join(proj, "_polish")
    os.makedirs(work, exist_ok=True)

    t = json.load(open(otj))
    words = t["words"] if isinstance(t, dict) else t
    timed = [w for w in words if "start" in w]
    dur_src = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", osrc],
                                   capture_output=True, text=True).stdout)
    t0 = 0.0 if a.no_trim else max(0.0, timed[0]["start"] - a.head)
    t1 = dur_src if a.no_trim else min(dur_src, timed[-1]["end"] + a.tail)
    dur = t1 - t0
    print(f"[polish] trim {t0:.2f}s → {t1:.2f}s  (cut {t0:.2f}s head, {dur_src - t1:.2f}s tail)")

    # voice: trimmed 48k mono → DeepFilterNet → HPF / presence / de-ess / gentle compression
    raw = os.path.join(work, "voice_raw.wav")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", osrc, "-vn", "-ac", "1", "-ar", str(SR), raw])
    voice_in = raw
    if a.denoise > 0:
        run([DFN, "--atten-lim", str(max(6, a.denoise)), "-o", work, raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cand = [f for f in os.listdir(work) if f.startswith("voice_raw_") and f.endswith(".wav")]
        if not cand:
            sys.exit("[polish] DeepFilterNet produced no output")
        voice_in = os.path.join(work, cand[0])
        print("[polish] voice denoised (DeepFilterNet3)")
    voice = os.path.join(work, "voice.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", voice_in, "-af",
         "highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3200:t=q:w=1.4:g=1.8,"
         "deesser=i=0.35,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=3", "-ar", str(SR), voice])
    v, _ = sf.read(voice)
    N = int(round(dur * SR))
    v = np.pad(v, (0, max(0, N - len(v))))[:N]

    mix = v.copy()
    if a.music != "none":
        bed = calm_bed(dur)
        # duck: bed sits ~-30 dB under speech, rises a little in pauses, fades in/out
        duck = np.full(N, 1.0)
        for w in timed:
            s, e = w["start"] - t0, w["end"] - t0
            duck[max(0, int((s - 0.2) * SR)):min(N, int((e + 0.35) * SR))] = 0.45
        k = int(0.25 * SR)
        duck = np.convolve(duck, np.ones(k) / k, mode="same")
        tt = np.arange(N) / SR
        fade = np.clip(tt / 1.5, 0, 1) * np.clip((dur - tt) / 2.0, 0, 1)
        sp = np.zeros(N, bool)
        for w in timed:
            sp[max(0, int((w["start"] - t0) * SR)):min(N, int((w["end"] - t0) * SR))] = True
        vr = np.sqrt(np.mean(v[sp] ** 2)) if sp.any() else 0.05          # speech RMS
        # level 1.0: bed -18 dB under speech in pauses, ~-25 dB while he talks (duck 0.45)
        mix = v + bed * vr * 10 ** (-18 / 20) * a.music_level * duck * fade
        print(f"[polish] music bed: calm piano + pad, ducked under speech (level {a.music_level})")
    mix /= max(1.0, np.abs(mix).max() / 0.97)
    mixwav = os.path.join(work, "mix.wav")
    sf.write(mixwav, mix, SR)

    # picture: trim + grade, muxed with the new mix
    out = os.path.join(work, "source_new.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", osrc, "-i", mixwav,
         "-map", "0:v", "-map", "1:a", "-vf", GRADES[a.grade], "-c:v", "libx264", "-crf", "16", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out])
    shutil.move(out, src)
    print(f"[polish] grade: {a.grade}")

    # captions follow the trim
    shifted = [dict(w, start=round(w["start"] - t0, 3), end=round(w["end"] - t0, 3)) if "start" in w else w for w in words]
    json.dump(dict(t, words=shifted) if isinstance(t, dict) else shifted, open(tj, "w"), indent=1)
    print(f"[polish] done → {src}  ({dur:.1f}s). Next: caption.py build {a.name} && caption.py render {a.name}")


if __name__ == "__main__":
    main()
