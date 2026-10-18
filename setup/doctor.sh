#!/usr/bin/env bash
# Video Studio health check. Prints ✓ / ✗ per tool and the fix for each ✗.
#   setup/doctor.sh           full report
#   setup/doctor.sh --quiet   one summary line + only the problems (used by the session-start hook)
cd "$(dirname "$0")/.."
source setup/versions.env
Q=0; [ "${1:-}" = "--quiet" ] && Q=1
REQ_BAD=0; OPT_BAD=0; LINES=()
chk() { # level name test fix
  if eval "$3" >/dev/null 2>&1; then [ $Q = 1 ] || LINES+=("  ✓ $2")
  else
    if [ "$1" = req ]; then REQ_BAD=$((REQ_BAD + 1)); LINES+=("  ✗ $2  →  $4"); else OPT_BAD=$((OPT_BAD + 1)); LINES+=("  ○ $2 (optional)  →  $4"); fi
  fi
}
H="$HOME/.claude/skills"; A="$HOME/.agents/skills"
has_skill() { [ -f "$H/$1/SKILL.md" ] || [ -f "$A/$1/SKILL.md" ]; }

[ $Q = 1 ] || LINES+=("Core")
chk req "macOS"                       '[ "$(uname)" = Darwin ]'                                  "setup.sh is macOS-only for now"
chk req "Homebrew"                    'command -v brew'                                          "install Homebrew (see setup.sh output)"
chk req "Node ≥ $NODE_MIN"            '[ "$(node -v | sed "s/v\([0-9]*\).*/\1/")" -ge $NODE_MIN ]' "setup/setup.sh --only brew"
chk req "ffmpeg"                      'command -v ffmpeg'                                        "setup/setup.sh --only brew"
chk req "uv (Python runner)"          'command -v uv'                                            "setup/setup.sh --only brew"
chk req "★ HyperFrames CLI $HYPERFRAMES_VERSION" 'npx --no-install hyperframes@$HYPERFRAMES_VERSION --version || ls ~/.npm/_npx/*/node_modules/hyperframes/package.json' "setup/setup.sh --only hyperframes"
chk req "★ HyperFrames skills"        'has_skill hyperframes && has_skill hyperframes-cli'       "setup/setup.sh --only hyperframes"
chk req "Studio Python env (.venv)"   '.venv/bin/python -c "import numpy, scipy, soundfile, cv2, librosa"' "setup/setup.sh --only python"

[ $Q = 1 ] || LINES+=("" "Creative tools")
chk req "huashu-art-motion skill"     'has_skill huashu-art-motion'                              "setup/setup.sh --only skills"
chk req "motion-prompt skill"         'has_skill motion-prompt'                                  "setup/setup.sh --only skills"
chk req "HyperFrames workflow skills" 'has_skill talking-head-recut && has_skill faceless-explainer && has_skill embedded-captions' "setup/setup.sh --only hyperframes"
chk req "Kokoro voice (offline TTS)"  '~/.local/share/hf-kokoro/bin/python -c "import kokoro_onnx" && [ -s ~/.cache/kokoro/kokoro-v1.0.onnx ]' "setup/setup.sh --only voice"
chk req "Caption transcriber"         '[ -e ~/.hyperframes-root/packages/cli/dist/cli.js ] && [ -f ~/.claude/skills/embedded-captions/scripts/transcribe.cjs ]' "setup/setup.sh --only transcribe"
chk req "DeepFilterNet (voice cleanup)" '[ -x ~/.venvs/dfn/bin/deepFilter ]'                     "setup/setup.sh --only denoise"
chk req "ImageMagick"                 'command -v magick || command -v convert'                  "setup/setup.sh --only brew"
chk req "Playwright Chromium (huashu)" 'ls ~/Library/Caches/ms-playwright | grep -q chromium'    "setup/setup.sh --only browsers"

[ $Q = 1 ] || LINES+=("" "Optional (only needed by some workflows)")
chk opt "Fal music-video plugin"      'claude plugin list 2>/dev/null | grep -q motion-graphics-music-video' "setup/setup.sh --only plugins"
chk opt "Homebrew Ruby on PATH (plugin)" 'ruby -e "exit(RUBY_VERSION.to_i >= 3 ? 0 : 1)"'        "setup/setup.sh --only plugins --add-path, then restart the app"
chk opt "claude-animation plugin"     'claude plugin list 2>/dev/null | grep -q claude-animation' "setup/setup.sh --only plugins"
chk opt "Arcads plugin (ad research)" 'claude plugin list 2>/dev/null | grep -q "arcads@"'        "setup/setup.sh --only plugins"
chk opt "edge-tts (online neural voices)" 'command -v edge-tts || [ -x ~/.local/bin/edge-tts ]' "setup/setup.sh --only voice"
chk opt "Topaz Video (upscale)"       'ls -d /Applications/Topaz\ Video*.app'                    "paid app, install yourself; fallback: ffmpeg scale=lanczos"

if [ $Q = 1 ]; then
  if [ $REQ_BAD = 0 ]; then echo "Video Studio: setup OK (HyperFrames $HYPERFRAMES_VERSION)${OPT_BAD:+; $OPT_BAD optional tool(s) missing}"
  else echo "Video Studio: $REQ_BAD required tool(s) missing — offer to run setup/setup.sh"; fi
  printf '%s\n' "${LINES[@]}" | grep '✗' || true
else
  echo "Video Studio doctor"; printf '%s\n' "${LINES[@]}"
  echo; echo "Connectors (check inside Claude, not from the shell): Higgsfield (AI image/video), Apify (ad research)."
  [ $REQ_BAD = 0 ] && echo "Required: all good." || echo "Required: $REQ_BAD missing — run setup/setup.sh"
fi
exit 0
