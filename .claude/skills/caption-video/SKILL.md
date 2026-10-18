---
name: caption-video
description: Add styled, word-synced captions (and an optional scroll-stopping hook) to a talking video. The user gives a video; you transcribe it, show every caption style rendered on their own footage, they pick a style and hook, and you render the captioned MP4. Use when the user uploads/gives a video and says "caption this", "add captions/subtitles", "make captions", "caption styles", "add a hook", or invokes /caption-video.
---

# Caption a video

The user gives a talking video. They choose from the caption-style catalog, which is previewed on
their own footage, and you deliver the captioned MP4. Everything runs locally with HyperFrames.
After Effects is never needed.

**Kit:** `.claude/skills/caption-video/kit/` inside the studio repo. Projects are created in
`videos/captions/<name>/` and finished videos go to `out/captions/<name>.mp4` (both relative to the studio root).

From the studio root, set `K="$PWD/.claude/skills/caption-video/kit"` and run `python3 "$K/caption.py" …`
(quote paths; folders may contain spaces). Use the studio venv python (`.venv/bin/python`) if `numpy`/`scipy`
are missing from the system python — `setup/setup.sh` creates it.

## Flow

### 1. Get the video
If no video path was given, ask for one. Check that it exists and has a speaking person. Run:

```bash
python3 "$K/caption.py" new "<video path>" <short-name>
```

This copies the video, re-encodes it to H.264, and transcribes it word-by-word with WhisperX. The
first run in a while can take a minute. Long videos take roughly real time ÷ 4.

### 2. Show the transcript
Print the transcript from the command output in a readable block. Point out any likely mistakes,
especially brand names and jargon (product names, "HyperFrames", acronyms), and ask the user
to confirm or correct them. Corrections go in `--fix "wrong=right,…"` at build time. If the
transcript reads as gibberish, or the audio has no speech, stop and say so. Don't caption made-up words.

### 3. Show every style on their footage
Run `python3 "$K/caption.py" styles` for the list and `python3 "$K/caption.py" preview <name>` for
the visual sheet. The sheet is at `videos/captions/<name>/previews/styles.png`. Look at it yourself,
then send it with `SendUserFile` (display `render`). Next to it, give the numbered list with each
style's "best for" line:

1. **Lime Hook**: the template look (Anton caps, lime spoken word)
2. **Karaoke Pop**: big 2-word bursts, yellow spoken word
3. **One Word**: one giant word at a time
4. **Clean Box**: dark text on a white card, highlighter on the spoken word
5. **Editorial**: calm sentence case, key words in italic serif
6. **Subtitle**: small full-sentence subtitles
7. **Neon**: cyan glow on the spoken word

Recommend one in a single line based on the content: hype or social → 1 or 2, explainer or ad → 4,
founder story or premium → 5, interview or podcast → 6, tech or AI → 7. Then ask them to pick a
number. If the catalog in `caption.py` has changed, list what `styles` prints rather than this copy.

### 4. Hook (optional)
Suggest 3 hooks taken from what the speaker actually says. Lead with the most surprising number,
result or contradiction, use 4–8 words, and keep the payoff to one big word. Format each one in
hook syntax, then ask with `AskUserQuestion`: three hook options plus "No hook" (the user can also
type their own).

The hook syntax uses one line per `|`, each starting with its style:
- `s:` italic serif intro ("How", "Why")
- `c:` white condensed caps setup
- `b:` the big ringed payoff word or number (1–2 words)
- `l:` lime caps twist
- `r:` small italic tag

Example: `s:How|c:I reached|b:300k+|l:without ads|r:views`. The hook must match what the video
delivers in its first 10 seconds.

### 4b. Polish (offer it; run it when they ask for grading, cleaner audio, trimming or music)
```bash
python3 "$K/polish.py" <name> [--grade clean|cinematic|none] [--music calm|none] [--music-level 1.0] [--denoise 100]
```
- **Trim:** cuts dead air before the first word and after the last (keeps 0.3 s and 0.9 s), and shifts
  the transcript to match.
- **Grade:** `clean` (default) gives warm, healthy skin, gentle contrast and a soft vignette. `cinematic`
  is deeper and cooler. Before choosing, compare one frame of each against the original and look at it.
- **Voice:** DeepFilterNet3 noise removal (`~/.venvs/dfn`, created by setup.sh; never install it globally, it needs numpy<2),
  then a high-pass, presence boost, de-esser and gentle compression.
- **Music:** a synthesized calm piano and pad bed. At level 1 it sits about 20 dB under the voice in
  pauses and about 25 dB under while they talk. Use `--music-level 0.6` for quieter or `1.5` for more present.
- Originals are kept as `source_orig.mp4` / `transcript_orig.json`, so polish can be re-run with any
  settings. After polishing, run `build` and `render` again.
- Mention any stumbles or false starts in the opening ("at the present, at the moment…"). Cutting them
  makes a small jump cut, so ask before doing it.

### 5. Build, check, render
```bash
python3 "$K/caption.py" build <name> --style <key> [--hook "…"] [--hot "word,word"] [--fix "a=b"]
cd "videos/captions/<name>" && npx --yes hyperframes@0.8.147 check
python3 "$K/caption.py" render <name>
```

- `--hot` lists words that stay in the accent colour. Pick 2–5 payoff words; numbers are hot automatically.
- `check` contrast warnings at the hook's fade-out moment are expected. Fix any real errors before rendering.
- Before rendering a hook, snapshot it (`npx --yes hyperframes@0.8.147 snapshot . --at 1.6 --no-end --describe false`)
  and check that it doesn't cover the face. When the face is high in frame (seated or mid-shot), move the
  hook onto the chest with `--hook-y 0.43`; the shading follows it automatically.
- Before sending, pull 3–4 frames from `out/captions/<name>.mp4` and look at them. Captions must not
  cover the mouth or eyes. If they do, rebuild with `--cap-y` (higher number = lower on screen).
- Footage filmed sideways (a camera turned on its side, with no rotation metadata) shows the person lying
  on their side in the contact sheet. Rotate it first (`ffmpeg -vf transpose=2` = 90° counter-clockwise, or
  `transpose=1` = clockwise; check one frame) into `videos/_caption-inputs/`, then run `new` on that file.
- Send the MP4 with `SendUserFile`, and give its path as a link.

### 6. Revisions
Settings persist in `videos/captions/<name>/caption.json`, so a revision is just
`build <name> --<option> …` followed by `render <name>`. Common asks:
- **Different style:** `--style`.
- **Bigger or smaller:** `--size 1.2`.
- **Higher or lower:** `--cap-y 0.7`.
- **Fewer words per caption:** `--words 2`.
- **Different colour:** `--accent "#FF4D3D"`.
- **Change the hook:** `--hook`; `--hook ""` removes it.
- **Hook length:** `--hook-dur 3.5`.

They can also open it in HyperFrames Studio themselves with `cd videos/captions/<name> && npm run dev`.

## Setup facts (if something breaks)
- Transcription calls `~/.claude/skills/embedded-captions/scripts/transcribe.cjs` with
  `HYPERFRAMES_ROOT=~/.hyperframes-root`, a HyperFrames CLI 0.8.147 install with a
  `packages/cli/dist/cli.js` symlink. If either is missing, reinstall:
  `npx hyperframes skills update embedded-captions`, then rebuild `~/.hyperframes-root`
  (npm install `hyperframes@0.8.147` and symlink `node_modules/hyperframes/dist/cli.js` to `packages/cli/dist/cli.js`).
- Fonts live in `kit/fonts/` (all SIL OFL) and are copied into each project.
- `setup/doctor.sh` checks every piece below; `setup/setup.sh` repairs them.
- Captions that go *behind* the person are possible with the `/embedded-captions` workflow, but it is
  much slower (about 4 minutes per 10 seconds) and needs `HYPERFRAMES_ROOT` set. Offer it only if asked.
