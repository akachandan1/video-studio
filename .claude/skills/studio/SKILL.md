---
name: studio
description: Front door of Video Studio. Use for ANY video request in this repo — "make a video", "launch film", "ad", "reel", "showreel", "UGC", "product demo", "explainer", "captions", "music video", "edit this footage", "what can you make?", or when a newcomer just says hi. Checks setup, asks what they want to make, routes to the right workflow skill, and makes sure everything is assembled and rendered in HyperFrames under the PLAYBOOK rules.
---

# Video Studio — front door

**HyperFrames is the core engine.** Every video made here is a HyperFrames project (HTML + one paused GSAP
timeline on `window.__timelines["main"]`, `data-*` timing) that is linted, checked and rendered with
`npx hyperframes`. Other tools *feed* HyperFrames: they make shots, art, voice, music or captions that end up as
assets inside a HyperFrames composition. Load the `hyperframes` skill for composition rules before writing HTML.

## 1. First contact (every new session)
1. Run `setup/doctor.sh --quiet`. If anything **required** is ✗, tell the user in one plain line what's missing
   and offer to run `setup/setup.sh` (≈10 min, asks before each install). Optional ✗ (Higgsfield, Fal, Topaz)
   only matter when a workflow needs them — mention them then, not now.
2. If `videos/` is empty (first-timer), offer the 10-second proof render:
   `cp -R templates/hello-world videos/hello-world && cd videos/hello-world && ../../.venv/bin/python score.py && npx --yes hyperframes@0.8.172 render -o ../../out/hello-world.mp4`
   then send the MP4. This proves the whole pipeline works before any real job.

## How every message should feel
Like a well-made app: one stage per message and then wait; bold stage titles; choices as tables; short lines;
pasteable blocks that contain only what gets pasted; no narration of internal steps (file writes, checks,
timing maths). Speak where the user acts or something is missing.

## 2. Ask what they're making (plain words, no skill names)
If the request is vague, ask ONE question with options (AskUserQuestion), then route:

| They want | Route to skill | Needs |
|---|---|---|
| Fast CapCut-style reel, showreel, hype edit, story told in chop cuts | `chop-reel` | nothing paid |
| Apple / OpenAI-style product launch film, premium spec ad | `launch-film` | optional Higgsfield credits for AI shots |
| UGC / creator-style ads, AI presenter, ad variants for Meta/TikTok | `ugc-ads` (+ `ugc-actor` for casting) | Higgsfield credits |
| Screen recording → polished product walkthrough | `product-demo` | a recording; optional VO script (.srt) |
| Narrated, fact-checked explainer in a Vox-style collage or paper-diorama look ("why does X happen?") | `explainer` | nothing paid (AI scenes optional) |
| Painterly / Kurzgesagt-style explainer, art-history styles, science "what's inside" | `art-styles` | nothing paid |
| Captions / subtitles / hook on a talking video, clean up audio | `caption-video` | the video |
| Recut a long talking-head into a short (TikTok/Reels) with B-roll graphics | `talking-head-recut` (HyperFrames) + `caption-video` | the video |
| Original music / sound design / beat-synced edit | `score` | nothing paid |
| Text, article or URL → explainer or promo | `faceless-explainer`, `product-launch-video` (HyperFrames) | nothing paid |
| Music track → music video | `music-to-video` (HyperFrames) or the Fal music-video plugin | Fal key for the plugin |
| Slides / pitch → video | `slideshow` (HyperFrames) | nothing paid |
| "Use motion #020" / "open the motion-prompt library" | `motion-prompt` → port the move into HyperFrames | nothing paid |

Always ask these before building (batch them): **format** (16:9 / 9:16 / 4:5, or several), **length**, **audience &
goal**, **brand assets** (logo, colours, fonts — or "invent one"), **budget for paid generations** (credits / $ cap or "code only").

## 3. Build — the house pipeline
1. **Project:** `videos/<short-name>/` (gitignored). Start from `templates/` when one fits, else `npx hyperframes init`.
2. **Plan on paper first:** a cue sheet / shot list with times on a beat grid (e.g. 120 or 150 BPM). Picture cuts,
   sound hits and captions all reference the same times.
3. **Python** always via the studio env: `<studio>/.venv/bin/python` (from a project folder: `../../.venv/bin/python`).
4. **Make assets** with the routed workflow (code scenes, AI shots, huashu art, Kokoro VO, synth score).
5. **Assemble in HyperFrames.** `npx hyperframes lint` → fix every error → `npx hyperframes check` →
   snapshot key frames and LOOK at them (`npx hyperframes snapshot . --at <t>`).
6. **Render** → `out/<name>.mp4`, loudness-normalise to −14 LUFS
   (`ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy out.mp4`). Pull 4–6 frames and check them
   before sending. Send with SendUserFile.
7. **Multi-aspect:** lay out relative to the stage (W, H, short side M) and build each aspect from one source.

## 4. Rules that always apply
Read `docs/PLAYBOOK.md` once per session. The non-negotiables:
- **Quote cost and wait for a yes before any paid generation** (Higgsfield, Fal, ElevenLabs).
- **Real people's footage:** no AI voice regeneration, no invented frames. Denoise / EQ / upscale only.
- **Research before designing ads** (category ad libraries first; brand guides are identity, not layout rules).
- **"Edit it like this reference"** → pull frames at 6 fps and list typography, layering, placement, motion
  before building.
- No client footage, brand assets or keys ever go into this repo (`videos/` and `out/` are gitignored).

## 5. When done
Offer one next step (other aspect ratio, a variant, captions). If the job produced a reusable trick, suggest
adding it to the studio (a template, a skill section, or a PLAYBOOK rule) — that's how the kit improves.
