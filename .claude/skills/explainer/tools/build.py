#!/usr/bin/env python3
"""Assemble an explainer project into a HyperFrames composition + audio mix.

  python3 build.py <project_dir> [--aspect 16:9|9:16] [--no-audio]

Inputs (inside the project):
  pack.json            title, aspect, look (collage | diorama), blocks[], sources[]   (see SKILL.md)
  clips/blockNN.mp4    optional AI/footage clip per block; a block WITHOUT a clip gets a code-built collage scene
  voice/blockNN.wav    narration per block (voice.py)
Outputs:
  index.html           1 root composition, N x 10 s exactly
  assets/mix.wav       narration + original score (ducked) + clip ambience, 48 kHz
Then: npx hyperframes lint / check / render, and loudnorm to -14 LUFS (SKILL.md step 9).
"""
import argparse, html, json, os, re, shutil, subprocess, sys

ap = argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--aspect'); ap.add_argument('--no-audio', action='store_true')
A = ap.parse_args()
P = os.path.abspath(A.project); HERE = os.path.dirname(os.path.abspath(__file__))
pack = json.load(open(os.path.join(P, 'pack.json')))
ASPECT = A.aspect or pack.get('aspect', '16:9')
W, H = (1920, 1080) if ASPECT == '16:9' else (1080, 1920)
PORT = H > W; S = min(W, H)
BL = 10.0; blocks = pack['blocks']; N = len(blocks); DUR = BL * N
LOOK = pack.get('look', 'collage')
esc = lambda s: html.escape(str(s))
px = lambda f: f'{round(S * f)}px'

THEMES = {
    'collage': dict(fields=['#F5CD3D', '#F1EADC', '#1E2942', '#E5533D', '#F1EADC', '#2D6B70', '#F5CD3D', '#1E2942'],
                    ink='#141414', paper='#F1EADC', accent='#E5533D', marker='#D92E22', head='Archivo Black', mono='Space Mono'),
    'diorama': dict(fields=['#E6DCC6', '#D9CCB0', '#2A241C', '#E6DCC6', '#CFC0A0', '#2A241C', '#E6DCC6', '#D9CCB0'],
                    ink='#2A241C', paper='#EDE4D0', accent='#C2571A', marker='#C2571A', head='Archivo Black', mono='Space Mono'),
}
T = THEMES[LOOK]
dark = lambda c: c in ('#1E2942', '#2D6B70', '#2A241C')

def big_px(text):
    # one line, never wraps: Archivo Black averages ~0.72 em per character
    room = W * (.84 if PORT else .44)
    return round(min(S * (.2 if PORT else .19), room / max(1, len(str(text))) / .72))

def voice_dur(k):
    f = os.path.join(P, 'voice', f'block{k:02d}.wav')
    if not os.path.exists(f): return None
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout or 0)

def clip_for(k):
    f = os.path.join(P, 'clips', f'block{k:02d}.mp4')
    return f'clips/block{k:02d}.mp4' if os.path.exists(f) else None

# ---------------------------------------------------------------- tower silhouette (simple, original)
TOWER = ('<svg viewBox="0 0 100 200" class="tower"><path d="M49 2h2l2 26 3 40 7 42 13 50 17 38H70c-4-14-11-24-20-24s-16 10-20 24H7l17-38 13-50 7-42 3-40z"/>'
         '<rect x="34" y="108" width="32" height="5"/><rect x="40" y="66" width="20" height="4"/></svg>')

def visual(k, v, field):
    """Inner HTML for the code-built picture of one block."""
    kind = v.get('kind', 'stat'); ink = T['paper'] if dark(field) else T['ink']
    if kind == 'tower':
        ticks = ''.join(f'<i style="bottom:{i * 10}%"></i>' for i in range(11))
        return f'<div class="vis tower-w" style="color:{ink}"><div class="ruler">{ticks}</div>{TOWER}<div class="grow" id="grow{k}"></div></div>'
    if kind == 'lean':
        return f'<div class="vis lean-w" style="color:{ink}"><div class="sun" id="sun{k}"></div><div class="lean" id="lean{k}">{TOWER}</div><div class="ground"></div></div>'
    if kind == 'dots':
        n = v.get('n', 96)
        return f'<div class="vis dots" id="dots{k}">' + ''.join(f'<b style="background:{T["accent"] if i % 17 == 0 else ink}"></b>' for i in range(n)) + '</div>'
    if kind == 'bars':
        vals = v.get('values', [20, 35, 50, 70, 100]); hi = v.get('highlight', len(vals) - 1)
        return f'<div class="vis bars" id="bars{k}">' + ''.join(
            f'<b style="height:{x}%;background:{T["accent"] if i == hi else ink}"></b>' for i, x in enumerate(vals)) + '</div>'
    if kind == 'calendar':
        n = v.get('n', 7)
        return f'<div class="vis cal" id="cal{k}">' + ''.join(
            f'<b style="background:{T["accent"] if i == n - 1 else "transparent"};border-color:{ink}"></b>' for i in range(n)) + '</div>'
    return '<div class="vis"></div>'

# ---------------------------------------------------------------- captions: <= 5 words, timed by characters
def caption_chunks(line, t0, d):
    words = line.split(); chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 5 or (len(cur) >= 3 and re.search(r'[.,;:!?]$', w)): chunks.append(' '.join(cur)); cur = []
    if cur:
        if chunks and len(cur) <= 1: chunks[-1] += ' ' + cur[0]
        else: chunks.append(' '.join(cur))
    total = sum(len(c) for c in chunks); acc = 0; out = []
    for c in chunks:
        a = t0 + d * acc / total; acc += len(c); out.append((round(a, 3), round(t0 + d * acc / total, 3), c))
    return out

# ---------------------------------------------------------------- composition
els, js = [], []
for k, b in enumerate(blocks, 1):
    t0 = (k - 1) * BL; field = T['fields'][(k - 1) % len(T['fields'])]; fg = T['paper'] if dark(field) else T['ink']
    clip = clip_for(k); co = b.get('callout') or {}
    if clip:
        els.append(f'<video id="v{k}" class="clip vid" src="{clip}" data-start="{t0}" data-duration="{BL}" data-track-index="1" muted playsinline></video>')
        js.append(f'tl.fromTo("#v{k}", {{scale: 1.12, filter: "blur(14px)"}}, {{scale: 1, filter: "blur(0px)", duration: .45, ease: "expo.out", immediateRender: false}}, {t0});')
        if co:
            els.append(f'<div id="co{k}" class="clip callout" data-start="{t0}" data-duration="{BL}" data-track-index="5"><span class="tape"></span>'
                       f'<div class="big"><span id="cn{k}">{esc(co.get("big", ""))}</span></div><div class="lab">{esc(co.get("label", ""))}</div></div>')
            js.append(f'tl.fromTo("#co{k}", {{opacity: 0, y: {S * .04}, rotate: -4}}, {{opacity: 1, y: 0, rotate: -1.5, duration: .5, ease: "back.out(1.8)"}}, {t0 + 1.4});')
            js.append(f'tl.to("#co{k}", {{opacity: 0, y: -{S * .02}, duration: .35, ease: "power2.in"}}, {t0 + 7.2});')
    else:
        v = b.get('visual', {})
        els.append(f'<div id="s{k}" class="clip scene" data-start="{t0}" data-duration="{BL}" data-track-index="2" style="background:{field};color:{fg}">'
                   f'<div class="cam" id="cam{k}"><div class="txt"><div class="big" style="font-size:{big_px(co.get("big", ""))}px"><span class="bw"><span id="cn{k}">{esc(co.get("big", ""))}</span>'
                   f'<svg class="mark" id="mk{k}" viewBox="0 0 300 120" preserveAspectRatio="none"><path d="M18 64C30 18 150 6 250 22c40 7 42 52 2 72-60 28-190 28-226-6C10 70 30 40 90 30" stroke="{T["ink"] if field == T["accent"] else T["marker"]}"/></svg></span></div>'
                   f'<div class="lab">{esc(co.get("label", ""))}</div></div>'
                   f'{visual(k, v, field)}</div></div>')
        js.append(f'tl.fromTo("#cam{k}", {{x: {S * .22}, filter: "blur(16px)"}}, {{x: 0, filter: "blur(0px)", duration: .5, ease: "expo.out", immediateRender: false}}, {t0});')
        js.append(f'tl.fromTo("#cam{k}", {{scale: 1}}, {{scale: 1.05, duration: {BL - .5}, ease: "none", immediateRender: false}}, {t0 + .5});')
        js.append(f'tl.fromTo("#s{k} .txt", {{opacity: 0, y: {S * .05}}}, {{opacity: 1, y: 0, duration: .55, ease: "back.out(1.6)", immediateRender: false}}, {t0 + .35});')
        js.append(f'tl.fromTo("#mk{k} path", {{strokeDashoffset: 900}}, {{strokeDashoffset: 0, duration: .7, ease: "power2.inOut", immediateRender: false}}, {t0 + 1.6});')
        kind = v.get('kind')
        if kind == 'tower':
            js.append(f'tl.fromTo("#s{k} .tower", {{scaleY: .94}}, {{scaleY: 1.03, duration: 6, ease: "sine.inOut", immediateRender: false}}, {t0 + 1});')
            js.append(f'tl.fromTo("#grow{k}", {{scaleY: 0}}, {{scaleY: 1, duration: 6, ease: "sine.inOut", immediateRender: false}}, {t0 + 1});')
        elif kind == 'lean':
            js.append(f'tl.fromTo("#sun{k}", {{x: -{S * .12}, y: {S * .05}}}, {{x: {S * .12}, y: -{S * .03}, duration: 8, ease: "sine.inOut", immediateRender: false}}, {t0 + 1});')
            js.append(f'tl.fromTo("#lean{k}", {{rotate: 0}}, {{rotate: -3.5, duration: 4, ease: "sine.inOut", immediateRender: false}}, {t0 + 2});')
        elif kind == 'dots':
            js.append(f'tl.fromTo("#dots{k} b", {{scale: 0}}, {{scale: 1, duration: .25, ease: "back.out(3)", stagger: {{each: .035, from: "random"}}, immediateRender: false}}, {t0 + .8});')
        elif kind == 'bars':
            js.append(f'tl.fromTo("#bars{k} b", {{scaleY: 0}}, {{scaleY: 1, duration: .6, ease: "back.out(1.6)", stagger: .18, immediateRender: false}}, {t0 + .9});')
        elif kind == 'calendar':
            js.append(f'tl.fromTo("#cal{k} b", {{opacity: 0, y: {S * .03}}}, {{opacity: 1, y: 0, duration: .3, ease: "power3.out", stagger: .35, immediateRender: false}}, {t0 + .9});')
    # count-up for numeric callouts
    m = re.match(r'^([+\-]?)([\d][\d.,]*)(.*)$', str(co.get('big', '')))
    if m:
        num = m.group(2); dec = len(num.split('.')[1]) if '.' in num else 0; val = float(num.replace(',', ''))
        comma = ',' in num
        js.append(f'(() => {{ const o = {{v: 0}}, el = document.getElementById("cn{k}"); tl.fromTo(o, {{v: 0}}, {{v: {val}, duration: 1.2, ease: "power3.out", immediateRender: false, '
                  f'onUpdate: () => {{ el.textContent = "{m.group(1)}" + o.v.toLocaleString("en-US", {{minimumFractionDigits: {dec}, maximumFractionDigits: {dec}, useGrouping: {str(comma).lower()}}}) + {json.dumps(m.group(3))}; }} }}, {t0 + (1.4 if clip else .4)}); }})();')
    # captions
    d = voice_dur(k) or 9.0
    for i, (a, z, c) in enumerate(caption_chunks(b['line'], t0 + .25, d)):
        cid = f'c{k}_{i}'
        els.append(f'<div id="{cid}" class="clip cap" data-start="{a}" data-duration="{round(max(.2, z - a), 3)}" data-track-index="6"><span>{esc(c)}</span></div>')

title = esc(pack.get('title', 'Explainer'))
audio = '<audio id="mix" src="assets/mix.wav" data-start="0" data-duration="%s" data-track-index="10" data-volume="1"></audio>' % DUR
if A.no_audio and not os.path.exists(os.path.join(P, 'assets', 'mix.wav')): audio = ''   # silent preview build
grain = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' "
         "baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")
txt_w = '86%' if PORT else '46%'
css = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:{T['ink']}; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:{T['ink']}; font-family:"{T['head']}", sans-serif; }}
.vid {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.scene {{ position:absolute; inset:0; overflow:hidden; }}
.cam {{ position:absolute; inset:0; display:flex; flex-direction:{'column' if PORT else 'row'}; align-items:center; justify-content:{'flex-start' if PORT else 'center'}; gap:{px(.06)}; padding:{px(.25) if PORT else px(.08)} {px(.08)} {px(.08)}; }}
.txt {{ position:relative; width:{txt_w}; text-align:{'center' if PORT else 'left'}; }}
.big {{ font-size:{px(.2 if PORT else .19)}; line-height:1; letter-spacing:-.01em; white-space:nowrap; }}
.bw {{ position:relative; display:inline-block; }}
.lab {{ font-family:"{T['mono']}", monospace; font-size:{px(.032)}; letter-spacing:.06em; text-transform:uppercase; margin-top:{px(.03)}; opacity:.85; }}
.mark {{ position:absolute; left:-12%; top:-22%; width:124%; height:140%; overflow:visible; pointer-events:none; }}
.mark path {{ fill:none; stroke-width:5; stroke-linecap:round; stroke-dasharray:900; stroke-dashoffset:900; }}
.vis {{ position:relative; width:{'80%' if PORT else '40%'}; height:{'38%' if PORT else '78%'}; }}
.tower {{ height:100%; width:auto; display:block; margin:0 auto; fill:currentColor; transform-origin:50% 100%; }}
.tower-w .tower {{ position:absolute; left:50%; bottom:0; transform:translateX(-50%); }}
.ruler {{ position:absolute; left:12%; top:0; bottom:0; width:{px(.012)}; border-left:3px solid currentColor; opacity:.6; }}
.ruler i {{ position:absolute; left:0; width:{px(.03)}; border-top:3px solid currentColor; }}
.grow {{ position:absolute; left:12%; top:0; width:{px(.012)}; height:9%; background:{T['accent']}; transform-origin:50% 100%; }}
.lean-w .lean {{ position:absolute; left:50%; bottom:6%; height:88%; transform-origin:50% 100%; translate:-50% 0; }}
.lean-w .lean .tower {{ height:100%; }}
.sun {{ position:absolute; right:12%; top:6%; width:{px(.12)}; height:{px(.12)}; border-radius:50%; background:{T['accent']}; box-shadow:0 0 {px(.08)} {T['accent']}; }}
.ground {{ position:absolute; left:0; right:0; bottom:0; height:6%; border-top:4px solid currentColor; opacity:.5; }}
.dots {{ display:grid; grid-template-columns:repeat(12, 1fr); gap:{px(.012)}; align-content:center; }}
.dots b {{ aspect-ratio:1; border-radius:50%; display:block; }}
.bars {{ display:flex; align-items:flex-end; gap:{px(.02)}; }}
.bars b {{ flex:1; display:block; border-radius:{px(.008)} {px(.008)} 0 0; transform-origin:50% 100%; }}
.cal {{ display:grid; grid-template-columns:repeat(7, 1fr); gap:{px(.015)}; align-content:center; }}
.cal b {{ aspect-ratio:3/4; border:4px solid; border-radius:{px(.01)}; display:block; }}
.callout {{ position:absolute; {'left:8%; right:8%; top:7%' if PORT else 'left:5%; top:8%; max-width:42%'}; background:{T['paper']}; color:{T['ink']}; padding:{px(.03)} {px(.04)};
  box-shadow:0 {px(.02)} {px(.05)} rgba(0,0,0,.35); transform-origin:20% 0; }}
.callout .big {{ font-size:{px(.12)}; }} .callout .lab {{ font-size:{px(.026)}; }}
.tape {{ position:absolute; left:42%; top:{px(-.02)}; width:{px(.14)}; height:{px(.04)}; background:rgba(245,205,61,.75); transform:rotate(-3deg); }}
.cap {{ position:absolute; left:0; right:0; {'top:80%' if PORT else 'bottom:7%'}; text-align:center; }}
.cap span {{ display:inline-block; font-family:Inter, sans-serif; font-weight:800; font-size:{px(.05 if PORT else .042)}; color:#fff; background:{T['ink']};
  padding:{px(.008)} {px(.02)}; border-radius:{px(.006)}; max-width:86%; }}
#grain {{ position:absolute; inset:0; pointer-events:none; background-image:url("{grain}"); opacity:.16; mix-blend-mode:multiply; z-index:20; }}
"""
page = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono:wght@400;700&family=Inter:wght@800&display=block" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{chr(10).join(els)}
<div id="grain" class="clip" data-start="0" data-duration="{DUR}" data-track-index="8"></div>
{audio}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body></html>"""
open(os.path.join(P, 'index.html'), 'w').write(page)
for f in ('hyperframes.json', 'package.json', 'meta.json'):
    src = os.path.join(HERE, '..', '..', '..', '..', 'templates', 'hello-world', f)
    if not os.path.exists(os.path.join(P, f)) and os.path.exists(src): shutil.copy(src, os.path.join(P, f))
print(f'index.html: {N} blocks x {BL:.0f}s = {DUR:.0f}s, {ASPECT}, look={LOOK}, '
      f'{sum(1 for k in range(1, N + 1) if clip_for(k))} clip blocks, {sum(1 for k in range(1, N + 1) if not clip_for(k))} code scenes')

# ---------------------------------------------------------------- audio: narration + original score + ambience
if A.no_audio: sys.exit(0)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'score', 'scripts'))
import numpy as np, soundfile as sf
from synth import SR, Mix, kick, hat, pad, pluck, impact, riser, piano, tick, filt

def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy() if raw else np.zeros((0, 2), np.float32)

n = int(DUR * SR)
# score: 96 BPM so one block = 16 beats exactly; a chord per block, a hit on every block change
bed = Mix(DUR); beat = 60 / 96
CH = ([[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]] if LOOK == 'collage' else [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]])
for k in range(N):
    t0 = k * BL; ch = CH[k % 4]
    bed.add(pad(ch, BL, .07), t0)
    for j in range(16):
        at = t0 + j * beat
        if j % 4 == 0: bed.add(kick(.38), at)
        bed.add(hat(.035), at + beat / 2)
        if j % 4 == 2: bed.add(pluck(ch[j // 4 % 3] + 12, .07) if LOOK == 'collage' else piano(ch[j // 4 % 3] + 12, 1.6, .09), at)
    if k: bed.add(impact(.28), t0); bed.add(riser(.8, .12), t0 - .8)
    bed.add(tick(91, .05), t0 + 1.6)                                   # marker-draw / callout tick
bed.add(pad(CH[0], 2.5, .06), DUR - 2.5)
music = bed.master(room=True, drive=1.2, fade=1.5) * .5

voice = np.zeros((n, 2), np.float32); speech = np.zeros(n, np.float32); amb = np.zeros((n, 2), np.float32)
for k in range(1, N + 1):
    i0 = int(((k - 1) * BL + .25) * SR)
    vf = os.path.join(P, 'voice', f'block{k:02d}.wav')
    if os.path.exists(vf):
        a = load(vf)[: int((BL - .25) * SR)]; voice[i0:i0 + len(a)] += a; speech[i0:i0 + len(a)] = 1
    c = clip_for(k)
    if c:
        a = load(os.path.join(P, c))[: int(BL * SR)]; j0 = int((k - 1) * BL * SR); amb[j0:j0 + len(a)] += a * .22
kk = int(.3 * SR); sm = np.convolve(speech, np.ones(kk) / kk, mode='same')
duck = (10 ** (-9 * np.clip(sm * 1.5, 0, 1) / 20)).astype(np.float32)
mix = voice + music[:n] * duck[:, None] + amb
mix *= min(1.0, .95 / max(1e-9, np.abs(mix).max()))
os.makedirs(os.path.join(P, 'assets'), exist_ok=True)
sf.write(os.path.join(P, 'assets', 'mix.wav'), mix, SR, subtype='PCM_16')
print('assets/mix.wav: narration + score + ambience (loudnorm -14 LUFS after render)')
