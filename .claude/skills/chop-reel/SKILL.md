---
name: chop-reel
description: Fast CapCut-style chop-cut reel with a story — showreels, hype edits, launch teasers, "make it punchy". One canvas engine on a beat grid (punch-ins on cuts, flash frames, impact shakes, whip pans, speed ramps, freeze frames) rendered in HyperFrames, in 16:9 and 9:16 from one edit, with an original synthesized score locked to the cuts.
---

# Chop reel (HyperFrames)

Proven on "The Brief" showreel. People judge reels by **pace and narrative**, not polish alone — a plain
montage of nice scenes reads as "basic". Give it a story with stakes.

## 1. Story first (before any code)
Write a 5–8 beat story where each beat showcases one capability and the edit itself tells it. The pattern that worked:
**hook (a problem + a clock) → work montage (one skill per section) → twist/obstacle (freeze frame, client
feedback) → smash cut answer → payoff blitz → delivered → end card.** A persistent HUD (clock that jump-cuts,
stage label) keeps viewers oriented through fast cuts.

Then a cue sheet on a grid: 150 BPM = beat 0.4 s, bar 1.6 s (or 120 BPM = 0.5 s). Every cut, slam and caption
sits on a beat; sections change on bar lines. Hook = 1 word per beat for the first 1.6–3.2 s.

## 2. Start from the template
```bash
cp -R templates/chop-reel videos/<name> && cd videos/<name>
../../.venv/bin/python score.py   # writes assets/audio/score.wav
python3 build.py 169        # writes index.html (16:9);  build.py 916 for 9:16
npx --yes hyperframes@0.8.172 lint && npx --yes hyperframes@0.8.172 render -o ../../out/<name>-169.mp4
```
`reel.js` structure — edit in this order:
- **Scenes:** `function scene(g, l)` draws a whole frame at local time `l`. Use relative units (`W`, `H`, `M`,
  `PORT`) so both aspects work; `fit()` shrinks text to a max width.
- **SHOTS:** `[t0, t1, scene]` — the edit. `null` = covered by a transition.
- **FX lists:** `PUNCH` (1.06× zoom decaying over 0.2 s on each cut + extra beats), `FLASH` (2-frame white on
  drops, half-white on section cuts), `SHAKES` `[start, dur, amp]`, `WHIPS` (motion-blurred push between scenes,
  9 sub-frame renders averaged).
- Video clips (huashu art, caption-kit renders, AI shots) go *on top* as `<video class="clip">` in `build.py`
  with their own punch tweens in GSAP; the canvas draws black underneath.

## 3. Moves library
For named moves use the **motion-prompt** skill: `node ~/.claude/skills/motion-prompt/scripts/motion-prompt.mjs get 001 043`
returns each move's published spec (curves, durations, overshoot). Port the *numbers* exactly into reel.js and
cite them in a comment (`// #043 whip pan: …`) — the user notices when moves are "inspired by" instead of used.
Useful: #001 pop-in, #005 mask reveal, #007 count-up, #008 kinetic type, #010 overshoot, #017 mask, #020 zoom
through, #023 glitch, #024 impact shake, #038 speed ramp, #040 freeze frame, #043 whip pan, #046 smash cut.

## 4. Sound
Use the `score` skill: copy `examples/phonk_150bpm_45s.py` for a full-length trap/phonk score, or extend the
template's `score.py`. Every slam/flash in reel.js gets a hit at the same time (impact, clap, riser into drops,
record scratch on the freeze, silence before the smash cut). VO via Kokoro, ducked under; captions via `caption-video`.

## 5. Check & deliver
- Snapshot each section in both aspects and look: nothing cropped in 9:16, text ≥ 4% of short side.
- Render both, loudnorm −14 LUFS, send both. Name `out/<Title> (16x9).mp4` / `(9x16).mp4`.
- Revisions: change SHOTS / scene fns → rebuild both aspects → render.
