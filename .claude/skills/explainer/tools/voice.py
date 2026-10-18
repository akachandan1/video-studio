#!/usr/bin/env python3
"""Voice every block of an explainer and check each take fits its 10-second slot.

  python3 voice.py <project_dir> [--engine kokoro|edge] [--voice NAME] [--only 3,5]

Reads <project>/pack.json (blocks[].line, voice.engine, voice.name), writes voice/blockNN.wav and
voice/voice.json [{block, dur, ok}]. A take is OK between 7.5 s and 9.7 s; anything outside is listed so the
line can be rewritten (shorter / longer) and re-voiced with --only. Never time-stretch to fix length.

Engines
  kokoro  offline, free (default). Voices: am_michael (US male, documentary), bm_george (British male),
          af_heart (US female), bf_emma (British female), am_adam, af_nova. Runs via the hf-kokoro venv.
  edge    Microsoft neural voices via edge-tts (free, but sends the text to Microsoft's service).
          Voices: en-US-ChristopherNeural, en-GB-RyanNeural, en-US-JennyNeural, en-US-AriaNeural.
"""
import argparse, json, os, shutil, subprocess, sys

MIN_OK, MAX_OK = 7.5, 9.7
ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--engine'); ap.add_argument('--voice')
ap.add_argument('--only', default='')
A = ap.parse_args()
P = os.path.abspath(A.project); pack = json.load(open(os.path.join(P, 'pack.json')))
cfg = pack.get('voice', {}); engine = A.engine or cfg.get('engine', 'kokoro')
name = A.voice or cfg.get('name') or ('am_michael' if engine == 'kokoro' else 'en-US-ChristopherNeural')
only = {int(x) for x in A.only.split(',') if x}
out = os.path.join(P, 'voice'); os.makedirs(out, exist_ok=True)

def dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True, check=True).stdout)

def kokoro(text, path):
    py = os.path.expanduser('~/.local/share/hf-kokoro/bin/python')
    models = os.path.expanduser(os.environ.get('KOKORO_MODELS', '~/.cache/kokoro'))
    code = ("import sys,soundfile as sf\nfrom kokoro_onnx import Kokoro\n"
            f"k=Kokoro({os.path.join(models, 'kokoro-v1.0.onnx')!r},{os.path.join(models, 'voices-v1.0.bin')!r})\n"
            "y,sr=k.create(sys.argv[1],voice=sys.argv[2],speed=1.0,lang='en-gb' if sys.argv[2][0]=='b' else 'en-us')\n"
            "sf.write(sys.argv[3],y,sr)\n")
    subprocess.run([py, '-c', code, text, name, path], check=True)

def edge(text, path):
    exe = shutil.which('edge-tts') or os.path.expanduser('~/.local/bin/edge-tts')
    if not os.path.exists(exe): sys.exit('edge-tts not installed: setup/setup.sh --only voice')
    mp3 = path[:-4] + '.mp3'
    subprocess.run([exe, '--voice', name, '--text', text, '--write-media', mp3], check=True, capture_output=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ar', '48000', path], check=True); os.remove(mp3)

prev = {}
vj = os.path.join(out, 'voice.json')
if os.path.exists(vj): prev = {r['block']: r for r in json.load(open(vj))}
rows = []
for k, b in enumerate(pack['blocks'], 1):
    f = os.path.join(out, f'block{k:02d}.wav')
    if not only or k in only or not os.path.exists(f):
        (kokoro if engine == 'kokoro' else edge)(b['line'], f)
    d = round(dur(f), 2); ok = MIN_OK <= d <= MAX_OK
    rows.append({'block': k, 'dur': d, 'ok': ok, 'words': len(b['line'].split())})
    flag = 'ok' if ok else ('LONG: cut a few words' if d > MAX_OK else 'SHORT: add a few words')
    print(f'block {k:02d}  {d:5.2f}s  {len(b["line"].split()):2d} words  {flag}')
json.dump(rows, open(vj, 'w'), indent=1)
bad = [r['block'] for r in rows if not r['ok']]
print('all takes fit' if not bad else f'rewrite + re-voice blocks {bad}  (python3 voice.py {A.project} --only {",".join(map(str, bad))})')
