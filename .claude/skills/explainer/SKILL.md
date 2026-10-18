---
name: explainer
description: Guided studio for narrated, fact-checked explainer videos in a Vox-style editorial look (bold collage, flat colour fields, marker annotations, big numbers) or a paper-diorama documentary look. One idea in → sourced script in 10-second blocks → style key + per-scene prompts (or free code-built collage scenes) → offline voiceover fitted to each block → HyperFrames cut with captions, animated number callouts and an original score, in 16:9 and/or 9:16. Use for "Vox-style video", "explainer", "animated explainer", "data-driven video", "make a video about X", "why does X happen".
---

# Explainer (Vox-style) → HyperFrames

A ~60 s explainer is **N blocks × 10 s** (60 s = 6 blocks). Block k's narration line plays over block k's
picture. Tools: `.claude/skills/explainer/tools/` (`$T`). Style guide: `references/styles.md`. Worked example
with sources: `examples/explainer-eiffel/`.

## How it should feel
Like using a well-made app, not talking to a terminal:
- **One stage per message**, then stop and wait. A bold stage title with one fitting emoji.
- Settings and choices as **tables**; `---` dividers between sections; short lines, room to breathe.
- **No internal chatter:** never narrate file writes, tool checks, timing maths. Speak only where the user acts
  or something is missing.
- Anything meant to be pasted goes in a code block **containing only the prompt**; labels and notes stay outside.

## Stage 0 — silent checks (never narrated)
`setup/doctor.sh --quiet`. If `videos/` has explainer projects (a `pack.json` inside), open with
"Welcome back — a new video, or continue *<latest>*?" instead of Stage 1.

## Stage 1 — Welcome 🎬
A short welcome, a 5-row table of how it works (idea → look → voice → scenes → final cut), then ask **one**
question: *What should the video be about?* Any rough idea is fine, or `find one` for this week's
best topics. Stop.

## Stage 2 — Topic & settings ⚙️
- `find one` → web-search what's current; offer the **top 3**, each a one-line hook (a why/how question + a
  surprising number + why it will look good). Skip tragedies and gossip. The user picks; never pick for them.
- Otherwise sharpen the idea into **a one-line angle: a question whose answer is surprising.**

Then one settings table with defaults filled in; `go` accepts all:

| Setting | Default | Options |
|---|---|---|
| Look | `collage` | `collage` (bold editorial collage) · `diorama` (sepia paper documentary) |
| Pictures | `code` | `code` (free, built in HyperFrames) · `ai` (Higgsfield or any generator) · `mixed` |
| Length | 60 s | 30 s – 10 min, in 10 s blocks |
| Aspect | 16:9 | 16:9 · 9:16 · both |

Stop.

## Stage 3 — Research & script (silent)
Create `videos/<slug>/`. **Research every claim:** web-search, cross-check each number against **two
independent sources**, keep the URLs. If sources disagree, use the safe figure or drop it. A vague true line
beats a precise false one, so never invent a number, a quote or a prediction.

Write one narration line per block, **numbers spelled out**, plain speech:
- Kokoro voices: **22–26 words** per line. edge-tts voices: **18–20 words**. The voice step corrects drift anyway.
- Shape: **cold open** (the most surprising fact, no greeting) → stakes → evidence (one idea per block,
  each concrete: a number, date or place, escalating) → **the turn** → resolution with a kicker that echoes block 1.
- Tone: inquisitive, exact, lightly witty. It explains; it never sells.
- Design across blocks: **a recurring hero object** that comes back and changes (the tower, the container, the
  coin); **a question raised early, answered last**; one reveal moment the video is remembered by.

For each block also choose a **callout** (the number or two-word fact on screen, ≤ 9 characters, e.g.
`+15 cm`, `2.5M`, `7 yrs`) and a **visual**. In code mode the visual `kind` is one of `tower`-style silhouette
(adapt the SVG), `dots`, `bars`, `lean`, `calendar` or `stat`. Write `pack.json` (format below). Show nothing yet.

## Stage 4 — Voice 🎙
| Voice | Sound | Engine |
|---|---|---|
| `am_michael` | US male, calm documentary | Kokoro (offline, default) |
| `bm_george` | British male, measured | Kokoro |
| `af_heart` | US female, warm and clear | Kokoro |
| `en-US-ChristopherNeural` / `en-GB-RyanNeural` / `en-US-JennyNeural` | Microsoft neural voices | edge-tts (free, online) |

`samples` → voice block 1 in each of the three Kokoro voices and send the files. Stop.

## Stage 5 — The brief 📋 (gate)
One message:
- a table with angle, through-line, look, pictures, length/blocks, aspect and voice
- the script, as `Block 1 … N`
- the sources list

End: **"All good — or change anything?"** Loop until approved. The user may rewrite any line.

## Stage 6 — Pictures
**`code` mode:** skip to Stage 8. Every block becomes a collage scene: a colour field, paper grain, the
callout counting up, a marker circle drawing itself, and the visual.

**`ai` / `mixed` mode:**
1. **Style key 🎨:** offer 3 named variants in one sentence each (same visual system, different palette or
   composition, from `references/styles.md`). On the pick, give the pasteable image prompt.
   *Higgsfield:* `nano_banana_pro`, aspect = the video's. Quote the cost and wait for a yes before generating.
   One image locks the look; it's attached to every scene.
2. **Scenes 🎬:** one message per block (or all at once if asked). Each gets its narration line as context and a
   pasteable prompt built from the template in `references/styles.md`: STYLE / SCENE / MOTION / AUDIO /
   AVOID. Settings table: reference image = **the style key**, 10 s, 720p+, ambient sound on,
   save as **`blockNN.mp4`**.
   *Higgsfield directly:* `kling3_0` pro image-to-video with the style key. Quote the total
   (blocks × credits) first. Or the user runs prompts in any generator they like (Veo, Kling, Runway…).
3. **Clips come home 📥:** the user drops files in `videos/<slug>/clips/`. Rename obvious variants silently
   (`Block 1.mp4` → `block01.mp4`); ask only when a pairing is genuinely ambiguous. A block with no clip falls
   back to a code scene automatically.

## Stage 7 — Check clips (silent)
Pull a frame from each clip and look at it. Off-style or photoreal: tighten the STYLE and AVOID lines and regenerate
that block only. Two identical failures mean rewrite the prompt, not just the seed. Readable text inside AI clips is a
fail in `collage` (text lives in our callouts and captions).

## Stage 8 — Voice & cut (silent)
```bash
~/.local/share/hf-kokoro/bin/python $T/voice.py videos/<slug>                 # or --engine edge --voice en-GB-RyanNeural
```
Every take must land between **7.5 and 9.7 s**. The tool lists offenders: rewrite those lines (shorter or longer),
re-voice with `--only 3,5`, and repeat until all fit. Never time-stretch.
```bash
.venv/bin/python $T/build.py videos/<slug> [--aspect 9:16]                     # index.html + assets/mix.wav
cd videos/<slug> && npx --yes hyperframes@0.8.172 lint && npx --yes hyperframes@0.8.172 render -o raw.mp4
ffmpeg -y -i raw.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy -c:a aac -b:a 192k "../../out/<Title> (16x9).mp4"
```
`lint` warns about nested structure and dense tracks. Those concern the Studio timeline view, not the render,
so ignore them. Errors must be fixed. Snapshot a frame per block (`snapshot . --at 2.5,12.5,…`) and look:
numbers fit on one line, the marker circles the number, captions don't cover the picture.

## Stage 9 — Delivery ✅
Send the MP4. Then a small table: topic, length and aspect, look and voice, **sources** (links). Offer: the other
aspect ratio, a change to any block, or a new video.

## pack.json
```json
{ "title": "…", "angle": "…", "through_line": "…", "look": "collage", "aspect": "16:9",
  "voice": { "engine": "kokoro", "name": "am_michael" },
  "blocks": [ { "line": "…", "callout": { "big": "+15 cm", "label": "taller on the hottest days" },
                "visual": { "kind": "bars", "values": [10, 30, 60, 100], "highlight": 3 },
                "prompt": "(ai mode) full scene prompt" } ],
  "sources": [ "Publisher — title: https://…" ] }
```
Also write a human-readable `pack.md` (brief, script, prompts, sources). It's the project's record.

## Rules
- Facts: two sources per number; sources ship with every video. No invented figures, quotes or predictions.
- Paid generation only after quoting model × count × credits and getting a yes (PLAYBOOK #1).
- No real people's faces generated close-up; use mid-shots, silhouettes or censor bars, which also avoids moderation refusals.
- The Vox look is an homage. Never use Vox's logo, name or branding in the video.
