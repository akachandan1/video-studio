# Eight Eras: art traditions through time

<img src="../../docs/media/eight-eras.gif" width="640">

21 seconds through eight traditions, from cave painting and Egyptian wall painting to Persian miniatures.
Each era uses its own palette, line and lettering, with a year counter that rolls continuously and a hit on
every change in the synthesized score.

Like [twelve-painters](../twelve-painters/), `eras_eras.js` is a film definition for huashu-art-motion, and
HyperFrames does the titles, score and final render.

## Rebuild
```bash
cp -R examples/eight-eras videos/eight-eras && cd videos/eight-eras
cp -R ~/.claude/skills/huashu-art-motion/scripts/engine engine && cp eras_eras.js engine/
(cd engine && uv run --with playwright python render.py --film eras --fps 30 --out ../hf/assets/eras.mp4)
../../.venv/bin/python assets/score.py && cp assets/score.wav hf/assets/
cd hf && npx --yes hyperframes@0.8.172 render -o "../../../out/Eight Eras.mp4"
```
