---
name: product-demo
description: Turn a raw screen recording (+ optional timed VO script .srt) into a polished product walkthrough in HyperFrames — automatic cursor/click tracking, camera that eases in to where the user clicks, click ripples, spotlights, chapter cards, stat callouts timed to the voiceover, captions, offline Kokoro VO and a ducked music bed. Works for 1-minute clips up to 10+ minute demos.
---

# Product demo from a screen recording (HyperFrames)

Tools live in `.claude/skills/product-demo/tools/` (call it `$T`). Run them from the project folder
`videos/<name>/`, with the studio venv python (`.venv/bin/python`, has opencv/numpy/soundfile).

## 1. Prepare
1. `ffprobe` the recording (size, fps, duration, audio?). Pull a frame at 5 s and look at it: find the **content
   crop** (drop browser chrome / black bars) as `x,y,w,h`.
2. Crop + conform once: `ffmpeg -i rec.mp4 -vf crop=w:h:x:y,fps=30 -c:v libx264 -crf 18 -an assets/demo.mp4`.
   All later coordinates are in this cropped content space.

## 2. Track clicks
```bash
python3 $T/track.py assets/demo.mp4 work/track.json          # cursor blobs + UI-change frames (≈ real time ÷ 3)
python3 $T/events.py work/track.json work/events.json        # click / scroll events with cursor position + 'still'
```
Check 5–10 events by pulling the frame at each `t` and confirming the cursor is where it says. Clicks with
`still` ≥ 0.25 s (cursor rested before the UI changed) are the reliable ones. If the cursor style differs, a
template match around each event (crop the cursor tip from one frame, `cv2.matchTemplate`, keep score ≥ 0.75)
tightens positions.

## 3. Voiceover (optional)
- Client gave a timed script (.srt): `~/.local/share/hf-kokoro/bin/python $T/vo_srt.py script.srt vo --voice af_heart --fix pronounce.json`
  — one WAV per block fitted to its slot (speeds up to 1.18× max; reports lines that still overrun).
  `pronounce.json` spells acronyms/brands as spoken (`{"SSO": "S S O", "SaaS": "sass"}`). Listen to 3 lines.
- Premium voice later: regenerate `vo/*.wav` + `vo/vo.json` with ElevenLabs/Higgsfield TTS (quote cost) — nothing
  else changes.
- No script: write one from the recording (chapter per screen, ≤ 2 lines per action), get it approved, then TTS.

## 4. Direct
Write `demo.json` (all fields documented at the top of `$T/director.py`): content size, duration, brand strings,
accent, `reading` framing (default view between clicks, e.g. content area with sidebar trimmed at ~1.3×),
`sidebar_x` (navigation clicks get a brief hold), `chapters` (tied to VO blocks), `callouts` (big number + label at
the moment a VO phrase is said), `focus` windows for things worth a zoom that have no click (`spotlight: true`
dims the rest).
```bash
python3 $T/director.py demo.json                                   # -> index.html + work/director.json
python3 $T/mix.py --vo vo/vo.json --total <TOTAL> --intro 4 --bed music.wav --clicks work/events.json
npx --yes hyperframes@0.8.172 lint && npx --yes hyperframes@0.8.172 check
```
Music bed: synthesize one with the `score` skill (calm pad/piano) or use a licensed track. Ducking is automatic.

## 5. Review & render
Snapshot ~10 moments (each chapter card, 3 zooms, 2 callouts) and look: zoom target actually on screen,
callout on the emptier side, captions not covering the action. Tune `focus`/`reading`, re-run director.
Render (long demos take a while — run in background), loudnorm −14 LUFS, send.
