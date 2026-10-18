"""Writes index.html for an aspect:  python3 build.py 169   |   python3 build.py 916

reel.js is inlined so the render is one self-contained file. Fonts load from Google Fonts at render time;
for offline renders drop .woff2 files in assets/fonts and swap the <link> for @font-face rules.
"""
import pathlib
import sys

A = sys.argv[1] if len(sys.argv) > 1 else '169'
W, H = (1920, 1080) if A == '169' else (1080, 1920)
DUR = 12
here = pathlib.Path(__file__).parent
html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>Chop reel</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono:wght@400;700&display=block" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
#cv {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
#warm {{ position: absolute; left: -9999px; }} #warm span:nth-child(1) {{ font-family: "Archivo Black"; }} #warm span:nth-child(2) {{ font-family: "Space Mono"; }}
</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
<canvas id="cv" class="clip" width="{W}" height="{H}" data-start="0" data-duration="{DUR}" data-track-index="0"></canvas>
<div id="warm"><span>Aa</span><span>Aa</span></div>
<audio id="score" src="assets/audio/score.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
</div>
<script>{(here / "reel.js").read_text()}</script>
</body></html>'''
(here / 'index.html').write_text(html)
print('built', A, W, H)
