# Product-demo director: tracked clicks + VO script -> HyperFrames index.html with an auto camera.
#   python3 director.py demo.json            (run inside the project folder)
#
# Camera: rests on the "reading" framing, eases in (power3.inOut, TR s) to each cluster of reliable clicks,
# holds while the user works there, returns to rest when there's a gap. Manual FOCUS windows win over clicks.
# Also: click ripples, optional spotlights, chapter cards + pill, stat callouts timed to VO phrases,
# and sentence captions from the VO text. Audio comes from mix.py (assets/mix.wav).
#
# demo.json (all keys except the first block optional):
# {
#   "video": "assets/demo.mp4",  "content": [W, H],  "src_dur": 312.4,      # cropped recording + its size/length
#   "events": "work/events.json", "vo": "vo/vo.json",
#   "intro": 4.0, "tail": 4.0, "tr": 0.75, "min_still": 0.25,
#   "title": "Acme — product walkthrough", "accent": "#f47a2a",
#   "brand": "Acme", "brand_line": "Work, simplified", "product": "Acme Board", "tagline": "...", "url": "acme.com",
#   "chips": ["Boards", "Docs", "Automations"],
#   "reading": [cx, cy, zoom],                      # default framing between clicks (content coords); default = full
#   "sidebar_x": 300,                               # clicks left of this = navigation -> brief, tighter hold
#   "chapters": [[vo_block, "01", "Title", "Subtitle"], ...],
#   "callouts": [[vo_block, "phrase in that line", "BIG", "label", hold_s], ...],
#   "focus":    [[t0, t1, x0, y0, x1, y1, spotlight_bool], ...]   # recording seconds + content box
# }
import json, re, sys, os

C = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'demo.json'))
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = C['content']; SW, SH = 1920, 1080
INTRO, TAIL, TR = C.get('intro', 4.0), C.get('tail', 4.0), C.get('tr', 0.75)
SRC_DUR = C['src_dur']; TOTAL = round(INTRO + SRC_DUR + TAIL, 3)
S0 = min(1760 / W, 990 / H)                   # rest scale: the window floats on the stage with a margin
r = lambda x: round(float(x), 3)

ev = json.load(open(C['events']))['events'] if C.get('events') else []
vo = json.load(open(C['vo'])) if C.get('vo') and os.path.exists(C['vo']) else []

prev_end = -1                                  # same push-back rule as mix.py
for v in vo:
    v['at'] = max(v['start'], prev_end + 0.3); prev_end = v['at'] + v['dur']
V = {v['i']: v for v in vo}

def say(i, phrase=None):
    """composition time when VO block i says `phrase` (character-proportional estimate)."""
    v = V[i]; frac = 0
    if phrase:
        k = v['text'].find(phrase); assert k >= 0, f'phrase not in block {i}: {phrase!r}'
        frac = k / len(v['text'])
    return INTRO + v['at'] + v['dur'] * frac

def clamp_center(cx, cy, z):
    s = S0 * z; hx, hy = SW / 2 / s, SH / 2 / s
    cx = W / 2 if hx >= W / 2 else min(max(cx, hx), W - hx)
    cy = H / 2 if hy >= H / 2 else min(max(cy, hy), H - hy)
    return cx, cy

def fit_zoom(x0, y0, x1, y1, pad=1.18, zmax=2.1):
    w, h = max(1, (x1 - x0) * pad), max(1, (y1 - y0) * pad)
    return max(1.0, min(zmax, SW / (S0 * w), SH / (S0 * h)))

# ---------- click clusters -> holds ----------
min_still = C.get('min_still', 0.25); side_x = C.get('sidebar_x', 0)
clicks = [e for e in ev if e['kind'] == 'click' and e.get('still', 1) >= min_still and 3.0 < e['t'] < SRC_DUR - 1]
segs = []
for c in clicks:
    if segs and c['t'] - segs[-1]['t1'] < 2.6 and abs(c['x'] - segs[-1]['cx']) < W / 3 and abs(c['y'] - segs[-1]['cy']) < H * 0.4:
        s = segs[-1]; s['pts'].append(c); s['t1'] = c['t']
        s['cx'] = sum(p['x'] for p in s['pts']) / len(s['pts']); s['cy'] = sum(p['y'] for p in s['pts']) / len(s['pts'])
    else:
        segs.append({'t0': c['t'], 't1': c['t'], 'cx': c['x'], 'cy': c['y'], 'pts': [c]})
holds = []
for s in segs:
    xs = [p['x'] for p in s['pts']]; ys = [p['y'] for p in s['pts']]
    nav = side_x and all(x < side_x for x in xs)
    z = 1.75 if nav else max(1.6, fit_zoom(min(xs) - W * .17, min(ys) - H * .21, max(xs) + W * .17, max(ys) + H * .21, pad=1.0, zmax=1.9))
    holds.append({'t0': s['t0'] - 0.5, 't1': s['t1'] + (0.55 if nav else 1.9), 'cx': s['cx'], 'cy': s['cy'], 'z': z, 'pri': 1})
FOCUS = C.get('focus', [])
for t0, t1, x0, y0, x1, y1, _ in FOCUS:
    holds.append({'t0': t0, 't1': t1, 'cx': (x0 + x1) / 2, 'cy': (y0 + y1) / 2, 'z': fit_zoom(x0, y0, x1, y1), 'pri': 2})
holds.sort(key=lambda h: h['t0'])
manual = [h for h in holds if h['pri'] == 2]; keep = []
for h in holds:                                # manual focus wins; click holds are trimmed or dropped
    if h['pri'] == 1:
        bad = False
        for m in manual:
            if h['t1'] > m['t0'] - TR and h['t0'] < m['t1'] + TR:
                if h['t0'] < m['t0'] - TR - 1.0: h['t1'] = min(h['t1'], m['t0'] - TR - 0.2)
                else: bad = True
        if bad or h['t1'] - h['t0'] < 0.8: continue
    keep.append(h)
merged = []
for h in sorted(keep, key=lambda h: h['t0']):  # overlapping holds -> pan from one to the next
    if merged and h['t0'] < merged[-1]['t1'] + 0.1:
        p = merged[-1]; h['t0'] = p['t1'] + 0.1
        if h['t1'] - h['t0'] < 0.6:
            if h['pri'] == 1 and p['pri'] == 1: p['t1'] = max(p['t1'], h['t1'])
            continue
    merged.append(h)

REST = (W / 2, H / 2, 1.0)
READ = tuple(C.get('reading', REST))
cam = []
def key(t, cx, cy, z):
    cx, cy = clamp_center(cx, cy, z); cam.append((INTRO + t, cx, cy, z))
key(0, *REST); key(0.4, *REST); key(3.2, *READ)
last_t = 0
for i, h in enumerate(merged):
    arrive = max(h['t0'], last_t + TR); prev = cam[-1]
    cam.append((INTRO + arrive - TR, prev[1], prev[2], prev[3]))
    key(arrive, h['cx'], h['cy'], h['z'])
    end = max(h['t1'], arrive + 0.4); key(end, h['cx'], h['cy'], h['z'])
    nxt = merged[i + 1]['t0'] if i + 1 < len(merged) else SRC_DUR
    if nxt - end > TR * 2 + 0.7: key(end + TR, *READ); last_t = end + TR
    else: last_t = end
cam = [c for c in cam if c[0] <= INTRO + SRC_DUR - 4.0]
last = cam[-1]; cam.append((INTRO + SRC_DUR - 4.0, last[1], last[2], last[3])); key(SRC_DUR - 3.1, *REST)
cam.sort(key=lambda c: c[0])
def xf(cx, cy, z):
    s = S0 * z; return r(SW / 2 - cx * s), r(SH / 2 - cy * s), round(s, 5)
def cam_at(t):
    prev = cam[0]
    for c in cam:
        if c[0] > t: return prev
        prev = c
    return prev

# ---------- overlays ----------
ripples = [{'t': r(INTRO + c['t']), 'x': r(c['x']), 'y': r(c['y'])} for c in clicks]
caps = []
for v in vo:
    chunks, cur = [], []
    for w_ in v['text'].split():
        cur.append(w_)
        if len(cur) >= 9 or (len(cur) >= 4 and re.search(r'[.,:;!?]$', w_)): chunks.append(' '.join(cur)); cur = []
    if cur:
        if chunks and len(cur) <= 2: chunks[-1] += ' ' + ' '.join(cur)
        else: chunks.append(' '.join(cur))
    total = sum(len(c) for c in chunks); acc = 0
    for c in chunks:
        t0 = INTRO + v['at'] + v['dur'] * acc / total; acc += len(c)
        caps.append({'t0': r(t0), 't1': r(INTRO + v['at'] + v['dur'] * acc / total + 0.05), 'text': c})
chapters = [{'t': r(say(b) if b > 1 and vo else INTRO + 0.6), 'n': n, 'title': t, 'sub': s} for b, n, t, s in C.get('chapters', [])]
callouts = []
for b, p, big, lab, hold in C.get('callouts', []):
    t = say(b, p); c = cam_at(t + 0.5)
    callouts.append({'t': r(t), 'big': big, 'label': lab, 'hold': hold, 'side': 'left' if c[1] > W * 0.52 and c[3] > 1.4 else 'right'})
spots = [{'t0': r(INTRO + f[0]), 't1': r(INTRO + f[1]), 'x': f[2], 'y': f[3], 'w': f[4] - f[2], 'h': f[5] - f[3]} for f in FOCUS if f[6]]

D = {'cam': [[r(t), *xf(cx, cy, z)] for t, cx, cy, z in cam], 'ripples': ripples, 'caps': caps, 'chapters': chapters,
     'callouts': callouts, 'spots': spots, 'INTRO': INTRO, 'SRC_DUR': SRC_DUR, 'TOTAL': TOTAL, 'W': W, 'H': H,
     'rest': list(xf(*REST))}
os.makedirs('work', exist_ok=True); json.dump(D, open('work/director.json', 'w'), indent=0)

esc = lambda s: str(s).replace('&', '&amp;').replace('<', '&lt;')
html = open(os.path.join(HERE, 'template.html')).read().replace('/*__DATA__*/', 'const D = ' + json.dumps(D) + ';')
for k, v in {'__TOTAL__': TOTAL, '__INTRO__': INTRO, '__SRCDUR__': SRC_DUR, '__W__': W, '__H__': H,
             '__TITLE__': esc(C.get('title', 'Product demo')), '__ACCENT__': C.get('accent', '#f47a2a'),
             '__BRAND__': esc(C.get('brand', '')), '__BRAND_LINE__': esc(C.get('brand_line', '')),
             '__PRODUCT__': esc(C.get('product', 'Product')), '__TAGLINE__': esc(C.get('tagline', '')),
             '__URL__': esc(C.get('url', '')),
             '__CHIPS__': ''.join(f'<div>{esc(c)}</div>' for c in C.get('chips', []))}.items():
    html = html.replace(k, str(v))
html = html.replace('src="assets/demo.mp4"', f'src="{C.get("video", "assets/demo.mp4")}"')
open('index.html', 'w').write(html)
print('holds', len(merged), 'cam keys', len(cam), 'ripples', len(ripples), 'caps', len(caps), 'total', TOTAL)
if vo: print('VO drift max', round(max(v['at'] - v['start'] for v in vo), 2), 's (lines pushed later by overruns)')
