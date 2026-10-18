# Acknowledgments & third-party notices

Video Studio stands on these projects. None of their code is bundled in this repo; `setup/setup.sh` installs
each one from its official source, under its own license.

| Project | Role | License |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen | ★ Core engine: composition, lint/check, render, TTS, transcription | see repo |
| [GSAP](https://gsap.com) | Timelines inside every composition | GSAP standard license (free) |
| [huashu-art-motion](https://github.com/alchaincyf/huashu-art-motion) by 花叔 | Painterly / explainer canvas engine (art-styles examples) | MIT |
| [motion-prompt](https://github.com/showheyohtaki/motion-prompt) by Shohei Ohtaki | Library of 120 named motion moves | MIT |
| [motion-graphics-music-video-skill](https://github.com/makevoid/motion-graphics-music-video-skill) by makevoid | Fal music-video plugin | see repo |
| [claude-animation-skill](https://github.com/buildwithhanif/claude-animation-skill) | Hand-drawn 2D animation plugin | see repo |
| [Arcads skills](https://github.com/arcads-ai/skills) | Ad research / hook cloning plugin | see repo |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) / Kokoro-82M | Offline text-to-speech | MIT / Apache-2.0 |
| [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) | Voice noise removal | MIT / Apache-2.0 |
| [WhisperX](https://github.com/m-bain/whisperX) | Word-level transcription | BSD-2-Clause |
| [librosa](https://librosa.org) · NumPy · SciPy · OpenCV | Beat detection, synthesis, tracking | ISC / BSD / Apache-2.0 |
| [FFmpeg](https://ffmpeg.org) · [ImageMagick](https://imagemagick.org) | Conform, mix, finishing | LGPL/GPL · ImageMagick |

**Bundled fonts** (`.claude/skills/caption-video/kit/fonts/`, `examples/the-brief/reel/assets/fonts/`): Anton,
Bebas Neue, Inter, Montserrat, Oswald, Playfair Display, Space Grotesk, Instrument Serif. All are licensed
under the SIL Open Font License 1.1.

**Example films** in `examples/` are original works made with code. The art examples' film definitions call
huashu-art-motion's built-in painting scenes.

Video Studio is an independent project. It is not affiliated with Anthropic, HeyGen or any tool listed here.
