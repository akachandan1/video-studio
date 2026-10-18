# Explainer looks

Two house looks. Each has a picture vocabulary (what's on screen), a motion vocabulary (how it moves), a prompt
template for AI scenes, and an AVOID line copied verbatim into every scene prompt. Code mode implements the same
grammar in HyperFrames (`tools/build.py`): colour field, paper grain, a counting callout, a hand-drawn marker
and one visual.

---

## `collage`: bold editorial collage

**Picture vocabulary.** Combine two or three per block, chosen to *show the idea* of that block's line:
- **Cut-out photos** with a rough white paper edge, placed on flat colour. The photo is an element inside the
  frame; the frame itself is never live action.
- **Flat colour fields:** mustard yellow, paper white, deep navy, signal coral, teal. One dominant per block,
  with the palette consistent across the video.
- **Print texture:** grain, halftone dots, newsprint, torn edges, tape strips, soft drop shadows.
- **Marker annotations:** circles that draw themselves, underlines, arrows, scribbles. Shapes only, no lettering.
- **Wordless data shapes:** bars growing, a line drawing upward, dots filling a grid, pie slices pulling apart.
- **Flat maps** with routes drawing on and pulsing location dots.
- **Highlight blocks and spotlights:** a solid bar slides over a region, or everything dims except one cut-out.
- **Scale comparisons:** one object multiplying into rows, small next to huge, stacks rising.

**Motion vocabulary.** Snappy ease-out entrances with slight overshoot, a slow push-in while a fact lands,
parallax between paper layers, and a whip or page-turn between ideas. Something always moves, but only one thing is
*loud* at a time. Each block is one continuous camera move that starts and ends in motion blur, so hard cuts
between blocks read as one take.

**Style-key image prompt (template):**
```
Editorial motion-graphics collage, flat {DOMINANT} background, a cut-out photograph of {THROUGH-LINE OBJECT}
with a rough white paper border and soft drop shadow, halftone and paper-grain texture, one red marker circle
drawn around a detail, tape strips at the corners, palette of mustard yellow, paper white, deep navy and coral,
clean graphic composition with generous negative space, magazine explainer aesthetic, {ASPECT} frame, no text,
no letters, no logos
```

**Scene prompt (template), one per block:**
```
STYLE: match the attached reference image exactly. Editorial paper collage, flat colour fields, cut-out
photographs with white paper borders, halftone grain, hand-drawn marker strokes.
SCENE: {what the block's idea looks like, the through-line object and what changes about it, 2 to 3 sentences}
MOTION: one continuous camera move over 10 seconds, starting and ending with motion blur; elements snap in
with slight overshoot; {the one loud move}; parallax between paper layers.
AUDIO: soft paper rustles and tape sounds, a subtle whoosh on the camera move, no music, no voices.
AVOID: readable text, letters, numbers, logos, watermarks, photoreal live-action footage, 3D render look,
people speaking to camera, close-up faces of real people, glossy plastic, lens flares.
```

---

## `diorama`: paper documentary

**Picture vocabulary.** Miniature worlds built from newsprint and card: sepia buildings, paper figures with
censor-bar faces, letterpress prop labels (the one place text is allowed, short and typeset), string and pins
connecting evidence, and **one burnt-orange accent** per frame (a thread, a stamp, a light). Cinematic depth of
field, as if filmed on a tabletop.

**Motion vocabulary.** FPV-style glides through the miniature, rack focus between foreground and background
props, dust in the light, slow push-ins on the evidence. Fewer, longer moves than `collage`.

**Style-key image prompt (template):**
```
Cinematic tabletop paper diorama of {THROUGH-LINE OBJECT / place}, sepia newsprint and card construction,
paper figures with black censor bars over the faces, shallow depth of field, warm practical light with dust,
one burnt orange accent, documentary mood, {ASPECT} frame, no logos
```

**Scene prompt (template):**
```
STYLE: match the attached reference image exactly. Sepia newsprint paper diorama, card miniatures,
censor-bar paper figures, one burnt orange accent, shallow depth of field.
SCENE: {the block's idea as a miniature set and what happens in it}
MOTION: one continuous FPV-style glide through the set over 10 seconds, rack focus to {key prop}, start and
end in motion blur.
AUDIO: room tone, paper creaks, a distant ticking clock, no music, no voices.
AVOID: photoreal footage, plastic toys, 3D render gloss, modern logos, readable long text, close-up faces
of real people, people speaking to camera.
```

---

## Making generators cooperate
- **Real public figures:** describe them by role in a mid-shot or silhouette ("a head of state at a podium,
  face covered by a censor bar") rather than by name.
- **Sensitive imagery** (weapons, injuries, disasters): show the idea through objects, maps, data or aftermath
  props instead.
- Some platforms push a photoreal or "3D" preset onto stylised prompts. Turn it off or decline it.
- Keep the AVOID line identical across all blocks. Consistency is what makes separate clips feel like one film.

## Code-mode visual kinds (`pack.json → blocks[].visual.kind`)
| kind | Shows | Options |
|---|---|---|
| `stat` | just the counting callout and marker | none |
| `bars` | bars growing in sequence, one highlighted | `values` (0–100), `highlight` index |
| `dots` | a grid of dots popping in (counts, crowds, rivets) | `n` |
| `calendar` | tiles filling in, the last one accented (cycles, years) | `n` |
| `tower` | a silhouette against a ruler, growing | swap the SVG in `build.py` for your through-line object |
| `lean` | a silhouette tilting as a sun moves | none |
New kinds are welcome: add a branch in `visual()` and its animation in the block loop, and keep it wordless.
