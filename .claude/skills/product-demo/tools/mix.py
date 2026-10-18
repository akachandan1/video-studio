# Demo audio: voiceover lines + looped music bed (ducked under speech) + soft click ticks -> one WAV.
#   python3 mix.py --vo vo/vo.json --total 640 [--intro 4] [--bed music.wav] [--clicks events.json] [--out assets/mix.wav]
# vo.json comes from vo_srt.py: [{i, start, dur, ...}] with audio at vo/<i:02d>.wav (start = seconds in the recording).
# --intro shifts the VO when the film has a title card before the recording starts.
# Ducking: bed -26 dB under speech, -16 dB in gaps, -9 dB on the intro/outro.
import argparse, json, os, subprocess, numpy as np, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument('--vo', required=True); ap.add_argument('--total', type=float, required=True)
ap.add_argument('--intro', type=float, default=0.0); ap.add_argument('--bed', default='')
ap.add_argument('--clicks', default='', help='events.json; ticks on kind=click events (times in the recording)')
ap.add_argument('--out', default='assets/mix.wav')
A = ap.parse_args()
SR = 48000; N = int(A.total * SR) + SR; INTRO = A.intro
vo = json.load(open(A.vo)); vodir = os.path.dirname(os.path.abspath(A.vo))

def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

voice = np.zeros((N, 2), np.float32); speech = np.zeros(N, np.float32)
prev_end = -1
for v in vo:
    at = max(v['start'], prev_end + 0.3); prev_end = at + v['dur']          # never let lines overlap
    a = load(os.path.join(vodir, f"{v['i']:02d}.wav")); i = int((INTRO + at) * SR)
    voice[i:i + len(a)] += a[:N - i]
    speech[i:i + len(a)] = 1

bed = np.zeros((N, 2), np.float32)
if A.bed:                                                                   # loop with 4 s crossfades
    src = load(A.bed); xf = min(4 * SR, len(src) // 3); pos = 0
    ramp = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
    while pos < N:
        seg = src.copy()
        if pos > 0: seg[:xf] *= ramp
        seg[-xf:] *= ramp[::-1]
        end = min(N, pos + len(seg)); bed[pos:end] += seg[:end - pos]
        pos += len(seg) - xf
    k = int(0.35 * SR)
    sm = np.convolve(speech, np.ones(k) / k, mode='same')
    gain = 10 ** ((-16 + (-10) * np.clip(sm * 1.6, 0, 1)) / 20)
    t = np.arange(N) / SR
    last_vo = INTRO + prev_end if vo else A.total
    loud = (t < INTRO) | (t > last_vo + 1.0)
    gain = np.where(loud, np.maximum(gain, 10 ** (-9 / 20)), gain).astype(np.float32)
    bed *= (gain * np.clip((A.total - t) / 2.5, 0, 1).astype(np.float32))[:, None]

clicks = np.zeros((N, 2), np.float32)
if A.clicks:
    L = int(0.035 * SR); tt = np.arange(L) / SR; rng = np.random.default_rng(7)
    tick = ((np.sin(2 * np.pi * 2600 * tt) * 0.5 + rng.standard_normal(L) * 0.25) * np.exp(-tt * 140) * 0.16).astype(np.float32)
    for e in json.load(open(A.clicks))['events']:
        if e['kind'] != 'click': continue
        i = int((INTRO + e['t']) * SR)
        if 0 <= i < N - L: clicks[i:i + L] += tick[:, None]

mix = voice + bed + clicks
peak = np.abs(mix).max(); mix *= min(1.0, 0.95 / max(peak, 1e-9))
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
sf.write(A.out, mix[:int(A.total * SR)], SR, subtype='PCM_16')
print('mix ok ->', A.out, 'peak', round(float(peak), 3), '(run loudnorm -14 LUFS on the final render)')
