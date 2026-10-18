---
name: score
description: Original music and sound design written in code (numpy synth — no samples, no licences) and locked to picture: cue sheet first, every hit on a cut. Phonk/trap, cinematic, felt-piano launch scores, risers, impacts, whooshes, UI ticks, typing, record scratch. Also beat-grid detection for a supplied track so cuts land on its beats, and delivery loudness (-14 LUFS).
---

# Score & sound design

`scripts/synth.py` = shared instruments + stereo `Mix` + master bus + `loudnorm`. `examples/` = three complete scores.

## Workflow
1. **Cue sheet first** — in the score file's docstring, list every picture event with its time (cuts, slams,
   freeze, VO in/out, end card). Choose BPM so sections land on bar lines (150 BPM: beat 0.4, bar 1.6; 120 BPM:
   beat 0.5, bar 2.0). Picture and score share these numbers.
2. Write `assets/audio/score.py` in the project:
   ```python
   import sys; sys.path.insert(0, "<studio>/.claude/skills/score/scripts")
   from synth import *
   m = Mix(45.0)
   for b in grid(150, 16, 3.2): m.add(kick(), b)       # beats from 3.2 s
   m.add(riser(1.6), 1.6); m.add(impact(), 3.2)       # drop on the cut
   m.write("assets/audio/score.wav")
   ```
3. Sound-design grammar that sells cuts: **riser → silence (≈0.1 s) → impact** on drops; whoosh on whips;
   record scratch + filtered loop on a freeze frame; full silence before a smash cut; pop/tick per staggered
   element; clack under folds; bell chord on the end card. Duck the bed ~10 dB under VO.
4. Mix into HyperFrames as `<audio data-track-index="10">` (VO on its own track). After rendering:
   `ffmpeg -i film.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy film_final.mp4`.

## Examples (copy one as a starting point; run `python3 file.py out.wav`)
- `phonk_150bpm_45s.py` — trap/phonk, cowbell melody, 808 glides, break with scratch, delivery build. Chop reels.
- `cinematic_120bpm_60s.py` — plucks, marimba, pads, impacts, glitch section. Showreels / explainers.
- `launch_piano_120bpm_40s.py` — felt piano motif, warm pulse, fold clacks. Premium launch films.

## Supplied music
`python3 scripts/beats.py track.mp3 assets/audio` → `beats.json` / `beats.js` (`window.BEATS.beats`, `downbeats`,
`bpm`). Snap cut times to the nearest beat; put big changes on downbeats. Check the residual it prints (< 20 ms good). BPM is folded into 75–140, so a 150 BPM track reports 75 — use half-beats.
For full music videos from a track use the HyperFrames `music-to-video` skill or the Fal music-video plugin.
