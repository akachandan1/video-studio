# The Brief: a 45-second chop-cut showreel

<img src="../../docs/media/the-brief-169.gif" width="560"> <img src="../../docs/media/the-brief-916.gif" width="180">

**The story:** a client brief lands at 09:00 for a speaker called *Dot*, with a 60-minute deadline. A clock HUD
jump-cuts through the hour: storyboard → kinetic titles → data → product UI → **freeze**, *"can it be more
artistic?"* → smash cut **BET.** → a nine-style art blitz plus a Kurzgesagt-style exploded view → voiceover
with karaoke captions → transition run → render bar → **DELIVERED** → end card. Every capability of the studio
appears once, and the edit tells the story.

| Layer | How | File |
|---|---|---|
| Edit + motion graphics | One canvas engine, a SHOTS list on a 150 BPM grid, CapCut FX (punch-ins, flash frames, impact shakes, whip pans). Motion Prompt moves ported from their published specs and cited inline (`#001`, `#043`…) | `reel/reel.js`, `reel/build.py` |
| Art blitz | huashu-art-motion: one flat scene repainted in 9 styles (Van Gogh, Lichtenstein, ink, 8-bit, Kusama, cubism, mosaic, Monet, Matisse), then an exploded view | `blitz/blitz.js`, `blitz/eras.js` |
| "Now make it sing" | Kokoro VO (`am_michael`), its loudness envelope drives the type; captions from the caption kit (karaoke) | `sing/build.py`, `vo/env.json` |
| Score | Original phonk/trap at 150 BPM, synthesized, every hit on a cut | `assets/audio/score.py` |

## Rebuild
```bash
cp -R examples/the-brief videos/the-brief && cd videos/the-brief
# 1. score
../../.venv/bin/python assets/audio/score.py && cp assets/audio/score.wav reel/assets/audio/
# 2. art blitz (per aspect) with huashu
cp -R ~/.claude/skills/huashu-art-motion/scripts/engine engine && mkdir -p engine/demos/blitz && cp blitz/*.js engine/demos/blitz/
(cd engine && uv run --with playwright python render.py --film demos/blitz --no-counter --fps 30 --out ../reel/assets/video/blitz_169.mp4)
(cd engine && uv run --with playwright python render.py --film demos/blitz --no-counter --fps 30 --width 1080 --height 1920 --out ../reel/assets/video/blitz_916.mp4)
# 3. voice + sing clip
HYPERFRAMES_PYTHON=~/.local/share/hf-kokoro/bin/python npx --yes hyperframes@0.8.172 tts "Now make it sing." -v am_michael -o reel/assets/audio/vo36.wav
#    build sing/ per aspect, caption it with the caption-video skill (karaoke), save as reel/assets/video/sing_169.mp4 / sing_916.mp4
# 4. assemble + render both aspects
cd reel && python3 build.py 169 && npx --yes hyperframes@0.8.172 render -o "../../../out/The Brief (16x9).mp4"
python3 build.py 916 && npx --yes hyperframes@0.8.172 render -o "../../../out/The Brief (9x16).mp4"
```
The end card carries the author's name. Change `endcard()` in `reel.js` for your own.
