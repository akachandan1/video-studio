# Catalog — every tool in the studio

**★ HyperFrames is the core.** Every other tool produces something (a shot, art, a voice, music, captions) that is
assembled, checked and rendered by HyperFrames. Cost: 🟢 free/local · 🟡 paid per use · 🔴 paid app.

## ★ Core: HyperFrames (heygen-com/hyperframes)
HTML + GSAP compositions rendered deterministically to MP4. CLI pinned in `setup/versions.env`.

| Skill / command | Use it for |
|---|---|
| `hyperframes`, `-core`, `-animation`, `-creative`, `-keyframes` | Composition rules, timing, motion, design |
| `hyperframes-cli` | `init`, `lint`, `check`, `snapshot`, `render`, `tts`, `transcribe`, `remove-background`, `beats`, `audio` |
| `hyperframes-registry` | Ready blocks: `npx hyperframes catalog` / `add` (whip-pan-cut, rgb-glitch-text, grain-overlay…) |
| `hyperframes-audio` | Audio carve/measure, place hits on picture |
| `hyperframes-studio` | Visual preview/editor (`npm run dev` in a project) |
| `embedded-captions` | Word-level WhisperX transcription; captions behind the subject |
| `talking-head-recut` | Long talking video → short with graphic overlays |
| `faceless-explainer` | Text/article/topic → explainer video |
| `product-launch-video` | URL/brief → promo video |
| `music-to-video` | Track → music video |
| `slideshow` | Deck → video |
| `general-video`, `motion-graphics`, `media-use`, `pr-to-video`, `figma` | General builds, motion graphics, media sourcing, PR videos, Figma import |

## Studio workflows (this repo, `.claude/skills/`)
| Skill | What | Cost |
|---|---|---|
| `studio` | Front door: setup check, routing, house pipeline | 🟢 |
| `chop-reel` | CapCut-style story reel, 16:9 + 9:16 (template: `templates/chop-reel`) | 🟢 |
| `launch-film` | Apple/OpenAI-style launch film + fold-cut builder | 🟢 / 🟡 AI shots |
| `ugc-ads` | Research → AI presenter → hook × ratio variants | 🟡 |
| `ugc-actor` | Casting profiles + image prompts for AI presenters | 🟢 |
| `product-demo` | Screen recording → auto-camera walkthrough with VO | 🟢 |
| `art-styles` | Painterly / Kurzgesagt animation via huashu → HyperFrames | 🟢 |
| `score` | Synth music + SFX locked to cuts; beat detection | 🟢 |
| `caption-video` | 7 caption styles previewed on footage, hooks, audio polish | 🟢 |

## Creative engines (installed by setup.sh from official repos)
| Tool | Source | What | Cost |
|---|---|---|---|
| huashu-art-motion | alchaincyf/huashu-art-motion | Canvas engine for painterly/science animation (custom scenes) | 🟢 |
| motion-prompt | showheyohtaki/motion-prompt | 120 numbered moves with exact specs; `pick` opens the gallery | 🟢 |
| claude-animation (plugin) | buildwithhanif/claude-animation-skill | Hand-drawn 2D, watercolour/editorial looks | 🟢 |
| motion-graphics-music-video (plugin) | makevoid/motion-graphics-music-video-skill | Track → AI music video via Fal | 🟡 Fal key |
| Arcads (plugin) | arcads-ai/skills | `spy-competitor-ads`, `clone-hook`, `clone-static-ad` | 🟢 / 🟡 |

## Audio & voice
| Tool | What | Cost |
|---|---|---|
| Kokoro (kokoro-onnx) | Offline TTS: `HYPERFRAMES_PYTHON=~/.local/share/hf-kokoro/bin/python npx hyperframes tts "…" -v af_heart` (also `bm_george`, `am_michael`) | 🟢 |
| DeepFilterNet3 | Voice noise removal (`~/.venvs/dfn/bin/deepFilter`) | 🟢 |
| WhisperX (via uvx) | Word-level transcripts for captions | 🟢 |
| librosa (`score/scripts/beats.py`) | Beat grid of a supplied track | 🟢 |
| ElevenLabs via Higgsfield `text2speech_v2` | Premium / cloned / Hindi voices | 🟡 |

## AI generation (connectors — each person connects their own account)
| Connector | Models we use | Typical cost |
|---|---|---|
| Higgsfield | `nano_banana_pro` (accurate people, ~2 cr), `gpt_image_2_5` (~2.75 cr), `soul_2`, `seedream_v5_pro`; video `kling3_0` pro (~7.5 cr / 5 s silent, ~14 cr / 7 s talking), `seedance_2_5` omni_reference (~105–120 cr / 15–20 s talking), `wan2_7` lip-sync (~2.5 cr/s) | 🟡 |
| Apify | `apify/facebook-ads-scraper` for Ad Library research | 🟡 small |

## Finishing
| Tool | What | Cost |
|---|---|---|
| ffmpeg | Conform, crop, loudnorm −14 LUFS, contact sheets | 🟢 |
| ImageMagick | Stills, sheets, image prep | 🟢 |
| Topaz Video | Upscale real footage (not installed by setup) | 🔴 — fallback `ffmpeg -vf scale=iw*2:-2:flags=lanczos` |

## Alternative engine (not installed by default)
**Remotion** (remotion-dev/skills, 12 skills) — React-based video. Install with `npx skills add remotion-dev/skills -g`
only if a project must be Remotion. The studio's workflows, templates and rules assume HyperFrames.
