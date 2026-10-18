// Chop-reel engine — CapCut-style fast edit on one canvas. Every frame is a pure function of t (deterministic render).
// EDIT THIS FILE: palette, SHOTS (the edit), scene functions, and the FX lists (PUNCH / FLASH / SHAKES / WHIPS).
// Layout is relative to the stage (W×H, M = short side) so the same edit renders 16:9 and 9:16 (build.py 169 | 916).
// Grid: 150 BPM → beat B = 0.4 s, bar = 1.6 s. Keep every cut on the grid and mirror the cue times in score.py.
(() => {
const root = document.getElementById('root');
const W = +root.dataset.width, H = +root.dataset.height, M = Math.min(W, H), PORT = H > W, DUR = +root.dataset.duration;
const cv = document.getElementById('cv'), c = cv.getContext('2d');
const off = document.createElement('canvas'); off.width = W; off.height = H; const o = off.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H; const a2 = acc.getContext('2d');
const B = 0.4;

// ---------- palette & type ----------
const INK = '#0d0d0f', PAPER = '#f2eee6', ACC = '#ff5a1f', BLUE = '#2e5bff', LIME = '#c6f432', YEL = '#ffd21f';
const FONT = 'Archivo Black', MONOF = 'Space Mono';

// ---------- math ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const eOut3 = k => 1 - Math.pow(1 - k, 3), eIO2 = k => k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
const eOut5 = k => 1 - Math.pow(1 - k, 5);
const backOut = (k, s = 1.70158) => 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2);
const spring = (t, k = 7, w = 17) => t <= 0 ? 0 : 1 - Math.exp(-k * t) * Math.cos(w * t);     // overshoot pop
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

// ---------- drawing helpers ----------
const F = (px, fam = FONT) => `${Math.round(px)}px "${fam}"`;
const rr = (g, x, y, w, hh, r) => { g.beginPath(); g.roundRect(x, y, w, hh, r); };
function text(g, s, x, y, px, col, { fam = FONT, align = 'center', base = 'middle', ls = 0 } = {}) {
  g.font = F(px, fam); g.fillStyle = col; g.textAlign = align; g.textBaseline = base;
  if (ls) g.letterSpacing = ls + 'px'; g.fillText(s, x, y); g.letterSpacing = '0px';
}
const fit = (g, s, px, maxW, fam = FONT) => { g.font = F(px, fam); const w = g.measureText(s).width; return w > maxW ? px * maxW / w : px; };
const bg = (g, col) => { g.fillStyle = col; g.fillRect(0, 0, W, H); };

// ======================= SCENES (g = context, l = local seconds) =======================
function hook(g, l) {                               // 0–1.6: word slam per beat
  bg(g, INK); const words = ['ONE', 'BRIEF.', '60 MIN.', 'GO.'];
  const i = Math.min(words.length - 1, Math.floor(l / B)), lt = l - i * B;
  const px = fit(g, words[i], M * (PORT ? .26 : .3), W * .86), s = 1 + .35 * (1 - spring(lt, 9, 20));
  g.save(); g.translate(W / 2, H / 2); g.scale(s, s); text(g, words[i], 0, 0, px, i === 3 ? ACC : PAPER); g.restore();
}
function kinetic(g, l) {                            // 1.6–4.0: stacked kinetic type with mask reveal
  bg(g, PAPER); const lines = [['MAKE', INK], ['IT', ACC], ['MOVE.', INK]]; const lh = M * (PORT ? .2 : .22);
  lines.forEach(([w, col], i) => {
    const k = eOut5(seg(l, i * B, i * B + .35)), y = H / 2 + (i - 1) * lh;
    g.save(); g.beginPath(); g.rect(0, y - lh / 2, W, lh); g.clip();
    text(g, w, W / 2, y + (1 - k) * lh, fit(g, w, lh * .95, W * .9), col); g.restore();
  });
  const k = seg(l, 1.6, 2.4); g.fillStyle = ACC; g.fillRect(W * .1, H / 2 + lh * 1.6, W * .8 * eOut3(k), M * .012);
}
function counter(g, l) {                            // 4.0–6.4: count-up + overshooting bars
  bg(g, INK); const v = Math.round(25000 * eOut3(seg(l, 0, 1.2)));
  text(g, v.toLocaleString('en-US'), W / 2, H * (PORT ? .36 : .38), M * .2, PAPER);
  text(g, 'FRAMES RENDERED', W / 2, H * (PORT ? .36 : .38) + M * .15, M * .045, ACC, { fam: MONOF, ls: M * .006 });
  const n = 7, bw = W * .7 / n, base = H * (PORT ? .82 : .9);
  for (let i = 0; i < n; i++) {
    const k = backOut(clamp(seg(l, .3 + i * .1, .8 + i * .1)), 2.2), hgt = M * (.08 + .25 * hash(i + 3)) * k;
    g.fillStyle = i === n - 1 ? ACC : BLUE; rr(g, W * .15 + i * bw + bw * .12, base - hgt, bw * .76, hgt, M * .01); g.fill();
  }
}
function cards(g, l) {                              // 6.4–8.8: staggered cards on the beat
  bg(g, '#16161a'); const labels = ['STORY', 'PACE', 'SOUND', 'TYPE'], cols = [ACC, LIME, YEL, BLUE];
  const cw = PORT ? W * .78 : W * .2, ch = PORT ? H * .16 : H * .5, gap = M * .03;
  labels.forEach((s, i) => {
    const k = spring(l - i * B, 8, 16), x = PORT ? (W - cw) / 2 : W / 2 + (i - 1.5) * (cw + gap) - cw / 2;
    const y = PORT ? H / 2 + (i - 1.5) * (ch + gap) - ch / 2 : (H - ch) / 2;
    g.save(); g.translate(x + cw / 2, y + ch / 2 + (1 - k) * M * .25); g.rotate((1 - k) * (i % 2 ? .12 : -.12));
    g.globalAlpha = clamp(k * 1.5); g.fillStyle = cols[i]; rr(g, -cw / 2, -ch / 2, cw, ch, M * .025); g.fill();
    text(g, s, 0, 0, fit(g, s, M * .07, cw * .8), INK); g.restore(); g.globalAlpha = 1;
  });
}
function endcard(g, l) {                            // 9.2–12: logo lockup
  bg(g, ACC); const k = spring(l, 6, 14);
  g.save(); g.translate(W / 2, H / 2 - M * .04); g.scale(.6 + .4 * k, .6 + .4 * k);
  text(g, 'YOUR NAME.', 0, 0, fit(g, 'YOUR NAME.', M * .16, W * .85), INK); g.restore();
  g.globalAlpha = seg(l, .5, .9); text(g, 'M O T I O N   ·   V I D E O', W / 2, H / 2 + M * .1, M * .035, INK, { fam: MONOF });
  g.globalAlpha = seg(l, 2.2, 2.8); bg(g, '#000'); g.globalAlpha = 1;
}

// ======================= EDIT =======================
// [t0, t1, scene]. A null scene = covered by a transition below.
const SHOTS = [
  [0, 1.6, hook], [1.6, 4.0, kinetic], [4.0, 6.4, counter], [6.4, 8.8, cards], [8.8, 9.2, null], [9.2, DUR, endcard],
];
const shotAt = t => SHOTS.find(([a, b]) => t >= a && t < b) || SHOTS[SHOTS.length - 1];
function drawRaw(g, t) { const s = shotAt(t); if (s[2]) s[2](g, t - s[0]); }

// Whip pan: [start, end, fromScene, fromLocal, toScene] — motion-blurred by averaging 9 sub-frame renders.
const WHIPS = [[8.8, 9.2, cards, 2.4, endcard]];
function whip(g, t, [t0, t1, from, fromL, to]) {
  const half = (t1 - t0) / 2, n = 9; a2.clearRect(0, 0, W, H);
  for (let i = 0; i < n; i++) {
    const st = t - t0 + (i / (n - 1) - .5) * (3.2 / 30); let x, scene;
    if (st < half) { x = -eIO2(clamp(st / half)) * W * .6; scene = () => from(o, fromL); }
    else { x = (1 - eIO2(clamp((st - half) / half))) * W * .6; scene = () => to(o, 0); }
    o.setTransform(1, 0, 0, 1, 0, 0); o.clearRect(0, 0, W, H); o.save(); o.translate(x, 0); scene(); o.restore();
    a2.globalAlpha = 1 / (i + 1); a2.drawImage(off, 0, 0);
  }
  a2.globalAlpha = 1; g.drawImage(acc, 0, 0);
}

// CapCut layer: punch-in on every cut (+ extra beats), flash frames on drops, decaying impact shakes.
const PUNCH = SHOTS.map(s => s[0]).concat([.4, .8, 1.2, 4.8, 5.6]);
const DROPS = [1.6, 9.2], FLASH = [1.6, 4.0, 6.4, 9.2];
const SHAKES = [[1.2, .5, 1], [9.2, .8, 1.1]];            // [start, duration, amplitude]
function frame(t) {
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  let z = 1, sx = 0, sy = 0, rot = 0;
  for (const ct of PUNCH) { const q = t - ct; if (q >= 0 && q < .2) z = Math.max(z, 1 + .06 * (1 - q / .2) ** 2); }
  for (const [s0, d, amp] of SHAKES) { const q = t - s0; if (q >= 0 && q < d) { const e = Math.exp(-5 * q);
    sx += amp * M * .05 * e * Math.sin(2 * Math.PI * 5 * q); sy += amp * M * .037 * e * Math.cos(2 * Math.PI * 6.5 * q); rot += amp * .02 * e * Math.sin(2 * Math.PI * 5 * q + .6); } }
  c.save(); c.translate(W / 2 + sx, H / 2 + sy); c.rotate(rot); c.scale(z, z); c.translate(-W / 2, -H / 2);
  const w = WHIPS.find(([a, b]) => t >= a && t < b); if (w) whip(c, t, w); else drawRaw(c, t);
  c.restore();
  for (const f of FLASH) { const q = t - f; if (q >= 0 && q < 2 / 30) { c.fillStyle = DROPS.includes(f) ? '#fff' : 'rgba(255,255,255,.55)'; c.fillRect(0, 0, W, H); } }
}

// ======================= TIMELINE =======================
const tl = gsap.timeline({ paused: true }); const d = { t: 0 };
window.__timelines = window.__timelines || {};
Promise.all([FONT, MONOF].map(f => document.fonts.load(`80px "${f}"`))).then(() => {
  tl.to(d, { t: DUR, duration: DUR, ease: 'none', onUpdate: () => frame(d.t) }, 0);
  frame(0);
  window.__timelines['main'] = tl;
});
})();
