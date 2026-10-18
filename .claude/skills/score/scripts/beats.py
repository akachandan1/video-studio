#!/usr/bin/env python3
"""Measure the beat grid of a supplied music track so picture cuts can land on it.

  python3 beats.py <track.wav|mp3> [out_dir]      -> out_dir/beats.json + beats.js (window.BEATS)

librosa's tracker gives tempo and rough beat positions; a least-squares fit turns
them into a clean grid, and the grid phase is then snapped to the measured
percussive onsets so hits land on the actual transients. Needs librosa (setup.sh puts it in the studio .venv).
"""
import json
import os
import sys
import numpy as np
import librosa

if len(sys.argv) < 2:
    sys.exit(__doc__)
wav = sys.argv[1]
out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(wav))
y, sr = librosa.load(wav, sr=None, mono=True)
dur = len(y) / sr

tempo, raw = librosa.beat.beat_track(y=y, sr=sr, units='time', tightness=400, hop_length=256)
raw = np.asarray(raw, dtype=float)
spb = float(np.median(np.diff(raw)))
while spb > 0.8:      # octave-correct into 75-140 BPM
    spb /= 2
while spb < 0.43:
    spb *= 2

k = np.round((raw - raw[0]) / spb)
spb, phase = np.polyfit(k, raw, 1)

perc = librosa.effects.percussive(y)
onsets = librosa.onset.onset_detect(y=perc, sr=sr, units='time', hop_length=128, backtrack=False)
grid_k = np.round((onsets - phase) / spb)
resid = onsets - (phase + grid_k * spb)
close = np.abs(resid) < 0.06
if close.sum() >= 4:
    phase += float(np.median(resid[close]))
phase = (phase + spb / 2) % spb - spb / 2           # beat 0 nearest t = 0

beats = [round(phase + i * spb, 5) for i in range(int((dur - phase) / spb) + 2)]
out = {
    'source': os.path.basename(wav),
    'bpm': round(60 / spb, 3),
    'spb': round(float(spb), 6),
    'phase': round(float(phase), 5),
    'beats': beats,
    'downbeats': beats[::4],
    'measured': {'tracker_beats': [round(float(b), 4) for b in raw],
                 'onsets_used': int(close.sum()),
                 'onset_residual_ms': round(float(np.median(np.abs(resid[close])) * 1000), 2)},
}
os.makedirs(out_dir, exist_ok=True)
for name, body in (('beats.json', json.dumps(out, indent=1)),
                   ('beats.js', 'window.BEATS = ' + json.dumps(out) + ';\n')):
    with open(os.path.join(out_dir, name), 'w') as f:
        f.write(body)
print(f"bpm {out['bpm']}  phase {out['phase']*1000:.1f} ms  tracker beats {len(raw)}  "
      f"onsets used {out['measured']['onsets_used']}  residual {out['measured']['onset_residual_ms']} ms")
