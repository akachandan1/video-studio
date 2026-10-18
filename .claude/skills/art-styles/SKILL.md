---
name: art-styles
description: Painterly and illustrated animation — Kurzgesagt-style flat science explainers ("what's inside", scale, mechanisms), art-history styles (Van Gogh, Monet, Lichtenstein, Kusama, Matisse, cubism, ink wash, 8-bit, Roman mosaic, cave painting, Persian miniature…). Uses the huashu-art-motion canvas engine with CUSTOM scenes, renders MP4s, and assembles/scores them in HyperFrames. Also the claude-animation plugin for hand-drawn 2D.
---

# Art-style animation → HyperFrames

## Engines
- **huashu-art-motion** (`~/.claude/skills/huashu-art-motion`, installed by setup.sh): deterministic canvas engine
  (`window.renderFrame(t)`), painting libs `PAINT` (strokes, halftone, pixelate, dabs, mosaic, facets, inkWash,
  brush, cut → Path2D), `TOON` (flat shading), `CAM` (pushTo dives). Read its SKILL.md for the API.
- **claude-animation plugin** (hand-drawn 2D, textured-editorial / watercolour looks) — alternative look.
- **HyperFrames** does assembly, titles, sound, captions and the final render.

## Workflow that works
1. **Custom scenes, not presets.** huashu's `render.py --spec` clips draw a centre node + satellites and read as a
   mind map. For anything showcase-grade write scenes:
   copy `scripts/engine` into `videos/<name>/engine`, create `demos/<film>/eras.js` + `<film>.js` registering
   `SCENES['id'] = (g, t, W, H) => {...}`.
2. **Kurzgesagt look:** one continuous world, flat shapes with TOON shading, rim light, a slow `CAM.pushTo` dive
   into each layer ("what's inside"), Poppins/rounded type, scale bars and labels that pop on the beat.
3. **Painter styles:** compose the subject once, then render it through each style's brush (Van Gogh = directional
   strokes along a flow field; Lichtenstein = halftone + black outline; Kusama = dots; cubism = facets
   ~nx26/ny16 with small shift — too many facets = shattered mess; ink = inkWash; 8-bit = pixelate + palette).
4. **Render** (30 fps, the engine defaults to 60):
   `uv run --with playwright python render.py --film demos/<film> --solo <id> --no-counter --fps 30 --from 0 --to <s> --out clip.mp4`
   (`--width 1080 --height 1920` for vertical).
5. **Assemble in HyperFrames:** clips as `<video class="clip">` with titles/labels as HTML on top, score from the
   `score` skill with a hit per style change, render, loudnorm −14.

Look at a frame of every style before rendering the full set — alpha/wash settings that look fine in code often
come out muddy.
