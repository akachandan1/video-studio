#!/usr/bin/env bash
# Video Studio one-time setup (macOS). Safe to re-run: every step skips what's already installed.
#
#   setup/setup.sh                 install everything required + recommended
#   setup/setup.sh --only <step>   run one step: brew | hyperframes | skills | plugins | python | voice | denoise | transcribe | browsers
#   setup/setup.sh --add-path      also append the Homebrew Ruby PATH line to ~/.zshrc (needed by the Fal music-video plugin)
#
# It never stores keys, never pushes anything, and installs third-party skills from their official repos.
set -uo pipefail
cd "$(dirname "$0")/.."
STUDIO="$PWD"
source setup/versions.env
ONLY=""; ADD_PATH=0
while [ $# -gt 0 ]; do case "$1" in --only) ONLY="$2"; shift ;; --add-path) ADD_PATH=1 ;; *) echo "unknown option $1"; exit 2 ;; esac; shift; done
want() { [ -z "$ONLY" ] || [ "$ONLY" = "$1" ]; }
say() { printf '\n\033[1m▸ %s\033[0m\n' "$*"; }
ok() { printf '  ✓ %s\n' "$*"; }
warn() { printf '  ! %s\n' "$*"; }
FAILED=()
step() { "$@" || FAILED+=("$1"); }

[ "$(uname)" = "Darwin" ] || { echo "setup.sh supports macOS only for now (see docs/CATALOG.md for manual installs)."; exit 1; }

# ---------------------------------------------------------------- 1. Homebrew packages
s_brew() {
  say "System tools (Homebrew): node, ffmpeg, imagemagick, ruby, uv, python"
  if ! command -v brew >/dev/null; then
    warn "Homebrew is not installed. It needs your password, so run this yourself in Terminal, then re-run setup:"
    echo '    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    return 1
  fi
  for p in node ffmpeg imagemagick ruby uv python@3.12; do
    if brew list --formula "$p" >/dev/null 2>&1; then ok "$p"; else brew install "$p" && ok "$p installed"; fi
  done
  local nv; nv=$(node -v | sed 's/v\([0-9]*\).*/\1/')
  [ "$nv" -ge "$NODE_MIN" ] && ok "node $(node -v)" || { warn "node $(node -v) < $NODE_MIN — run: brew upgrade node"; return 1; }
}

# ---------------------------------------------------------------- 2. HyperFrames (the core)
s_hyperframes() {
  say "HyperFrames CLI $HYPERFRAMES_VERSION (core engine) + its skills"
  npx --yes "hyperframes@$HYPERFRAMES_VERSION" --version >/dev/null && ok "hyperframes@$HYPERFRAMES_VERSION runs" || return 1
  # installs the core HyperFrames + GSAP skills and the workflow skills (faceless-explainer, product-launch-video,
  # talking-head-recut, music-to-video, slideshow, embedded-captions, media-use, …) for Claude Code
  npx --yes "hyperframes@$HYPERFRAMES_VERSION" skills update hyperframes hyperframes-cli hyperframes-core hyperframes-animation \
    hyperframes-audio hyperframes-creative hyperframes-keyframes hyperframes-registry hyperframes-studio \
    embedded-captions faceless-explainer general-video media-use motion-graphics music-to-video pr-to-video \
    product-launch-video slideshow talking-head-recut figma </dev/null && ok "HyperFrames skills installed/updated"
  npx --yes "hyperframes@$HYPERFRAMES_VERSION" doctor </dev/null | tail -15
}

# ---------------------------------------------------------------- 3. Third-party skills (official sources)
s_skills() {
  say "Third-party skills: huashu-art-motion, motion-prompt"
  for repo in alchaincyf/huashu-art-motion showheyohtaki/motion-prompt; do
    name=${repo#*/}
    if [ -f "$HOME/.claude/skills/$name/SKILL.md" ]; then ok "$name (already installed)"
    else npx --yes skills add "$repo" -g -y </dev/null && ok "$name installed" || warn "$name failed — try: npx skills add $repo"; fi
  done
}

# ---------------------------------------------------------------- 4. Claude Code plugins
s_plugins() {
  say "Claude Code plugins: Fal music-video, hand-drawn animation, Arcads ad research"
  command -v claude >/dev/null || { warn "claude CLI not found — install Claude Code first (https://claude.com/claude-code)"; return 1; }
  add() { # marketplace-source marketplace-name plugin
    claude plugin marketplace list 2>/dev/null | grep -q "$2" || claude plugin marketplace add "$1" </dev/null
    if claude plugin list 2>/dev/null | grep -q "$3@$2"; then ok "$3 (already installed)"
    else claude plugin install "$3@$2" </dev/null && ok "$3 installed" || warn "$3 failed — install from the app's plugin browser"; fi
  }
  add makevoid/motion-graphics-music-video-skill makevoid-music-video motion-graphics-music-video
  add buildwithhanif/claude-animation-skill claude-animation-skill claude-animation
  add https://github.com/arcads-ai/skills.git arcads arcads
  if [ $ADD_PATH = 1 ] && ! grep -q 'opt/ruby/bin' "$HOME/.zshrc" 2>/dev/null; then
    echo 'export PATH="/opt/homebrew/opt/ruby/bin:$PATH"' >> "$HOME/.zshrc" && ok "Ruby PATH line added to ~/.zshrc (restart the Claude app)"
  elif ! grep -q 'opt/ruby/bin' "$HOME/.zshrc" 2>/dev/null; then
    warn "The music-video plugin needs Homebrew Ruby on PATH. Re-run with --add-path (or add it yourself):"
    echo '    export PATH="/opt/homebrew/opt/ruby/bin:$PATH"'
  fi
  warn "Fal key: run  claude plugin configure motion-graphics-music-video@makevoid-music-video  (see docs/SECRETS.md)"
}

# ---------------------------------------------------------------- 5. Studio Python env
s_python() {
  say "Studio Python env (.venv): numpy, scipy, soundfile, opencv, librosa"
  [ -x .venv/bin/python ] || uv venv .venv --python 3.12 -q
  uv pip install -q --python .venv/bin/python numpy scipy soundfile opencv-python-headless librosa && ok ".venv ready"
}

# ---------------------------------------------------------------- 6. Offline voice (Kokoro)
s_voice() {
  say "Offline voiceover: Kokoro TTS"
  local V="$HOME/.local/share/hf-kokoro" M="$HOME/.cache/kokoro"
  [ -x "$V/bin/python" ] || uv venv "$V" --python 3.12 -q
  uv pip install -q --python "$V/bin/python" kokoro-onnx soundfile && ok "kokoro venv ($V)"
  mkdir -p "$M"
  for f in kokoro-v1.0.onnx voices-v1.0.bin; do
    [ -s "$M/$f" ] && ok "$f" || { curl -fL --progress-bar -o "$M/$f" "$KOKORO_MODELS_URL/$f" && ok "$f downloaded"; }
  done
  ok "HyperFrames TTS: HYPERFRAMES_PYTHON=$V/bin/python npx hyperframes tts \"Hello\" -v af_heart"
}

# ---------------------------------------------------------------- 7. Voice cleanup (DeepFilterNet)
s_denoise() {
  say "Voice cleanup: DeepFilterNet (own venv, needs numpy<2)"
  local D="$HOME/.venvs/dfn"
  [ -x "$D/bin/deepFilter" ] && { ok "deepFilter (already installed)"; return 0; }
  uv venv "$D" --python 3.11 -q
  uv pip install -q --python "$D/bin/python" "numpy<2" torch==2.2.2 torchaudio==2.2.2 deepfilternet && ok "deepFilter ready"
}

# ---------------------------------------------------------------- 8. Word-level transcription (caption kit)
s_transcribe() {
  say "Transcription layout for the caption kit (WhisperX via uvx, HyperFrames $HF_TRANSCRIBE_VERSION)"
  local R="$HOME/.hyperframes-root"
  mkdir -p "$R/packages/cli/dist"
  [ -f "$R/package.json" ] || echo "{\"name\":\"hf-root\",\"private\":true,\"dependencies\":{\"hyperframes\":\"$HF_TRANSCRIBE_VERSION\"}}" > "$R/package.json"
  (cd "$R" && npm install --silent --no-audit --no-fund) && ln -sf "$R/node_modules/hyperframes/dist/cli.js" "$R/packages/cli/dist/cli.js" && ok "~/.hyperframes-root"
  [ -f "$HOME/.claude/skills/embedded-captions/scripts/transcribe.cjs" ] && ok "embedded-captions transcriber" || warn "run: setup/setup.sh --only hyperframes"
}

# ---------------------------------------------------------------- 9. Browsers for canvas engines
s_browsers() {
  say "Headless Chromium for huashu-art-motion renders (Playwright)"
  uv run -q --with playwright python -m playwright install chromium && ok "playwright chromium"
}

want brew && step s_brew
want hyperframes && step s_hyperframes
want skills && step s_skills
want plugins && step s_plugins
want python && step s_python
want voice && step s_voice
want denoise && step s_denoise
want transcribe && step s_transcribe
want browsers && step s_browsers

echo
if [ ${#FAILED[@]} -eq 0 ]; then echo "Setup finished. Checking…"; else echo "Finished with problems in: ${FAILED[*]}"; fi
bash setup/doctor.sh
