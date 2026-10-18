# Video Studio — a Claude Code video kit, powered by HyperFrames

> **Open this folder in Claude Code** (desktop app Code tab, or `claude` in a terminal). A claude.ai chat upload
> won't work. New here? Read [START-HERE.md](START-HERE.md) — it's one page.

Describe a video in plain words; Claude plans it, makes the shots, music, voice and captions, and renders it.
**[HyperFrames](https://github.com/heygen-com/hyperframes) is the core**: every video is a HyperFrames
composition (HTML + GSAP), linted, checked and rendered by its CLI. Everything else plugs into it.

```
              ┌──────────── asset makers ────────────┐
 code scenes · Higgsfield AI shots · huashu art · motion-prompt moves
 Kokoro voice · synth score · caption kit · Fal music-video · screen recordings
              └──────────────────┬───────────────────┘
                                 ▼
                    ★ HyperFrames composition ★
                lint → check → snapshot → render → −14 LUFS
                                 ▼
                          out/<video>.mp4
```

## What it makes
| Ask for | Workflow |
|---|---|
| A punchy CapCut-style reel or showreel, 16:9 + 9:16 | `chop-reel` |
| An Apple/OpenAI-style product launch film | `launch-film` |
| UGC ad variants with an AI presenter | `ugc-ads` + `ugc-actor` |
| A product walkthrough from a screen recording | `product-demo` |
| Kurzgesagt-style or painterly animation | `art-styles` |
| Captions + hook + cleaner audio on a talking video | `caption-video` |
| Original music / sound design synced to cuts | `score` |
| Explainers, promos, music videos, slideshows, talking-head recuts | HyperFrames workflow skills |

## Install
```bash
git clone <this repo> video-studio && cd video-studio
setup/setup.sh          # macOS; idempotent; then: setup/doctor.sh
```
Or just open the folder in Claude Code and say hi — it runs the doctor and offers to install what's missing.

Skills in `.claude/skills/` load automatically when Claude Code opens this folder. To use them in *every*
folder, install as a plugin: `claude plugin marketplace add <this repo>` then
`claude plugin install video-studio@video-studio`.

## Layout
```
CLAUDE.md            what Claude reads first (HyperFrames core, first-run steps, rules)
START-HERE.md        one-page guide for humans
.claude/skills/      studio workflows: studio (front door), chop-reel, launch-film, ugc-ads, ugc-actor,
                     product-demo, art-styles, score, caption-video
.claude/settings.json  session-start hook → setup/doctor.sh
templates/           hello-world (proof render), chop-reel (16:9/9:16 engine + score)
setup/               setup.sh, doctor.sh, versions.env (pinned HyperFrames)
docs/                PLAYBOOK.md (house rules), CATALOG.md (every tool), SECRETS.md (accounts)
videos/  out/        your projects and renders (gitignored)
```

## Principles
- HyperFrames first; third-party tools installed from their official sources, never copied in.
- Free by default; paid AI generation only after quoting the cost.
- No client material or keys in the repo. Every job that teaches a new trick feeds back as a skill, template or playbook rule.
