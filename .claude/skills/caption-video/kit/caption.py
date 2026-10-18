#!/usr/bin/env python3
"""Caption kit: talking video in, HyperFrames project with word-timed captions (+ optional hook) out.

The default look ("lime") is a rebuild of a popular "Captions and Hooks" After Effects template
(no After Effects needed). `styles` lists the full catalog; `preview` renders every style
on a frame of the user's own footage so they can pick one.

  python3 caption.py new     <video> [name]   copy the video into videos/captions/<name>, transcribe it
  python3 caption.py styles                   list the caption styles (key, name, best for)
  python3 caption.py preview <name> [--hook ...]  one still per style on this footage → previews/styles.png
  python3 caption.py build   <name> [options]  (re)write index.html from transcript.json + options
  python3 caption.py render  <name>           render to <studio>/out/captions/<name>.mp4 (loudness -14 LUFS)

build options (saved to caption.json in the project, so re-builds remember them):
  --style lime          caption style key (see `styles`)
  --hook "s:How|c:I reached|b:300k+|l:without ads|r:views"
        one line per |, prefixed by its style:
        s = italic serif, c = condensed caps, b = big accent with ring, l = accent caps, r = small serif, right
  --hook-dur 2.8        seconds the hook stays up
  --hook-y 0.11         hook top, as a fraction of frame height (move it down when the face is high in frame)
  --hot "word,word"     words always shown in the accent colour (numbers are hot automatically)
  --accent "#A3E635"    override the style's accent colour
  --cap-y 0.76          override caption top, as a fraction of the frame height
  --words 3             override max words per caption
  --size 1.0            caption size multiplier
  --fix "wrong=right"   transcript corrections, comma-separated (e.g. "hyper frames=HyperFrames")
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
# studio root = 4 levels up (<studio>/.claude/skills/caption-video/kit); override with STUDIO_ROOT
ROOT = os.environ.get("STUDIO_ROOT") or os.path.abspath(os.path.join(KIT, "..", "..", "..", ".."))
PROJECTS = os.path.join(ROOT, "videos", "captions")
OUT = os.path.join(ROOT, "out", "captions")
HF = "hyperframes@0.8.147"
HF_ROOT = os.path.expanduser("~/.hyperframes-root")             # CLI checkout layout the transcriber expects
TRANSCRIBE = os.path.expanduser("~/.claude/skills/embedded-captions/scripts/transcribe.cjs")

# None = take the value from the chosen style
DEFAULTS = {"style": "lime", "hook": "", "hook_dur": 2.8, "hook_y": 0.11, "hot": "", "accent": None, "cap_y": None,
            "words": None, "size": 1.0, "fix": ""}
TYPES = {"style": str, "hook": str, "hook_dur": float, "hook_y": float, "hot": str, "accent": str, "cap_y": float,
         "words": int, "size": float, "fix": str}

# ---------------------------------------------------------------------------
# Style catalog. `fs` is caption size as a fraction of frame width (portrait); `active` is how the
# spoken word is marked: color | bg | glow | dim (unspoken words dimmed) | none.
STYLES = {
    "lime": dict(
        name="Lime Hook", best="the AE template look: bold, social, creator talking heads",
        font="Anton", weight=400, case="uppercase", fs=0.095, words=3, chars=18, cap_y=0.76,
        color="#ffffff", accent="#A3E635", active="color", pop=1.1,
        css="-webkit-text-stroke: 0.06em #0b0b0b; paint-order: stroke fill; text-shadow: 0 0.06em 0.18em rgba(0,0,0,0.55);"),
    "karaoke": dict(
        name="Karaoke Pop", best="fast hype edits and ads: big 2-word bursts, yellow spoken word",
        font="Montserrat", weight=900, case="uppercase", fs=0.1, words=2, chars=14, cap_y=0.76,
        color="#ffffff", accent="#FFE600", active="color", pop=1.1,
        css="-webkit-text-stroke: 0.09em #000; paint-order: stroke fill; text-shadow: 0 0.08em 0 #000; letter-spacing: -0.01em; gap: 0 0.34em;"),
    "oneword": dict(
        name="One Word", best="punchy short hooks and reels: one giant word at a time",
        font="BebasNeue", weight=400, case="uppercase", fs=0.19, words=1, chars=12, cap_y=0.72,
        color="#ffffff", accent="#FF4D3D", active="none", pop=1.0,
        css="text-shadow: 0 0.04em 0.12em rgba(0,0,0,0.6), 0 0 0.5em rgba(0,0,0,0.25); letter-spacing: 0.01em;"),
    "boxed": dict(
        name="Clean Box", best="explainers and UGC ads: dark text on a white card, highlighter on the spoken word",
        font="Inter", weight=800, case="none", fs=0.062, words=4, chars=24, cap_y=0.74,
        color="#141414", accent="#FFE66D", active="bg", pop=1.0, hot="#E4572E",
        box="background: #ffffff; padding: 0.22em 0.5em 0.28em; border-radius: 0.38em; box-shadow: 0 0.2em 0.6em rgba(0,0,0,0.25);",
        css="letter-spacing: -0.02em;"),
    "editorial": dict(
        name="Editorial", best="founder stories, premium brands: calm sentence case, key words in italic serif",
        font="Inter", weight=600, case="none", fs=0.064, words=4, chars=26, cap_y=0.74,
        color="#ffffff", accent="#F3D9A4", active="dim", pop=1.0, serif_hot=True,
        css="text-shadow: 0 0.05em 0.3em rgba(0,0,0,0.6); letter-spacing: -0.015em;"),
    "subtitle": dict(
        name="Subtitle", best="interviews, podcasts, accessibility: small full-sentence subtitles",
        font="Inter", weight=600, case="none", fs=0.046, words=7, chars=36, cap_y=0.8,
        color="#ffffff", accent="#ffffff", active="none", pop=1.0,
        box="background: rgba(0,0,0,0.62); padding: 0.25em 0.55em 0.3em; border-radius: 0.3em;",
        css="line-height: 1.25;"),
    "neon": dict(
        name="Neon", best="tech, AI and gaming: cyan glow on the spoken word",
        font="SpaceGrotesk", weight=700, case="uppercase", fs=0.08, words=3, chars=18, cap_y=0.74,
        color="#ffffff", accent="#22E5FF", active="glow", pop=1.08,
        css="text-shadow: 0 0.05em 0.2em rgba(0,0,0,0.7); letter-spacing: 0.01em;"),
}


def die(msg):
    sys.exit(f"[caption] {msg}")


def esc(s):
    return html.escape(s, quote=True)


def norm(s):
    return re.sub(r"[^a-z0-9%+]", "", s.lower())


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    w, h = s["width"], s["height"]
    rot = next((abs(int(d.get("rotation", 0))) for d in s.get("side_data_list", []) if "rotation" in d), 0)
    if rot in (90, 270):
        w, h = h, w
    return w, h, float(j["format"]["duration"])


def canvas(w, h):
    r = w / h
    if r < 0.7:
        return 1080, 1920      # 9:16
    if r < 0.95:
        return 1080, 1350      # 4:5
    if r < 1.2:
        return 1080, 1080
    return 1920, 1080


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "clip"


def project(name):
    proj = os.path.join(PROJECTS, name)
    if not os.path.isdir(proj):
        die(f"no project {proj} — run: caption.py new <video>")
    return proj


# ---------------------------------------------------------------------------
def cmd_new(a):
    src = os.path.abspath(a.video)
    if not os.path.exists(src):
        die(f"no such video: {src}")
    name = slug(a.name or os.path.splitext(os.path.basename(src))[0])
    proj = os.path.join(PROJECTS, name)
    os.makedirs(os.path.join(proj, "assets", "fonts"), exist_ok=True)
    # always a clean H.264/AAC copy: phone .mov/HEVC files then preview and render reliably
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    os.path.join(proj, "source.mp4")], check=True)
    for f in os.listdir(os.path.join(KIT, "fonts")):
        shutil.copy(os.path.join(KIT, "fonts", f), os.path.join(proj, "assets", "fonts", f))
    json.dump({"name": f"captions-{name}", "private": True, "type": "module",
               "scripts": {k: f"npx --yes {HF} {v}" for k, v in
                           {"dev": "preview", "check": "check", "render": "render", "publish": "publish"}.items()}},
              open(os.path.join(proj, "package.json"), "w"), indent=2)
    json.dump({"id": name, "name": name}, open(os.path.join(proj, "meta.json"), "w"), indent=2)
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
               "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}},
              open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
    print(f"[caption] project: {proj}\n[caption] transcribing (WhisperX, word-level)…")
    env = dict(os.environ, HYPERFRAMES_ROOT=HF_ROOT)
    tj = os.path.join(proj, "transcript.json")
    if os.path.exists(tj):
        os.remove(tj)
    r = subprocess.run(["node", TRANSCRIBE, proj], env=env)
    if r.returncode or not os.path.exists(tj):
        die("transcription failed (see output above)")
    words = load_words(proj)
    print(f"[caption] name: {name}")
    print(f"[caption] {len(words)} words: {' '.join(w[0] for w in words)}")
    cfg_path = os.path.join(proj, "caption.json")
    if os.path.exists(cfg_path):
        os.remove(cfg_path)
    write_index(proj, load_cfg(proj, {}))


def load_words(proj):
    t = json.load(open(os.path.join(proj, "transcript.json")))
    ws = t.get("words", t) if isinstance(t, dict) else t
    return [(w["text"].strip(), float(w["start"]), float(w["end"])) for w in ws
            if "start" in w and w.get("text", "").strip()]


def chunk(words, max_words, max_chars):
    out, cur = [], []
    for i, (t, s, e) in enumerate(words):
        cur.append(i)
        text = " ".join(words[j][0] for j in cur)
        nxt_gap = words[i + 1][1] - e if i + 1 < len(words) else 9
        nxt_len = len(text) + 1 + len(words[i + 1][0]) if i + 1 < len(words) else 0
        if (t.endswith((".", "?", "!", ",", ":", ";")) or len(cur) >= max_words
                or nxt_len > max_chars or nxt_gap > 0.35):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


FONTS = r"""
@font-face { font-family: "Anton"; src: url("assets/fonts/Anton.ttf"); }
@font-face { font-family: "BebasNeue"; src: url("assets/fonts/BebasNeue.ttf"); }
@font-face { font-family: "Oswald"; src: url("assets/fonts/Oswald.ttf"); font-weight: 200 700; }
@font-face { font-family: "Montserrat"; src: url("assets/fonts/Montserrat.ttf"); font-weight: 100 900; }
@font-face { font-family: "Inter"; src: url("assets/fonts/Inter.ttf"); font-weight: 100 900; }
@font-face { font-family: "SpaceGrotesk"; src: url("assets/fonts/SpaceGrotesk.ttf"); font-weight: 300 700; }
@font-face { font-family: "PlayfairItalic"; src: url("assets/fonts/PlayfairItalic.ttf"); font-weight: 400 900; font-style: italic; }
"""

BASE_CSS = r"""
html, body { margin: 0; background: #000; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }
#clip { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.caps { position: absolute; left: 0; right: 0; }
.cap { position: absolute; left: 6%; right: 6%; top: 0; display: flex; justify-content: center; }
.cap-in { display: flex; flex-wrap: wrap; justify-content: center; align-items: baseline; gap: 0 0.24em;
          line-height: 1.04; text-align: center; }
.w { display: inline-block; transform-origin: 50% 80%; border-radius: 0.14em; padding: 0.16em 0.04em; margin: -0.16em -0.04em; }
.serif { font-family: "PlayfairItalic", serif; font-style: italic; font-weight: 600; letter-spacing: 0; }
.hook { position: absolute; left: 7%; right: 7%; display: flex; flex-direction: column; align-items: center;
        text-align: center; color: #fff; text-shadow: 0 0.05em 0.3em rgba(0,0,0,0.45); }
.hl { display: block; position: relative; line-height: 0.95; white-space: nowrap; }
.hl.s { font-family: "PlayfairItalic", serif; font-style: italic; font-weight: 500; align-self: flex-end; margin-right: 6%; }
.hl.r { font-family: "PlayfairItalic", serif; font-style: italic; font-weight: 500; align-self: flex-end; margin-right: 4%; }
.hl.c { font-family: "Oswald", sans-serif; font-weight: 400; text-transform: uppercase; letter-spacing: 0.02em; }
.hl.l { font-family: "Oswald", sans-serif; font-weight: 700; text-transform: uppercase; }
.hl.b { font-family: "Anton", sans-serif; text-transform: lowercase; letter-spacing: -0.01em; }
.scrim { position: absolute; left: 0; right: 0; }
.ring { position: absolute; left: -12%; top: -6%; width: 124%; height: 112%; overflow: visible; pointer-events: none; }
.tag { position: absolute; left: 0; right: 0; top: 3.5%; display: flex; justify-content: center; }
.tag span { font-family: "Inter"; font-weight: 800; color: #111; background: #fff; border-radius: 999px;
            padding: 0.3em 0.9em; letter-spacing: -0.01em; box-shadow: 0 0.2em 0.8em rgba(0,0,0,0.35); }
"""


def load_cfg(proj, overrides):
    cfg = dict(DEFAULTS)
    path = os.path.join(proj, "caption.json")
    if os.path.exists(path):
        cfg.update(json.load(open(path)))
    cfg.update({k: v for k, v in overrides.items() if v is not None})
    if cfg["style"] not in STYLES:
        die(f"unknown style {cfg['style']!r} — choose from: {', '.join(STYLES)}")
    return cfg


def write_index(proj, cfg, label=None, out="index.html"):
    st = STYLES[cfg["style"]]
    vw, vh, dur = probe(os.path.join(proj, "source.mp4"))
    W, H = canvas(vw, vh)
    words = load_words(proj)
    fixmap = {norm(k): v for k, v in (p.split("=", 1) for p in cfg["fix"].split(",") if "=" in p)}
    words = [(re.sub(r"^[\w'%+-]+", fixmap[norm(t)], t) if norm(t) in fixmap else t, s, e) for t, s, e in words]
    hot = {norm(h) for h in cfg["hot"].split(",") if h.strip()}
    acc = cfg["accent"] or st["accent"]
    hot_color = st.get("hot", acc)
    cap_y = cfg["cap_y"] if cfg["cap_y"] is not None else st["cap_y"]
    n_words = cfg["words"] if cfg["words"] is not None else st["words"]
    fs = round(st["fs"] * (W if W < H else H * 0.62) * float(cfg["size"]))
    act = st["active"]
    els, js = [], []

    els.append(f'<video id="clip" src="source.mp4" playsinline data-has-audio="true" data-start="0" '
               f'data-duration="{dur:.3f}" data-track-index="0" data-volume="1"></video>')

    cap_css = (f'font-family:"{st["font"]}",sans-serif;font-weight:{st["weight"]};text-transform:{st["case"]};'
               f'color:{st["color"]};{st["css"]}{st.get("box", "")}font-size:{fs}px')
    groups = chunk(words, int(n_words), st["chars"])
    cap = []
    for ci, g in enumerate(groups):
        c0 = words[g[0]][1]
        c1 = words[groups[ci + 1][0]][1] if ci + 1 < len(groups) else min(dur, words[g[-1]][2] + 0.6)
        if ci + 1 == len(groups):
            c1 = max(c1, c0 + 0.5)
        spans = []
        for wi in g:
            t, s, e = words[wi]
            is_hot = norm(t) in hot or bool(re.search(r"\d", t))
            cls = "w serif" if is_hot and st.get("serif_hot") else "w"
            style = f' style="color:{hot_color}"' if is_hot else ""
            spans.append(f'<span id="w{wi}" class="{cls}"{style}>{esc(t)}</span>')
            off = words[wi + 1][1] if wi + 1 < len(words) and wi + 1 in g else c1
            off = max(off, s + 0.05)
            sel = f'"#w{wi}"'
            if act == "color":
                js.append(f'tl.set({sel}, {{color: "{acc}"}}, {s:.3f});')
                if not is_hot:
                    js.append(f'tl.set({sel}, {{color: "{st["color"]}"}}, {off:.3f});')
            elif act == "bg":
                js.append(f'tl.set({sel}, {{backgroundColor: "{acc}"}}, {s:.3f});')
                js.append(f'tl.set({sel}, {{backgroundColor: "rgba(0,0,0,0)"}}, {off:.3f});')
            elif act == "glow":
                js.append(f'tl.set({sel}, {{color: "{acc}", textShadow: "0 0 0.25em {acc}, 0 0 0.6em {acc}"}}, {s:.3f});')
                js.append(f'tl.set({sel}, {{color: "{hot_color if is_hot else st["color"]}", '
                          f'textShadow: "0 0.05em 0.2em rgba(0,0,0,0.7)"}}, {off:.3f});')
            elif act == "dim":
                js.append(f'tl.fromTo({sel}, {{opacity: 0.38}}, {{opacity: 1, duration: 0.1}}, {s:.3f});')
            if st["pop"] > 1:
                js.append(f'tl.fromTo({sel}, {{scale: 1}}, {{scale: {st["pop"]}, duration: 0.08, ease: "power2.out"}}, {s:.3f});')
                js.append(f'tl.to({sel}, {{scale: 1, duration: 0.12, ease: "power2.inOut"}}, {s + 0.08:.3f});')
        cap.append(f'<div id="cap{ci}" class="clip cap" data-start="{c0:.3f}" data-duration="{c1 - c0:.3f}" '
                   f'data-track-index="20"><div class="cap-in" style=\'{cap_css}\'>{" ".join(spans)}</div></div>')
        js.append(f'tl.fromTo("#cap{ci} .cap-in", {{scale: 0.82, opacity: 0, y: {round(fs * 0.12)}}}, '
                  f'{{scale: 1, opacity: 1, y: 0, duration: 0.14, ease: "back.out(2.2)"}}, {c0:.3f});')
    els.append(f'<div class="caps" style="top:{round(H * float(cap_y))}px">\n  ' + "\n  ".join(cap) + "\n</div>")

    # hook: the template's mixed-type stack, top of frame, tinted with the style accent
    if cfg["hook"].strip():
        hd = float(cfg["hook_dur"])
        size = {"s": 0.075, "r": 0.06, "c": 0.085, "l": 0.095, "b": 0.26}
        hook_acc = cfg["accent"] or (st["accent"] if st["accent"].lower() != "#ffffff" else STYLES["lime"]["accent"])
        lines = []
        for k, part in enumerate(p for p in cfg["hook"].split("|") if p.strip()):
            kind, _, text = part.partition(":") if re.match(r"^[scrlb]:", part) else ("c", "", part)
            px = round(size[kind] * min(W, H * 0.6))
            color = hook_acc if kind in ("b", "l") else "#fff"
            ring = ""
            if kind == "b":
                ring = (f'<svg class="ring" viewBox="0 0 100 50" preserveAspectRatio="none">'
                        f'<path id="ring" d="M8,30 C6,10 40,3 62,5 C86,7 98,18 94,32 C90,45 52,49 28,45 C12,42 3,33 12,24"'
                        f' fill="none" stroke="{hook_acc}" stroke-linecap="round" vector-effect="non-scaling-stroke"'
                        f' style="stroke-width:{max(4, px // 28)}px" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
            lines.append(f'<span id="hl{k}" class="hl {kind}" style="font-size:{px}px;color:{color}">{esc(text)}{ring}</span>')
            js.append(f'tl.fromTo("#hl{k}", {{opacity: 0, y: {round(px * 0.35)}}}, '
                      f'{{opacity: 1, y: 0, duration: 0.32, ease: "power3.out"}}, {0.05 + k * 0.09:.2f});')
            if kind == "b":
                js.append(f'tl.fromTo("#hl{k}", {{scale: 1.25}}, {{scale: 1, duration: 0.4, ease: "back.out(2)"}}, {0.05 + k * 0.09:.2f});')
                js.append(f'tl.to("#ring", {{strokeDashoffset: 0, duration: 0.55, ease: "power2.inOut"}}, {0.35 + k * 0.09:.2f});')
        js.append(f'tl.to("#hook", {{opacity: 0, y: -30, duration: 0.25, ease: "power2.in"}}, {hd - 0.25:.2f});')
        js.append('tl.fromTo("#scrim", {opacity: 0}, {opacity: 1, duration: 0.2}, 0);')
        js.append(f'tl.to("#scrim", {{opacity: 0, duration: 0.35}}, {hd - 0.3:.2f});')
        hy = float(cfg["hook_y"])
        if hy < 0.25:   # hook at the top: shade from the top edge down
            scrim = "top:0;height:62%;background:linear-gradient(to bottom,rgba(0,0,0,0.78) 0%,rgba(0,0,0,0.6) 45%,rgba(0,0,0,0) 100%)"
        else:           # hook lower in frame: a soft band behind it, fading out above and below
            scrim = (f"top:{max(0, hy - 0.12) * 100:.1f}%;height:48%;background:linear-gradient(to bottom,"
                     "rgba(0,0,0,0) 0%,rgba(0,0,0,0.62) 25%,rgba(0,0,0,0.62) 65%,rgba(0,0,0,0) 100%)")
        els.append(f'<div id="scrim" class="clip scrim" data-start="0" data-duration="{hd:.2f}" data-track-index="29" style="{scrim}"></div>')
        els.append(f'<div id="hook" class="clip hook" data-start="0" data-duration="{hd:.2f}" data-track-index="30" '
                   f'style="top:{round(H * float(cfg["hook_y"]))}px">{"".join(lines)}</div>')

    if label:   # preview-only badge naming the style
        els.append(f'<div class="clip tag" data-start="0" data-duration="{dur:.3f}" data-track-index="90">'
                   f'<span style="font-size:{round(W * 0.05)}px">{esc(label)}</span></div>')

    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width={W}, height={H}">
<title>Captions {esc(os.path.basename(proj))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{FONTS}{BASE_CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{dur:.3f}" data-fps="30">
{chr(10).join(els)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
    open(os.path.join(proj, out), "w").write(doc)
    return W, H, dur, words, groups


def overrides_from(a):
    return {k: getattr(a, k, None) for k in DEFAULTS}


def cmd_build(a):
    proj = project(a.name)
    cfg = load_cfg(proj, overrides_from(a))
    json.dump(cfg, open(os.path.join(proj, "caption.json"), "w"), indent=2)
    W, H, dur, _, groups = write_index(proj, cfg)
    print(f"[caption] built {proj}/index.html  (style {cfg['style']}, {W}x{H}, {dur:.1f}s, {len(groups)} captions"
          f"{', hook' if cfg['hook'].strip() else ''})")


def cmd_styles(a):
    for i, (k, st) in enumerate(STYLES.items(), 1):
        print(f"{i}. {st['name']:<12} [{k}]  {st['best']}")


def pick_time(words, hook_dur, has_hook):
    """One shared moment for every style: a word of 4+ letters, mid-sentence, after the hook."""
    t_min = hook_dur + 0.2 if has_hook else 0.0
    for i in range(max(1, len(words) // 5), len(words) - 1):    # skip the intro / name
        t, s, e = words[i]
        if s >= t_min and len(norm(t)) >= 4 and words[i][1] - words[i - 1][2] < 0.3:
            return round(s + min(0.15, (e - s) / 2), 3)
    later = [w for w in words if w[1] >= t_min] or words
    return round(later[0][1] + 0.1, 3)


def cmd_preview(a):
    """One snapshot per style at the same moment (+ a hook frame when a hook is given), tiled into a sheet."""
    proj = project(a.name)
    base = load_cfg(proj, overrides_from(a))
    pdir = os.path.join(proj, "previews")
    shutil.rmtree(pdir, ignore_errors=True)
    os.makedirs(pdir)
    keep = open(os.path.join(proj, "index.html")).read() if os.path.exists(os.path.join(proj, "index.html")) else None
    tiles = []
    try:
        for i, key in enumerate(STYLES, 1):
            cfg = dict(base, style=key, accent=None, cap_y=None, words=None) if not a.keep_overrides else dict(base, style=key)
            W, H, dur, words, groups = write_index(proj, cfg, label=f"{i}. {STYLES[key]['name']}")
            t = pick_time(words, float(cfg["hook_dur"]), bool(cfg["hook"].strip()))
            sd = os.path.join(pdir, key)
            subprocess.run(["npx", "--yes", HF, "snapshot", proj, "-o", sd, "--at", str(t), "--no-end",
                            "--describe", "false"], check=True, capture_output=True)
            png = next(os.path.join(sd, f) for f in sorted(os.listdir(sd)) if f.endswith(".png"))
            tiles.append(png)
            print(f"[caption] preview {i}/{len(STYLES)} {key} @ {t}s")
        if base["hook"].strip():
            write_index(proj, dict(base, style="lime"), label="Hook (first seconds)")
            sd = os.path.join(pdir, "_hook")
            subprocess.run(["npx", "--yes", HF, "snapshot", proj, "-o", sd, "--at", "1.4", "--no-end",
                            "--describe", "false"], check=True, capture_output=True)
            tiles.append(next(os.path.join(sd, f) for f in sorted(os.listdir(sd)) if f.endswith(".png")))
    finally:
        if keep is not None:
            open(os.path.join(proj, "index.html"), "w").write(keep)
    cols = 4 if len(tiles) > 4 else len(tiles)
    rows = -(-len(tiles) // cols)
    tw = 360
    inputs, filt = [], []
    for i, p in enumerate(tiles):
        inputs += ["-i", p]
        filt.append(f"[{i}:v]scale={tw}:-2,pad={tw + 12}:ih+12:6:6:color=#111111[t{i}]")
    while len(filt) < cols * rows:      # pad the grid with blank tiles
        i = len(filt)
        inputs += ["-f", "lavfi", "-i", f"color=c=#111111:s={tw + 12}x{round(tw * H / W) + 12}:d=1"]
        filt.append(f"[{i}:v]null[t{i}]")
    th = round(tw * H / W) + 12
    layout = "|".join(f"{(i % cols) * (tw + 12)}_{(i // cols) * th}" for i in range(cols * rows))
    sheet = os.path.join(pdir, "styles.png")
    fc = ";".join(filt) + ";" + "".join(f"[t{i}]" for i in range(cols * rows)) + \
        f"xstack=inputs={cols * rows}:layout={layout}:fill=#111111"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-frames:v", "1", sheet], check=True)
    print(f"[caption] sheet → {sheet}")


def cmd_render(a):
    proj = project(a.name)
    os.makedirs(OUT, exist_ok=True)
    cmd_build(argparse.Namespace(name=a.name, **{k: None for k in DEFAULTS}))   # rebuild from caption.json
    raw = os.path.join(proj, "render_raw.mp4")
    subprocess.run(["npx", "--yes", HF, "render", "-o", raw, "--fps", "30"], cwd=proj, check=True)
    final = os.path.join(OUT, f"{a.name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", final], check=True)
    print(f"[caption] done → {final}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("video")
    n.add_argument("name", nargs="?")
    sub.add_parser("styles")
    for cmd in ("build", "preview"):
        b = sub.add_parser(cmd)
        b.add_argument("name")
        for k in DEFAULTS:
            b.add_argument("--" + k.replace("_", "-"), dest=k, type=TYPES[k], default=None)
        if cmd == "preview":
            b.add_argument("--keep-overrides", action="store_true",
                           help="apply saved accent/cap-y/words to every style instead of each style's own")
    r = sub.add_parser("render")
    r.add_argument("name")
    a = p.parse_args()
    {"new": cmd_new, "styles": cmd_styles, "build": cmd_build, "preview": cmd_preview, "render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main()
