"""12 s phonk-style score for the chop-reel template, 150 BPM (beat 0.4 s). Cues mirror reel.js:
  0–1.6 hook: word slams 0/.4/.8/1.2, riser into the drop
  1.6 DROP (kinetic type) · 4.0 counter (ticks) · 6.4 cards (pop per beat) · 8.8 whip · 9.2 end card impact + bell chord
Run: python3 score.py   -> assets/audio/score.wav
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for up in ("../../.claude/skills/score/scripts", "../../../.claude/skills/score/scripts"):   # templates/ or videos/
    sys.path.insert(0, os.path.join(HERE, up))
from synth import *

B = 0.4; S16 = B / 4
m = Mix(12.0)
for i in range(4): m.add(impact(.35), i * B); m.add(clap(.35), i * B)      # hook slams
m.add(riser(1.2, .25), .4)

MEL = [77, None, 80, None, 77, 75, None, 72, None, 75, 77, None, 80, 82, None, 80]     # cowbell, F minor
def groove(t0, t1):
    for b0 in [t0 + k * 1.6 for k in range(int((t1 - t0) / 1.6 + .999))]:
        for s in range(16):
            at = b0 + s * S16
            if at >= t1: break
            if s in (0, 6, 10): m.add(kick(.9), at)
            if s in (4, 12): m.add(clap(.45), at)
            m.add(hat(.07 if s % 2 else .1), at)
            if MEL[s]: m.add(cowbell(MEL[s], .12), at, pan=.2)
        m.add(bass808(41, 41, 1.4, .45), b0)
groove(1.6, 8.8)
m.add(impact(.7), 1.6); m.add(revcrash(.4, .25), 3.6)
for k in range(10): m.add(tick(88 + k % 3, .06), 4.0 + k * .12)            # counter ticks
for i in range(4): m.add(pop(.18), 6.4 + i * B)                             # card pops
m.add(whoosh(.4, .3), 8.8)
m.add(impact(.7), 9.2); m.add(bass808(29, 29, 2.6, .5), 9.2)
for i, n in enumerate([65, 68, 72, 77]): m.add(bell(n, .1, 3.5), 9.2 + i * .08, pan=-.3 + .2 * i)
print("wrote", m.write(os.path.join(HERE, "assets", "audio", "score.wav"), fade=1.0))
