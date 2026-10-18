"""Writes index.html for an aspect: python3 build.py 169 | 916"""
import sys, pathlib
A = sys.argv[1]; W, H = (1920, 1080) if A == '169' else (1080, 1920)
html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>The Brief — Chandan · Motion &amp; Video</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-Regular.woff2") format("woff2"); font-style: normal; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }}
#cv, #hud {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }} #hud {{ z-index: 5; }}
.wrap {{ position: absolute; inset: 0; z-index: 2; will-change: transform; }} .wrap video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
#warm {{ position: absolute; left: -9999px; }} #warm span:nth-child(1) {{ font-family: "Archivo Black"; }} #warm span:nth-child(2) {{ font-family: "Space Mono"; }} #warm span:nth-child(3) {{ font-family: "Instrument Serif"; }}
</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="45" data-width="{W}" data-height="{H}">
<canvas id="cv" class="clip" width="{W}" height="{H}" data-start="0" data-duration="45" data-track-index="0"></canvas>
<div id="blitz-wrap" class="wrap"><video id="blitz" class="clip" src="assets/video/blitz_{A}.mp4" data-start="19.2" data-duration="9.6" data-track-index="1" muted playsinline></video></div>
<div id="sing-wrap" class="wrap"><video id="sing" class="clip" src="assets/video/sing_{A}.mp4" data-start="28.8" data-duration="3.6" data-track-index="2" muted playsinline></video></div>
<canvas id="hud" class="clip" width="{W}" height="{H}" data-start="0" data-duration="45" data-track-index="3" data-layout-allow-occlusion></canvas>
<div id="warm"><span>Aa</span><span>Aa</span><span>Aa</span></div>
<audio id="score" src="assets/audio/score.wav" data-start="0" data-duration="45" data-track-index="10" data-volume="1"></audio>
<audio id="vo" src="assets/audio/vo36.wav" data-start="28.8" data-duration="3.6" data-track-index="11" data-volume="1.4"></audio>
</div>
<script>{pathlib.Path(__file__).with_name("reel.js").read_text()}</script>
</body></html>'''
pathlib.Path(__file__).with_name('index.html').write_text(html); print('built', A, W, H)
