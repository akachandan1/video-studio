# Video Studio

A Claude Code studio for making videos — launch films, chop-cut reels, UGC ads, product demos, art-style
explainers, captions and original music. **HyperFrames is the core engine**: every video is a HyperFrames
project (HTML + GSAP, rendered with `npx hyperframes`). Other tools make assets that HyperFrames assembles.

## On every new session
1. A session-start hook runs `setup/doctor.sh --quiet`; its result is above this file in context. If it says
   required tools are missing, tell the user in one plain sentence and offer to run `setup/setup.sh`
   (macOS, ~10 min, idempotent). Never edit `~/.zshrc` without asking (that's the `--add-path` flag).
2. The user may know nothing about video tooling. Don't lead with skill names or jargon. Load the **`studio`**
   skill and follow it: offer the hello-world proof render to first-timers, then ask what they want to make.

## Where things go
- `videos/<name>/` — one HyperFrames project per job (gitignored). Start from `templates/` when one fits.
- `out/` — finished MP4s (gitignored).
- `.claude/skills/` — studio workflows (auto-loaded): studio, chop-reel, launch-film, ugc-ads, ugc-actor,
  product-demo, art-styles, score, caption-video.
- `docs/PLAYBOOK.md` — house rules (read once per session). `docs/CATALOG.md` — every tool, cost, source.
  `docs/SECRETS.md` — how each person connects their own accounts.
- `setup/` — `setup.sh`, `doctor.sh`, `versions.env` (pinned HyperFrames version).

## Rules
- Use `npx --yes hyperframes@<HYPERFRAMES_VERSION from setup/versions.env>` for every HyperFrames command.
- Lint → check → snapshot and look → render → loudnorm −14 LUFS → look at frames → send.
- Quote cost and wait for a yes before any paid generation (Higgsfield, Fal, ElevenLabs).
- Never commit client footage, renders, brand assets, transcripts or keys. Reusable code goes into a skill or
  template with placeholders. Don't push to any remote unless the user explicitly asks.
- Python: use `.venv/bin/python` (numpy, scipy, soundfile, opencv, librosa). Kokoro: `~/.local/share/hf-kokoro/bin/python`.
