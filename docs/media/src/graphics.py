"""Build a still composition for a given size: python3 build.py banner|social|arch"""
import sys, pathlib
kind = sys.argv[1]
W, H = {"banner": (1600, 560), "social": (1280, 640), "arch": (1600, 900)}[kind]
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;600;800;900&family=Space+Mono:wght@400;700&display=block" />'
base_css = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#0d0d0f; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#0d0d0f; color:#f2eee6; font-family: Inter, sans-serif; }}
.mono {{ font-family:"Space Mono", monospace; }}
.acc {{ color:#ff5a1f; }}
"""
thumbs = "".join(f'<div class="th" style="background-image:url(assets/t{i}.jpg)"></div>' for i in range(1, 7))

if kind in ("banner", "social"):
    big = 132 if kind == "banner" else 104
    body = f"""
<div id="grid"></div>
<div id="strip">{thumbs}</div>
<div id="fade"></div>
<div id="txt">
  <div class="kick mono"><span class="dot"></span>CLAUDE CODE · VIDEO KIT</div>
  <h1>Video&nbsp;Studio<span class="acc">.</span></h1>
  <p>Describe a video. Claude makes it — shots, music, voice, captions —<br/>and renders it with <b class="acc">HyperFrames</b>.</p>
  <div class="chips mono"><span>launch films</span><span>chop-cut reels</span><span>UGC ads</span><span>product demos</span><span>art-style explainers</span><span>captions</span><span>original scores</span></div>
</div>"""
    css = f"""
#grid {{ position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px); background-size:40px 40px; }}
#strip {{ position:absolute; right:-60px; top:-40px; width:{int(W*.52)}px; display:grid; grid-template-columns:1fr 1fr; gap:14px; transform:rotate(-8deg); }}
.th {{ aspect-ratio:16/9; border-radius:14px; background-size:cover; background-position:center; box-shadow:0 20px 50px rgba(0,0,0,.5); border:1px solid rgba(255,255,255,.08); }}
#fade {{ position:absolute; inset:0; background:linear-gradient(90deg,#0d0d0f 38%,rgba(13,13,15,.75) 58%,rgba(13,13,15,0) 85%); }}
#txt {{ position:absolute; left:{int(W*.05)}px; top:50%; transform:translateY(-50%); width:{int(W*.62)}px; }}
.kick {{ font-size:{int(big*.15)}px; letter-spacing:.18em; color:#b9b4aa; display:flex; align-items:center; gap:12px; }}
.dot {{ width:{int(big*.13)}px; height:{int(big*.13)}px; border-radius:50%; background:#ff5a1f; display:inline-block; }}
h1 {{ font-family:Inter; font-weight:900; font-size:{big}px; line-height:1; letter-spacing:-.045em; margin-top:{int(big*.14)}px; }}
p {{ font-size:{int(big*.2)}px; line-height:1.4; color:#d8d3c9; margin-top:{int(big*.2)}px; }}
.chips {{ margin-top:{int(big*.24)}px; display:flex; flex-wrap:wrap; gap:10px; max-width:{int(W*.5)}px; }}
.chips span {{ font-size:{int(big*.12)}px; padding:6px 12px; border:1px solid rgba(255,255,255,.18); border-radius:99px; color:#e9e4da; }}
"""
else:  # architecture diagram
    makers = [("Code scenes", "HTML · canvas · GSAP"), ("AI shots", "Higgsfield · Fal"), ("Art engine", "huashu-art-motion"),
              ("Named moves", "motion-prompt"), ("Voice", "Kokoro · ElevenLabs"), ("Music & SFX", "synth.py · beats.py"),
              ("Captions", "WhisperX · caption kit"), ("Footage", "screen recs · talking heads")]
    cards = "".join(f'<div class="mk"><b>{a}</b><span class="mono">{b}</span></div>' for a, b in makers)
    wf = ["studio", "explainer", "chop-reel", "launch-film", "ugc-ads", "product-demo", "art-styles", "score", "caption-video"]
    wfs = "".join(f'<span>{w}</span>' for w in wf)
    body = f"""
<div class="lbl mono" style="top:44px">1 · YOU ASK, IN PLAIN WORDS</div>
<div id="ask">“A 30-second launch film for my app — vertical, punchy.”</div>
<div class="lbl mono" style="top:196px">2 · A WORKFLOW SKILL PLANS IT  (cue sheet on a beat grid)</div>
<div id="wf" class="mono">{wfs}</div>
<div class="lbl mono" style="top:330px">3 · ASSET MAKERS</div>
<div id="mks">{cards}</div>
<svg id="arrows" width="{W}" height="{H}"><defs><marker id="ah" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ff5a1f"/></marker></defs>
 <line x1="800" y1="150" x2="800" y2="186" stroke="#ff5a1f" stroke-width="3" marker-end="url(#ah)"/>
 <line x1="800" y1="296" x2="800" y2="322" stroke="#ff5a1f" stroke-width="3" marker-end="url(#ah)"/>
 <line x1="800" y1="598" x2="800" y2="628" stroke="#ff5a1f" stroke-width="3" marker-end="url(#ah)"/>
 <line x1="800" y1="768" x2="800" y2="800" stroke="#ff5a1f" stroke-width="3" marker-end="url(#ah)"/></svg>
<div id="core"><div class="mono k">★ THE CORE</div><b>HyperFrames composition</b><span class="mono">lint → check → snapshot → render → loudnorm −14 LUFS</span></div>
<div id="out" class="mono">out/your-film (16x9).mp4 · (9x16) · (4x5)</div>"""
    css = """
.lbl { position:absolute; left:80px; font-size:15px; letter-spacing:.16em; color:#8f8a80; }
#ask { position:absolute; left:80px; right:80px; top:74px; height:76px; border-radius:16px; background:#1a1a1f; border:1px solid #2c2c33; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:600; }
#wf { position:absolute; left:80px; right:80px; top:226px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
#wf span { padding:12px 18px; border-radius:12px; background:#16161a; border:1px solid #33333b; font-size:19px; color:#f2eee6; }
#wf span:first-child { background:#ff5a1f; color:#0d0d0f; border-color:#ff5a1f; font-weight:700; }
#mks { position:absolute; left:80px; right:80px; top:360px; display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
.mk { background:#16161a; border:1px solid #2c2c33; border-radius:14px; padding:20px 22px; height:108px; display:flex; flex-direction:column; justify-content:center; gap:8px; }
.mk b { font-size:24px; font-weight:800; } .mk span { font-size:15px; color:#a39e94; }
#arrows { position:absolute; inset:0; }
#core { position:absolute; left:340px; right:340px; top:636px; height:132px; border-radius:20px; background:linear-gradient(135deg,#ff5a1f,#ff8a3d); color:#0d0d0f; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; box-shadow:0 20px 60px rgba(255,90,31,.25); }
#core .k { font-size:15px; letter-spacing:.2em; font-weight:700; } #core b { font-family:"Archivo Black"; font-size:44px; letter-spacing:-.02em; } #core span { font-size:17px; }
#out { position:absolute; left:0; right:0; top:812px; text-align:center; font-size:22px; color:#f2eee6; }
"""

html = f"""<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>{kind}</title>{FONTS}
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{base_css}{css}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="{W}" data-height="{H}">{body}</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>"""
pathlib.Path("index.html").write_text(html)
print("built", kind, W, H)
