# Acknowledgments

Video Studio stands on the work of these projects and people. Unless noted, **nothing below is bundled**:
`setup/setup.sh` installs each from its official source under its own license. Material that *is* included
here (adapted code, ported specs, fonts) is listed with full license texts in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Core
| Project | Role | License |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen | ★ The core engine: compositions, lint/check, snapshots, render, TTS, transcription, background removal, and its Claude Code skills | see repo |
| [GSAP](https://gsap.com) by GreenSock (Webflow) | Animation timelines in every composition (loaded from jsDelivr) | GSAP Standard License (free) |
| [Claude Code](https://claude.com/claude-code) by Anthropic | The agent that runs the studio | Anthropic terms |

## Creative engines & skills
| Project | Role | License | Bundled? |
|---|---|---|---|
| [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) by alchaincyf (花叔) | Painterly / explainer canvas engine | MIT | Two adapted film files in `examples/` (notice included) |
| [motion-prompt](https://github.com/showheyohtaki/motion-prompt) by Shohei Ohtaki | 120 named motion moves with exact specs | MIT | Moves ported into `examples/the-brief` and `templates/chop-reel` (attribution lines + notice included) |
| [motion-graphics-music-video-skill](https://github.com/makevoid/motion-graphics-music-video-skill) by makevoid | Music-video plugin (Fal) | see repo | no |
| [claude-animation-skill](https://github.com/buildwithhanif/claude-animation-skill) by buildwithhanif | Hand-drawn 2D animation plugin | see repo | no |
| [Arcads skills](https://github.com/arcads-ai/skills) by Arcads | Ad research / hook cloning plugin | see repo | no |
| [skills CLI](https://github.com/vercel-labs/skills) (`npx skills`) | Installs third-party skills | see repo | no |
| [Remotion skills](https://github.com/remotion-dev/skills) | Listed as an alternative engine in the catalog | see repo | no |

## Audio, voice, speech
| Project | Role | License |
|---|---|---|
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad · [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) by thewh1teagle | Offline text-to-speech (model files downloaded by setup) | Apache-2.0 / MIT |
| [edge-tts](https://github.com/rany2/edge-tts) by rany2 | Optional online narration with Microsoft neural voices (text is sent to Microsoft's service) | LGPL-3.0 / GPL-3.0 |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) by Microsoft | Runs the Kokoro model | MIT |
| [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) by Hendrik Schröter | Voice noise removal | MIT / Apache-2.0 |
| [PyTorch](https://pytorch.org) | DeepFilterNet runtime | BSD-3-Clause |
| [WhisperX](https://github.com/m-bain/whisperX) by Max Bain · [OpenAI Whisper](https://github.com/openai/whisper) | Word-level transcription | BSD-2-Clause / MIT |
| [librosa](https://librosa.org) | Beat detection (`beats.py`) | ISC |
| [python-soundfile](https://github.com/bastibe/python-soundfile) | WAV I/O | BSD-3-Clause |

## Foundations
| Project | Role | License |
|---|---|---|
| [NumPy](https://numpy.org) · [SciPy](https://scipy.org) | Synthesis (`synth.py`), DSP, mixing | BSD-3-Clause |
| [OpenCV](https://opencv.org) | Cursor/click tracking (`product-demo`) | Apache-2.0 |
| [FFmpeg](https://ffmpeg.org) | Conform, crop, loudness, contact sheets, GIFs | LGPL / GPL |
| [ImageMagick](https://imagemagick.org) | Stills and image prep | ImageMagick License |
| [Playwright](https://playwright.dev) by Microsoft | Headless Chromium for huashu renders | Apache-2.0 |
| [Node.js](https://nodejs.org) · [uv](https://github.com/astral-sh/uv) by Astral · [Homebrew](https://brew.sh) | Runtimes and installers | MIT / MIT-Apache-2.0 / BSD-2-Clause |

## Fonts
- **Bundled** (SIL OFL 1.1): Anton, Bebas Neue, Inter, Montserrat, Oswald, Playfair Display, Space Grotesk,
  Instrument Serif. Designers and the license are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- **Loaded from [Google Fonts](https://fonts.google.com) at render time** (SIL OFL 1.1): Archivo Black (Omnibus-Type),
  Space Mono (Colophon), Poppins (Indian Type Foundry), Inter.

## Services (optional, each user's own account)
Higgsfield, Fal, ElevenLabs, Apify and Topaz Video are third-party commercial services or apps, used under
their own terms. Their names are trademarks of their respective owners. Video Studio only calls them when you
ask, after quoting the cost.

## Inspiration
- The caption kit's default "Lime Hook" look is a code rebuild of the style of a popular *Captions and Hooks*
  After Effects template. No template files or assets are used.
- Editing grammar (chop cuts, punch-ins, flash frames) follows common short-form editing practice, as seen in apps like CapCut.
- The `explainer` workflow's editorial-collage look is an homage to the visual language of Vox explainer videos;
  it uses no Vox assets, name or branding and is not affiliated with Vox Media. Its staged, app-like guided flow
  was inspired by a community "Vox Animation" studio-folder concept; the workflow, style guide and tools here are
  written from scratch.
- Explainer and art examples are homages to the Kurzgesagt visual style and to the painters and traditions they
  name. They are original works, not affiliated with or endorsed by Kurzgesagt.
- Community files: Code of Conduct based on the [Contributor Covenant](https://www.contributor-covenant.org);
  badges by [shields.io](https://shields.io).

---

Video Studio is an independent open-source project. It is not affiliated with, sponsored by, or endorsed by
Anthropic, HeyGen, or any project, company or service listed here. All trademarks belong to their owners.
