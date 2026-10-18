# What's inside the Great Pyramid? Kurzgesagt-style flat science

<img src="../../docs/media/great-pyramid.gif" width="640">

16 seconds, one continuous world, one camera. The cross-section is **to scale** (1200 px base = 230.3 m, about
5.21 px/m): passages at roughly 26.5°, the King's Chamber floor at 43 m, the Queen's Chamber at 21 m, the
Subterranean Chamber about 30 m below ground, and the relieving chambers stacked above. The camera X-rays the
pyramid, draws the passages, lights the King's Chamber, dives in, glides up to the relieving chambers (with the
workers' graffiti) and pulls back.

Shows the `art-styles` skill's main lesson: **write custom scenes.** huashu's preset clips read like mind maps;
a custom scene with `TOON.flat` shading and `CAM.pushTo` dives reads like a real explainer.

## Rebuild
```bash
cp -R examples/great-pyramid videos/great-pyramid && cd videos/great-pyramid
cp -R ~/.claude/skills/huashu-art-motion/scripts/engine engine && cp -R demos/pyramid engine/demos/
(cd engine && uv run --with playwright python render.py --film demos/pyramid --solo pyr --no-counter --from 0 --to 16 --fps 30 --out ../hf/assets/pyramid.mp4)
../../.venv/bin/python assets/score.py && cp assets/score.wav hf/assets/
cd hf && npx --yes hyperframes@0.8.172 render -o "../../../out/Great Pyramid.mp4"
```
Preview the scene live: open `engine/index.html?film=demos/pyramid` with any static server.
