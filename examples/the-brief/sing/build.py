# Motion Prompt #001 #008 (spring form) · MIT License (c) 2026 Shohei Ohtaki · https://showheyohtaki.github.io/motion-prompt/
"""Writes the 'Now make it sing' clip (3.6 s) for a given aspect: python3 build.py 1920 1080 | 1080 1920"""
import sys, json, pathlib
W, H = int(sys.argv[1]), int(sys.argv[2])
env = json.load(open(pathlib.Path(__file__).parent.parent / 'vo' / 'env.json'))
html = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>The Brief · sing</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0d0d0f; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #0d0d0f; font-family: "Archivo Black", sans-serif; }}
#cv {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }} #fontwarm {{ position: absolute; left: -9999px; font-family: "Archivo Black"; }}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="3.6" data-width="{W}" data-height="{H}">
<canvas id="cv" class="clip" width="{W}" height="{H}" data-start="0" data-duration="3.6" data-track-index="0"></canvas>
<div id="fontwarm">NOW MAKE IT SING</div>
<audio id="vo" src="assets/vo36.wav" data-start="0" data-duration="3.6" data-track-index="10" data-volume="1"></audio></div>
<script>
const ENV = {json.dumps(env)}, W = {W}, H = {H}, M = Math.min(W, H);
const cv = document.getElementById("cv"), c = cv.getContext("2d");
const env = t => {{ const f = t * 30, i = Math.floor(f), a = ENV[Math.max(0, Math.min(ENV.length - 1, i))], b = ENV[Math.max(0, Math.min(ENV.length - 1, i + 1))]; return a + (b - a) * (f - i); }};
const spring = (t, k, w) => t <= 0 ? 0 : 1 - Math.exp(-k * t) * Math.cos(w * t);     // Motion Prompt #001/#008 spring form
function render(t) {{
  c.fillStyle = "#0d0d0f"; c.fillRect(0, 0, W, H);
  const cx = W / 2, cy = H * (H > W ? 0.4 : 0.42), e = env(t);
  // title: NOW MAKE IT SING — #008 kinetic slam per word on the 0.2 s grid (beats of 150 BPM)
  const words = ["NOW", "MAKE", "IT", "SING."], fs = Math.round(M * (H > W ? 0.12 : 0.11));
  c.font = fs + 'px "Archivo Black"'; c.textAlign = "center"; c.textBaseline = "middle";
  const titleOut = Math.max(0, Math.min(1, (t - 0.85) / 0.15));
  words.forEach((w, i) => {{ const t0 = i * 0.2, q = t - t0; if (q < 0 || titleOut >= 1) return;
    const sc = i === 3 ? 3.4 - 2.4 * Math.min(1, q / 0.18) ** 3 : spring(q, 6.5, 15);         // slam vs spring
    const totalW = words.map(x => c.measureText(x + " ").width).reduce((a, b) => a + b, 0);
    let x = cx - totalW / 2; for (let k = 0; k < i; k++) x += c.measureText(words[k] + " ").width;
    const ww = c.measureText(w).width; c.save(); c.globalAlpha = 1 - titleOut; c.translate(x + ww / 2, cy); c.scale(sc, sc);
    c.fillStyle = i === 3 ? "#ff5a1f" : "#f2eee6"; c.fillText(w, 0, 0); c.restore(); }});
  // the Dot as a speaker: radial EQ + pulsing body, after the title
  const a = Math.max(0, Math.min(1, (t - 0.9) / 0.2)); if (a <= 0) return;
  c.save(); c.globalAlpha = a;
  const R = M * 0.15 * (1 + e * 0.25), N = 72;
  for (let k = 0; k < N; k++) {{ const ang = k / N * Math.PI * 2 - Math.PI / 2, tt = t - (k / N) * 0.9, v = tt < 1 ? 0 : env(tt);
    const r0 = M * 0.2, r1 = r0 + M * 0.02 + v * M * 0.13; c.strokeStyle = `rgba(242,238,230,${{0.2 + v * 0.7}})`; c.lineWidth = M * 0.007; c.lineCap = "round";
    c.beginPath(); c.moveTo(cx + Math.cos(ang) * r0, cy + Math.sin(ang) * r0); c.lineTo(cx + Math.cos(ang) * r1, cy + Math.sin(ang) * r1); c.stroke(); }}
  const g = c.createRadialGradient(cx, cy, 0, cx, cy, R * 2.4); g.addColorStop(0, "rgba(255,90,31,.5)"); g.addColorStop(1, "rgba(255,90,31,0)"); c.fillStyle = g; c.fillRect(cx - R * 2.4, cy - R * 2.4, R * 4.8, R * 4.8);
  c.fillStyle = "#ff5a1f"; c.beginPath(); c.arc(cx, cy, R, 0, Math.PI * 2); c.fill();
  c.fillStyle = "rgba(60,20,8,.5)"; for (let row = -4; row <= 4; row++) for (let col = -4; col <= 4; col++) {{ const x = cx + col * R * 0.2 + (row % 2) * R * 0.1, y = cy + R * 0.12 + row * R * 0.17; if (Math.hypot(x - cx, y - cy) < R * 0.78 && y > cy - R * 0.1) {{ c.beginPath(); c.arc(x, y, R * 0.035, 0, Math.PI * 2); c.fill(); }} }}
  c.fillStyle = "rgba(255,255,255,.5)"; c.beginPath(); c.ellipse(cx - R * 0.42, cy - R * 0.45, R * 0.16, R * 0.1, -0.6, 0, Math.PI * 2); c.fill();
  c.restore();
}}
const tl = gsap.timeline({{ paused: true }}); const d = {{ t: 0 }};
document.fonts.load(Math.round(M * 0.12) + 'px "Archivo Black"').then(() => {{
  tl.to(d, {{ t: 3.6, duration: 3.6, ease: "none", onUpdate: () => render(d.t) }}, 0); render(0);
  window.__timelines["main"] = tl; }});
</script></body></html>'''
pathlib.Path(__file__).with_name('index.html').write_text(html)
print('built', W, H)
