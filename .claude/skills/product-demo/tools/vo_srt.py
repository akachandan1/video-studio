# Offline voiceover from a timed script (.srt) with Kokoro — one WAV per subtitle block, each fitted to its slot.
#   python3 vo_srt.py <script.srt> <out_dir> [--voice af_heart] [--fix pronounce.json]
# Writes <out_dir>/01.wav … and <out_dir>/vo.json [{i, start, end, dur, speed, text}] for mix.py.
# Lines that run long are re-spoken faster (max 1.18x); anything still long is reported so the script can be trimmed.
# pronounce.json: {"API": "A P I", "SaaS": "sass", ...} — spell acronyms/brands the way they should be SAID.
# Run with the Kokoro venv python that setup.sh creates:  ~/.local/share/hf-kokoro/bin/python vo_srt.py …
# Voices: af_heart (warm female, default), am_michael, bm_george (British male), bf_emma … see Kokoro docs.
import argparse, json, os, re, soundfile as sf
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser(); ap.add_argument('srt'); ap.add_argument('out')
ap.add_argument('--voice', default='af_heart'); ap.add_argument('--fix', default='')
A = ap.parse_args()
MODELS = os.path.expanduser(os.environ.get('KOKORO_MODELS', '~/.cache/kokoro'))
K = Kokoro(os.path.join(MODELS, 'kokoro-v1.0.onnx'), os.path.join(MODELS, 'voices-v1.0.bin'))
fix = json.load(open(A.fix)) if A.fix else {}
os.makedirs(A.out, exist_ok=True)

def ts(s):
    h, m, r = s.strip().split(':'); s2, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(s2) + int(ms) / 1000

blocks = [b for b in open(A.srt, encoding='utf-8-sig').read().strip().split('\n\n') if '-->' in b]
out = []; long_lines = []
for i, b in enumerate(blocks):
    L = b.strip().split('\n'); k = next(j for j, l in enumerate(L) if '-->' in l)
    a, z = L[k].split(' --> '); text = ' '.join(L[k + 1:]); spoken = text
    for w, say in sorted(fix.items(), key=lambda kv: -len(kv[0])):
        spoken = re.sub(r'(?<![\w])' + re.escape(w) + r'(?![\w])', say, spoken)
    win = ts(z) - ts(a); speed = 1.0
    for _ in range(4):
        y, sr = K.create(spoken, voice=A.voice, speed=speed, lang='en-us')
        d = len(y) / sr
        if d <= win - 0.35 or speed >= 1.18: break
        speed = round(min(1.18, speed * (d / (win - 0.4))), 3)
    if d > win: long_lines.append((i + 1, round(d - win, 2)))
    sf.write(os.path.join(A.out, f'{i + 1:02d}.wav'), y, sr)
    out.append({'i': i + 1, 'start': ts(a), 'end': ts(z), 'dur': round(d, 2), 'speed': speed, 'text': text})
    print(i + 1, f'slot {win:.1f}s', f'spoken {d:.2f}s', f'x{speed}', flush=True)
json.dump(out, open(os.path.join(A.out, 'vo.json'), 'w'), indent=1)
if long_lines: print('OVER SLOT (trim script or let mix.py push later lines):', long_lines)
