# Twelve Painters: one scene, twelve masters

<img src="../../docs/media/twelve-painters.gif" width="640">

25 seconds at 128 BPM. A single domestic scene (a woman at a table, a cat, a window) is repainted in twelve
styles, in date order. Each segment is 9 eighth-notes long, each change gets a signature transition, and a
year counter rolls continuously. The score moves one chord per painter (I–vi–IV–V in F), with a soft impact and
sparkle on every change.

`eras_painters.js` is a film definition for the huashu-art-motion engine: which of its painting styles to use,
in what order, with which transitions and labels. The engine's built-in scenes do the painting.

## Rebuild
```bash
cp -R examples/twelve-painters videos/twelve-painters && cd videos/twelve-painters
cp -R ~/.claude/skills/huashu-art-motion/scripts/engine engine && cp eras_painters.js engine/
(cd engine && uv run --with playwright python render.py --film painters --fps 30 --out ../hf/assets/painters.mp4)
../../.venv/bin/python assets/score.py && cp assets/score.wav hf/assets/
cd hf && npx --yes hyperframes@0.8.172 render -o "../../../out/Twelve Painters.mp4"
```
`--film painters` makes the engine load `eras_painters.js`.
