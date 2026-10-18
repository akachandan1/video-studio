"""8 s score for the hello-world film, built with the studio synth kit: python3 score.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for up in ("../../.claude/skills/score/scripts", "../../../.claude/skills/score/scripts"):   # templates/ or videos/
    sys.path.insert(0, os.path.join(HERE, up))
from synth import *

m = Mix(8.0)
m.add(pop(.3), 0.0); m.add(clack(.4), 0.5); m.add(whoosh(.6, .18), 0.9)
for i, b in enumerate(grid(120, 10, 1.0)):                                     # 120 BPM groove from beat 3
    m.add(kick(.8), b); m.add(hat(.08), b + .25)
    if i % 2: m.add(clap(.3), b)
for i, w in enumerate([1.0, 1.5, 2.0]): m.add(pluck(72 + 4 * i, .2), w)       # one note per title word
m.add(pad([57, 60, 64, 67], 4.0, .08), 1.0)
m.add(riser(.6, .2), 5.0); m.add(impact(.6), 6.2); m.add(bell(76, .1, 1.8), 6.25)
print("wrote", m.write(os.path.join(HERE, "assets", "audio", "score.wav"), fade=0.6))
