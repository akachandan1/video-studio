"""Fold-cut launch film builder: python3 build.py  ->  index.html (from src/template.html).

Put 11 clips in assets/clips/c01.mp4 … c11.mp4 (AI shots from Higgsfield, product renders, or footage)
and a score at assets/audio/score.wav (see the score skill: examples/launch_piano_120bpm_40s.py has the
matching fold "clack" cues). Then edit SHOTS / SUPERS below, run this, and `npx hyperframes check`.

Every shot is split into two half-frame <video> copies so any cut can become a
"fold": the outgoing shot's halves hinge shut onto the centre line (landing on
the score's magnetic clack), or the incoming shot's halves unfold open.
Timing constants here mirror assets/audio/score.py (FOLDS, UNFOLD).
"""
import json
from pathlib import Path

FOLD_DUR = 0.5    # fold completes exactly on its cue time
UNFOLD_DUR = 0.55

# id, clip, start, end, media_start, playback_rate, transition_in
SHOTS = [
    ("s1", "c01", 0.0, 4.0, 0.4, 1.0, "fade"),
    ("s2", "c02", 4.0, 8.0, 0.0, 0.8, "cut"),
    ("s3", "c03", 8.0, 12.0 + UNFOLD_DUR, 0.0, 0.75, "cut"),
    ("s4", "c04", 12.0, 15.0, 0.0, 0.3, "unfold"),
    ("s5", "c05", 15.0 - FOLD_DUR, 18.0, 1.0, 1.0, "fold"),
    ("s6", "c09", 18.0, 21.0, 1.0, 1.0, "cut"),
    ("s7", "c06", 21.0 - FOLD_DUR, 24.0, 1.0, 1.0, "fold"),
    ("s8", "c07", 24.0, 27.0, 1.2, 1.0, "cut"),
    ("s9", "c08", 27.0 - FOLD_DUR, 30.0, 1.0, 1.0, "fold"),
    ("s10", "c10", 30.0 - FOLD_DUR, 33.0, 0.0, 1.0, "fold"),
    ("s11", "c11", 33.0 - FOLD_DUR, 40.0, 0.0, 0.35, "fold"),
]

# supers: start, end, lines, style
SUPERS = [
    (4.7, 7.7, ["Line one.", "The promise."], "hero"),
    (8.6, 11.6, ["Line two.", "The twist."], "hero left"),
    (12.9, 14.6, ["The headline spec.", "A number people remember."], "lower"),
    (18.5, 20.6, ["Feature one."], "lower"),
    (21.4, 23.7, ["Feature two."], "lower"),
    (24.4, 26.6, ["Feature three.", "What it means for you."], "lower"),
    (27.4, 29.6, ["Feature four.", "One-line benefit."], "lower"),
    (30.4, 32.6, ["The callback line."], "lower"),
]

shot_html, tl_js = [], []
z = 50
for sid, clip, start, end, ms, rate, tin in SHOTS:
    # a folding-out shot must sit above its successor; an unfolding-in shot above its predecessor
    z = z + 1 if tin == "unfold" else z - 1
    dur = round(end - start, 3)
    halves = []
    for side in ("l", "r"):
        halves.append(
            f'<div class="half {side}" id="{sid}-{side}"><div class="shade" id="{sid}-{side}-sh"></div>'
            f'<video id="{sid}-{side}v" class="clip" src="assets/clips/{clip}.mp4" data-start="{start}" '
            f'data-duration="{dur}" data-media-start="{ms}" data-playback-rate="{rate}" '
            f'data-track-index="{1 if side == "l" else 2}" muted playsinline></video></div>'
        )
    shot_html.append(f'<div class="shot" id="{sid}" style="z-index:{z}">{"".join(halves)}</div>')

# transitions
for i, (sid, clip, start, end, ms, rate, tin) in enumerate(SHOTS):
    if tin == "unfold":
        tl_js.append(f'unfold("{sid}", {start}, {UNFOLD_DUR});')
    if tin == "fold":
        prev = SHOTS[i - 1][0]
        cue = round(start + FOLD_DUR, 3)
        tl_js.append(f'fold("{prev}", "{sid}", {cue}, {FOLD_DUR});')

sup_html = []
for k, (a, b, lines, style) in enumerate(SUPERS):
    inner = "".join(f'<div class="ln"><span id="t{k}-{j}">{ln}</span></div>' for j, ln in enumerate(lines))
    sup_html.append(f'<div class="super {style}" id="t{k}">{inner}</div>')
    tl_js.append(f'superIn({k}, {len(lines)}, {a}, {b});')

html = Path("src/template.html").read_text()
html = html.replace("<!--SHOTS-->", "\n      ".join(shot_html))
html = html.replace("<!--SUPERS-->", "\n      ".join(sup_html))
html = html.replace("/*TRANSITIONS*/", "\n      ".join(tl_js))
Path("index.html").write_text(html)
print("wrote index.html", len(SHOTS), "shots", len(SUPERS), "supers")
