---
name: ugc-ads
description: UGC / creator-style ad sets for Meta, TikTok, Reels — research the category's ads first, cast an AI presenter, generate talking clips with Higgsfield, cut to real-product cutaways, and build hook × ratio variants (A/B/C × 9:16 + 4:5) in HyperFrames with cuts anchored to spoken words. Also green-screen tip videos and statics.
---

# UGC ad sets (HyperFrames + Higgsfield)

## 1. Research first — always
Before designing anything, look at what the category runs: Meta Ad Library / TikTok Creative Center / LinkedIn
ads (Apify `apify/facebook-ads-scraper` if connected, or the Arcads `spy-competitor-ads` skill). Write
`research/AD_RESEARCH.md`: ~50–150 ads, the patterns that recur in long-running ones (first-frame artifact,
first-person native feel, numbered steps, demo-not-claim, one segment per ad, CTA style), and 3–6 concepts.
The user picks the concept(s). Brand guides supply logo/palette/fonts, **not** layout rules.

## 2. Cast the presenter
Use the `ugc-actor` skill for the profile, then generate the still. **Be hyper-specific** about region,
features, styling and setting (e.g. Indian market: North Indian Punjabi features, kajal, chikankari kurta,
builder-floor jaali window; "iPhone photo, unretouched, no beauty filter, no text"). Generic prompts give generic,
wrong-market faces. Models: `nano_banana_pro` (best ethnic accuracy, ~2 cr), `soul_2` (stylised realism).
Show 3–4 candidates; the user picks one.

## 3. Talking clips (Higgsfield) — quote cost first
- `seedance_2_5` omni_reference, 720p, 15–20 s, native audio (~105–120 credits/clip): portrait + script.
- `kling3_0` pro talking clips handle Hinglish lip-sync (~14 cr / 7 s), but mangle pure Hindi.
- Hindi/other languages: write Devanagari + English in Latin, TTS with a cloned voice
  (Higgsfield `text2speech_v2` elevenlabs variant), then audio-first lip-sync (`wan2_7`, start image + audio).
- Brand names get mispronounced (e.g. an invented brand read as a common word) — spell phonetically in the script.
- Presenters often hold up a phone with a generated (fake) screen: **always cover it with a real product cutaway.**
- Green-screen tips: `npx hyperframes remove-background clip.mp4` → transparent webm over designed screens.

## 4. Build variants
- Transcribe each take: `npx hyperframes transcribe clip.mp4` (use `medium.en` if words are off); fix brand words.
- `build.py` pattern: anchor **every cut to a spoken word** from the transcript (not to seconds), so a new take
  only needs a new transcript. Generate variants: hooks A (face-first) / B (product-first) / C (proof/number-first)
  × 9:16 + 4:5 → one HyperFrames root per variant (write each to index.html and render in a loop — a project
  allows one root composition).
- Cutaways: real screen recordings (cropped tall, sped up) or HTML rebuilds of the real UI labelled "Demo".
  No fake testimonials, no invented customer numbers; claims = product mechanics.
- Captions via `caption-video` styles (Clean Box / Karaoke work best for UGC), CTA end card.
- Render all, loudnorm −14 LUFS, name `Brand_Concept_Hook_Ratio.mp4`.

## 5. Statics (optional)
HyperFrames still frames exported with `npx hyperframes snapshot . --at <t>`. For premium statics: AI lifestyle
scene with a chroma-green screen/paper, then composite the **real** product art in with an OpenCV homography — never
let an image model draw the product/artwork itself.
