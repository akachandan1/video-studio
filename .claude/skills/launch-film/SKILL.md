---
name: launch-film
description: Apple / OpenAI-style product launch film or premium spec ad (30–60 s) — minimal supers, big product moments, signature transition, piano/pulse score, end-card lockup. Shots come from code (HyperFrames scenes), Higgsfield AI image→video, or real product footage, all assembled and rendered in HyperFrames. Includes the fold-cut builder (shots hinge shut/open on the centre line).
---

# Launch film (HyperFrames)

## 1. Concept (get a yes before spending anything)
- **One idea, one verb.** ("Open to more", "Say it.") The product's defining property becomes the film's
  signature transition or motif (a foldable → fold cuts; a voice product → type that speaks).
- **Shot plan** (table): time, shot, source (code / AI / footage), super text, sound cue. 8–12 shots for 40 s.
- **Register:** big type, few words per super (≤ 6), lots of black, one accent colour, Inter/Instrument Serif
  (SF Pro is not redistributable). End card: product name, tagline, availability line.
- If it's a real brand, label it a **spec ad** and use only official imagery the user supplies.

## 2. Shots
- **Code shots** (UI, type, product diagrams): HyperFrames compositions. Best quality-per-cost; zero credits.
- **AI shots (Higgsfield connector):** image first (`gpt_image_2_5` ≈ 2.75 credits, `nano_banana_pro` ≈ 2 credits
  for accuracy), then image→video (`kling3_0` pro, sound off ≈ 7.5 credits / 5 s; `seedance_2_5` for people).
  Use the official product image as reference. **Quote the total and wait for a yes.** Generate 1 test shot before
  the batch. Review every clip at full res — AI clips go wrong in ways thumbnails hide (warped product, extra
  hinges, text gibberish). Trim around artefacts with `data-media-start`/`playback-rate` before paying to regenerate.
- **Footage / renders** from the user: conform to H.264, same fps (30).

## 3. Fold-cut example (`examples/fold-cut/`)
`build.py` turns a SHOTS list into split-half `<video>` pairs so any cut can be a **fold** (outgoing halves hinge
shut on the centre line, landing on a magnetic "clack") or an **unfold** (incoming halves open), plus SUPERS
(hero / lower supers with line reveals). Copy it into `videos/<name>/`, put clips in `assets/clips/`, edit SHOTS
and SUPERS, `python3 build.py`, lint, check, render. The same build-from-a-list pattern works for any signature
transition (iris, slide, light-leak).

## 4. Sound
`score` skill → `examples/launch_piano_120bpm_40s.py`: felt piano motif over a warm pulse with a clack on every
fold. Change the cue list to your cuts. Or the Fal music-video plugin / a licensed track + `beats.py`.

## 5. Finish
`npx hyperframes check` (contrast, overlaps), snapshot every super, render, loudnorm −14, contact-sheet 6 frames
and look before sending. Offer 9:16 cut-down (re-layout supers; don't just crop).
