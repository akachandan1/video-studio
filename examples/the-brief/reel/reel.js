// Motion Prompt #001 #002 #003 #004 #005 #006 #007 #008 #010 #011 #015 #017 #019 #020 #022 #023 #024 #034 #038 #039 #040 #041 #043 #046 #056 #069 #085 (moves ported from their published specs) · MIT License (c) 2026 Shohei Ohtaki · https://showheyohtaki.github.io/motion-prompt/
// 'The Brief' — chop-cut showreel engine. One canvas, one shot list on a 150 BPM grid (beat 0.4 s).
// Every frame is a pure function of t. Motion Prompt moves are ported from their published specs (numbers cited inline).
// Layout is relative to the stage (W×H), so the same edit renders 16:9 and 9:16.
(() => {
const root = document.getElementById('root');
const W = +root.dataset.width, H = +root.dataset.height, M = Math.min(W, H), PORT = H > W;
const cv = document.getElementById('cv'), c = cv.getContext('2d');
const hud = document.getElementById('hud'), h = hud.getContext('2d');
const off = document.createElement('canvas'); off.width = W; off.height = H; const o = off.getContext('2d');
const acc = document.createElement('canvas'); acc.width = W; acc.height = H; const a2 = acc.getContext('2d');

// ---------- palette & type ----------
const INK = '#0d0d0f', PAPER = '#f2eee6', OR = '#ff5a1f', BLUE = '#2e5bff', LIME = '#c6f432', YEL = '#ffd21f', MINT = '#2fbf71', CYAN = '#22d3ee';
const F = (px, fam = 'Archivo Black') => `${Math.round(px)}px "${fam}"`;
const MONO = (px) => F(px, 'Space Mono');

// ---------- math ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const eIn3 = k => k * k * k, eOut3 = k => 1 - Math.pow(1 - k, 3), eIO3 = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
const eOut5 = k => 1 - Math.pow(1 - k, 5), eIO2 = k => k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
const backOut = (k, s = 1.70158) => 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2);
const backIn = (k, s = 1.70158) => (s + 1) * k * k * k - s * k * k;
const spring = (t, k, w) => t <= 0 ? 0 : 1 - Math.exp(-k * t) * Math.cos(w * t);   // #001/#008 spring form
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

// ---------- drawing helpers ----------
const rr = (g, x, y, w, hh, r) => { g.beginPath(); g.roundRect(x, y, w, hh, r); };
const text = (g, s, x, y, px, col, { fam = 'Archivo Black', align = 'center', base = 'middle', ls = 0 } = {}) => { g.font = F(px, fam); g.fillStyle = col; g.textAlign = align; g.textBaseline = base; if (ls) g.letterSpacing = ls + 'px'; g.fillText(s, x, y); g.letterSpacing = '0px'; };
const fit = (g, s, px, maxW, fam = 'Archivo Black') => { g.font = F(px, fam); const w = g.measureText(s).width; return w > maxW ? px * maxW / w : px; };
function dot(g, x, y, r, { grille = true } = {}) {                       // the Dot product, flat
  const gr = g.createRadialGradient(x, y, 0, x, y, r * 2.2); gr.addColorStop(0, 'rgba(255,90,31,.35)'); gr.addColorStop(1, 'rgba(255,90,31,0)'); g.fillStyle = gr; g.fillRect(x - r * 2.2, y - r * 2.2, r * 4.4, r * 4.4);
  g.fillStyle = OR; g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.fill();
  g.fillStyle = 'rgba(150,40,8,.35)'; g.beginPath(); g.arc(x + r * .16, y + r * .16, r * .9, 0, 6.2832); g.fill(); g.fillStyle = OR; g.beginPath(); g.arc(x - r * .05, y - r * .05, r * .86, 0, 6.2832); g.fill();
  if (grille) { g.fillStyle = 'rgba(70,22,8,.5)'; for (let row = -4; row <= 4; row++) for (let col = -4; col <= 4; col++) { const px = x + col * r * .19 + (row % 2) * r * .095, py = y + r * .12 + row * r * .16; if (Math.hypot(px - x, py - y) < r * .76 && py > y - r * .1) { g.beginPath(); g.arc(px, py, r * .034, 0, 6.2832); g.fill(); } } }
  g.fillStyle = 'rgba(255,255,255,.5)'; g.beginPath(); g.ellipse(x - r * .42, y - r * .45, r * .16, r * .1, -.6, 0, 6.2832); g.fill();
}
function radial(g, x, y, r0, r1, n, col, w, rot = 0) { g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; for (let i = 0; i < n; i++) { const a = rot + i / n * 6.2832; g.beginPath(); g.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); g.lineTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1); g.stroke(); } }
function phone(g, cx, cy, s, inner) {                                    // a phone frame of height s*M*0.82
  const ph = M * .82 * s, pw = ph * .48, x = cx - pw / 2, y = cy - ph / 2;
  g.fillStyle = '#16161a'; rr(g, x, y, pw, ph, pw * .14); g.fill(); g.strokeStyle = '#2c2c33'; g.lineWidth = M * .004; g.stroke();
  g.save(); rr(g, x + pw * .035, y + pw * .035, pw * .93, ph - pw * .07, pw * .11); g.clip(); g.fillStyle = '#f6f4ef'; g.fillRect(x, y, pw, ph); inner(g, x + pw * .035, y + pw * .035, pw * .93, ph - pw * .07); g.restore();
  g.fillStyle = '#16161a'; rr(g, cx - pw * .14, y + pw * .06, pw * .28, pw * .07, pw * .035); g.fill();
}

// ---------- persistent HUD: brief label, jump-cut clock (#041), move credits ----------
const CLOCK = [[0, '09:00'], [3.2, '09:08'], [6.4, '09:19'], [9.6, '09:31'], [12.8, '09:44'], [16.0, '09:53'], [19.2, '09:55'], [28.8, '09:57'], [35.2, '09:58'], [38.4, '09:59']];
const STAGE = [[0, 'BRIEF IN'], [3.2, 'STORYBOARD'], [6.4, 'TITLES'], [9.6, 'DATA'], [12.8, 'PRODUCT UI'], [16.0, 'CLIENT FEEDBACK'], [19.2, 'ART DIRECTION'], [26.4, 'EXPLAINER'], [28.8, 'SOUND'], [32.4, 'TRANSITIONS'], [35.2, 'RENDER'], [38.4, 'DELIVERED']];
const CRED = [[0, 3.2, '#001 Pop-in · #034 Handheld · #006 Typewriter · #024 Impact shake'], [3.2, 6.4, 'Storyboard · #004 Line draw · #043 Whip pan'],
  [6.4, 9.6, '#008 Kinetic type · #005 Mask reveal · #020 Zoom through'], [9.6, 12.8, '#007 Count-up · #010 Overshoot · #038 Speed ramp · #002 Stagger'],
  [12.8, 16.0, '#069 Skeleton · #085 Ripple · #056 Toast'], [16.0, 19.2, '#040 Freeze frame · #006 Typewriter · #046 Smash cut'],
  [19.2, 26.4, 'huashu-art-motion · 9 painting styles'], [26.4, 28.8, 'Kurzgesagt-style explainer'], [28.8, 32.4, 'Kokoro voice · caption kit (word-synced)'],
  [32.4, 35.2, '#017 Mask · #019 Liquid · #023 Glitch · #020 Zoom through'], [35.2, 40.0, '#039 Time-lapse · #024 Impact · #003 Burst · #015 Particles']];
const STYLES = ['VAN GOGH', 'LICHTENSTEIN', 'CHINESE INK', '8-BIT', 'KUSAMA', 'CUBISM', 'ROMAN MOSAIC', 'MONET', 'MATISSE'];
const at = (list, t) => { let v = list[0][1]; for (const [k, s] of list) if (t >= k) v = s; return v; };
function drawHud(t) {
  h.clearRect(0, 0, W, H); if (t >= 40.0) return;
  const pad = M * .045, sz = M * (PORT ? .026 : .02);
  // brief label (top-left)
  h.font = MONO(sz); h.textAlign = 'left'; h.textBaseline = 'middle';
  const lab = 'BRIEF · DOT LAUNCH FILM', lw = h.measureText(lab).width;
  h.fillStyle = 'rgba(13,13,15,.72)'; rr(h, pad - sz * .6, pad - sz * .9, lw + sz * 2.6, sz * 1.8, sz * .9); h.fill();
  h.fillStyle = OR; h.beginPath(); h.arc(pad + sz * .25, pad, sz * .32, 0, 6.2832); h.fill(); h.fillStyle = PAPER; h.fillText(lab, pad + sz * .9, pad + 1);
  // clock pill (top-right): jumps per section, colon blinks on the beat
  const clk = at(CLOCK, t), ck = clk.replace(':', Math.floor(t / .4) % 2 ? ' ' : ':'), cs = sz * 1.5;
  h.font = MONO(cs); const cw = h.measureText('00:00').width; const cx = W - pad - cw - cs * .8;
  const jump = CLOCK.find(([k]) => t >= k && t < k + .2); const jp = jump ? 1 + .25 * (1 - seg(t, jump[0], jump[0] + .2)) : 1;
  h.save(); h.translate(cx + (cw + cs * .8) / 2, pad + cs * .1); h.scale(jp, jp);
  h.fillStyle = t >= 38.4 ? MINT : t >= 16 && t < 19.2 ? '#e8322e' : PAPER; rr(h, -(cw + cs * .8) / 2, -cs * .75, cw + cs * .8, cs * 1.5, cs * .75); h.fill();
  h.fillStyle = INK; h.textAlign = 'center'; h.fillText(ck, 0, 1); h.restore();
  h.font = MONO(sz * .8); h.textAlign = 'right'; h.fillStyle = PAPER; h.globalAlpha = .85;
  h.fillStyle = 'rgba(13,13,15,.72)'; const st = at(STAGE, t), sw = h.measureText(st).width; rr(h, W - pad - sw - sz, pad + cs * .95, sw + sz, sz * 1.4, sz * .7); h.fill();
  h.fillStyle = PAPER; h.fillText(st, W - pad - sz * .5, pad + cs * .95 + sz * .72); h.globalAlpha = 1;
  // move credits (bottom-left) + art style tag during the blitz
  const cr = CRED.find(([a, b]) => t >= a && t < b);
  if (cr) { const k = seg(t, cr[0], cr[0] + .25) * (1 - seg(t, cr[1] - .15, cr[1])); h.globalAlpha = k; h.font = MONO(sz * .78); h.textAlign = 'left';
    const tw = h.measureText(cr[2]).width; const maxw = W - pad * 2; const s = tw > maxw - sz ? (maxw - sz) / tw : 1;
    h.save(); h.translate(pad, H - pad); h.scale(s, s); h.fillStyle = 'rgba(13,13,15,.72)'; rr(h, -sz * .6, -sz * .85, tw + sz * 1.2, sz * 1.7, sz * .85); h.fill(); h.fillStyle = PAPER; h.fillText(cr[2], 0, 1); h.restore(); h.globalAlpha = 1; }
  if (t >= 19.2 && t < 26.4) { const i = Math.floor((t - 19.2) / .8), lt = (t - 19.2) % .8, s = spring(lt, 7, 17); const tag = String(i + 1).padStart(2, '0') + '  ' + STYLES[i];
    h.save(); h.translate(W / 2, H * (PORT ? .82 : .86)); h.scale(s, s); h.font = F(M * .05); const tw = h.measureText(tag).width;
    h.fillStyle = INK; rr(h, -tw / 2 - M * .03, -M * .045, tw + M * .06, M * .09, M * .02); h.fill(); h.fillStyle = PAPER; h.textAlign = 'center'; h.fillText(tag, 0, M * .004); h.restore(); }
}

// ======================= SHOTS =======================
// HOOK — h1: notification on a handheld phone (#001 pop-in springs, #034 handheld sums of sines)
function hookPhone(g, t) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H);
  const T = 2 * Math.PI * t / 4.7, yaw = .016 * Math.sin(3 * T) + .008 * Math.sin(7 * T + 1), roll = .02 * Math.sin(5 * T + 1) + .008 * Math.sin(11 * T + 3);
  g.save(); g.translate(W / 2 + yaw * W * .6, H / 2 + (.012 * Math.sin(4 * T + 2)) * H * .5); g.rotate(roll);
  phone(g, 0, 0, PORT ? .95 : .9, (g, x, y, w, hh) => {
    g.fillStyle = '#1d1f2b'; g.fillRect(x, y, w, hh); text(g, '9:00', x + w / 2, y + hh * .2, w * .26, PAPER, { fam: 'Space Mono' });
    const p = spring(t - .1, 6.5, 15), rot = -.35 * (1 - spring(t - .1, 6, 11));
    g.save(); g.translate(x + w / 2, y + hh * .48); g.scale(p, p); g.rotate(rot);
    g.fillStyle = PAPER; rr(g, -w * .44, -w * .17, w * .88, w * .34, w * .07); g.fill();
    g.fillStyle = OR; g.beginPath(); g.arc(-w * .3, 0, w * .08, 0, 6.2832); g.fill();
    text(g, 'NEW BRIEF', -w * .17, -w * .05, w * .085, INK, { align: 'left' }); text(g, 'Dot Audio · 9:00', -w * .17, w * .06, w * .055, '#6b675e', { fam: 'Space Mono', align: 'left' });
    const b = spring(t - .38, 7, 17); g.save(); g.translate(w * .4, -w * .16); g.scale(b, b); g.fillStyle = YEL; g.beginPath(); g.arc(0, 0, w * .055, 0, 6.2832); g.fill(); text(g, '1', 0, 1, w * .06, INK); g.restore();
    g.restore();
  });
  g.restore();
}
// h2: typewriter brief (#006: chars settle from 1.35 = 1 + .35e^(−16t); cursor; send disc spring; press)
function hookType(g, t) {
  g.fillStyle = '#1d1f2b'; g.fillRect(0, 0, W, H);
  const msg = 'Launch film for DOT.', n = msg.length, per = .028, fw = Math.min(W * .86, M * 1.35), fh = M * .14, x0 = W / 2 - fw / 2, y0 = H / 2 - fh / 2;
  text(g, 'Dot Audio', W / 2, y0 - M * .14, M * .04, PAPER, { fam: 'Space Mono' }); text(g, 'Deadline today. Can you deliver?', W / 2, y0 - M * .075, M * .032, '#9aa0b5', { fam: 'Space Mono' });
  g.fillStyle = '#fff'; rr(g, x0, y0, fw, fh, fh / 2); g.fill();
  const px = fit(g, msg, M * .07, fw * .7); g.font = F(px); let x = x0 + fh * .55; const shown = clamp(Math.floor((t - .02) / per) + 1, 0, n);
  for (let i = 0; i < shown; i++) { const ch = msg[i], cw = g.measureText(ch).width, s = 1 + .35 * Math.exp(-16 * (t - .02 - i * per)); g.save(); g.translate(x + cw / 2, y0 + fh / 2); g.scale(s, s); text(g, ch, 0, 2, px, INK); g.restore(); x += cw; }
  if (t < .62 || Math.floor(t / .47) % 2 === 0) { g.fillStyle = OR; g.fillRect(x + 4, y0 + fh * .25, M * .006, fh * .5); }
  const bx = x0 + fw - fh * .55, by = y0 + fh / 2, bp = spring(t - .62, 6.5, 15), press = 1 - .2 * Math.sin(Math.PI * seg(t, .66, .76));
  g.fillStyle = '#d6d2c8'; g.beginPath(); g.arc(bx, by, fh * .36, 0, 6.2832); g.fill();
  g.save(); g.translate(bx, by); g.scale(bp * press, bp * press); g.fillStyle = BLUE; g.beginPath(); g.arc(0, 0, fh * .36, 0, 6.2832); g.fill();
  g.fillStyle = '#fff'; g.beginPath(); g.moveTo(-fh * .12, -fh * .14); g.lineTo(fh * .16, 0); g.lineTo(-fh * .12, fh * .14); g.closePath(); g.fill(); g.restore();
}
// h3: DEADLINE slab drops, frame shakes (#024: fall cubic-in, stretch 1.12; shake x 15e^(−5t)sin(2π5t), y 11e^(−5t)cos(2π6.5t), rot .02…)
function hookDeadline(g, t) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H);
  const land = .16, k = eIn3(seg(t, 0, land)), y = lerp(-H * .4, H * .5, k), sq = t > land ? .22 * Math.exp(-14 * (t - land)) * Math.cos(20 * (t - land)) : 0;
  const sw = Math.min(W * .86, M * 1.5), sh = M * .26;
  g.save(); g.translate(W / 2, y + sh / 2); g.scale(1 + sq, (t < land ? 1.12 : 1) * (1 - sq)); g.fillStyle = YEL; rr(g, -sw / 2, -sh, sw, sh, M * .03); g.fill();
  text(g, 'DEADLINE: 60 MIN', 0, -sh / 2, fit(g, 'DEADLINE: 60 MIN', M * .11, sw * .9), INK); g.restore();
  if (t > land) { const q = t - land; g.globalAlpha = clamp(1 - q / .55); for (let i = 0; i < 6; i++) { const a = Math.PI + (i + .5) / 6 * Math.PI; g.strokeStyle = PAPER; g.lineWidth = M * .006; const r0 = sw * .5 + q * M * .5; g.beginPath(); g.moveTo(W / 2 + Math.cos(a) * r0 * .9, H * .5 + sh / 2 + Math.sin(a) * M * .05); g.lineTo(W / 2 + Math.cos(a) * (r0 + M * .06), H * .5 + sh / 2 + Math.sin(a) * M * .09); g.stroke(); } g.globalAlpha = 1; }
  text(g, '09:00', W / 2, H * .5 + sh, M * .07, PAPER, { fam: 'Space Mono' });
}
// h4: clock punch-in with RGB split building to the drop
function hookClock(g, t) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H); const z = 1 + eIn3(seg(t, 0, .8)) * .9, sp = seg(t, .2, .8) * M * .02;
  const s = '09:00:0' + Math.min(2, Math.floor(t / .4)); g.save(); g.translate(W / 2, H / 2); g.scale(z, z);
  const px = fit(g, s, M * .2, W * .9, 'Space Mono'); g.globalCompositeOperation = 'lighter';
  text(g, s, -sp, 0, px, '#c02b0b', { fam: 'Space Mono' }); text(g, s, sp, 0, px, '#0b6b8a', { fam: 'Space Mono' }); g.globalCompositeOperation = 'source-over'; text(g, s, 0, 0, px, PAPER, { fam: 'Space Mono' }); g.restore();
}

// STORYBOARD — pencil line-draw panels (#004 line draw), boiling lines at 8 fps
function pencil(g, pts, k, lt, w = M * .006) { if (k <= 0) return; const n = Math.max(2, Math.floor(pts.length * k)); g.strokeStyle = '#2b2a28'; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round';
  const b = Math.floor(lt * 8); g.beginPath(); for (let i = 0; i < n; i++) { const j = hash(i * 7 + b) - .5; const [x, y] = pts[i]; i ? g.lineTo(x + j * M * .003, y + j * M * .003) : g.moveTo(x, y); } g.stroke(); }
const circlePts = (x, y, r, n = 60) => Array.from({ length: n + 1 }, (_, i) => [x + Math.cos(i / n * 6.2832 - 1.6) * r, y + Math.sin(i / n * 6.2832 - 1.6) * r]);
const rectPts = (x, y, w, hh) => [[x, y], [x + w, y], [x + w, y + hh], [x, y + hh], [x, y]].flatMap((p, i, a) => i ? Array.from({ length: 12 }, (_, k) => [lerp(a[i - 1][0], p[0], (k + 1) / 12), lerp(a[i - 1][1], p[1], (k + 1) / 12)]) : [p]);
function panel(g, i, x, y, w, hh, k, lt) {
  g.fillStyle = '#fbf8f1'; g.fillRect(x, y, w, hh); g.strokeStyle = '#2b2a28'; g.lineWidth = M * .004; g.strokeRect(x, y, w, hh);
  text(g, '0' + (i + 1), x + w * .07, y + hh * .1, Math.min(w, hh) * .09, OR, { fam: 'Space Mono', align: 'left' });
  const cx = x + w / 2, cy = y + hh / 2, s = Math.min(w, hh);
  if (i === 0) { pencil(g, circlePts(cx, cy - s * .08, s * .22), k, lt); pencil(g, rectPts(cx - s * .16, cy + s * .14, s * .32, s * .14), clamp(k * 1.4 - .4), lt); }
  if (i === 1) { pencil(g, rectPts(cx - s * .14, cy - s * .32, s * .28, s * .64), k, lt); pencil(g, circlePts(cx, cy - s * .05, s * .07), clamp(k * 1.5 - .5), lt); pencil(g, rectPts(cx - s * .1, cy + s * .14, s * .2, s * .07), clamp(k * 1.5 - .5), lt); }
  if (i === 2) { pencil(g, circlePts(cx, cy - s * .02, s * .16), k, lt); pencil(g, [[cx - s * .4, cy + s * .3], [cx - s * .22, cy + s * .12], [cx - s * .14, cy + s * .14]], clamp(k * 1.5 - .5), lt); pencil(g, [[cx + s * .4, cy + s * .3], [cx + s * .22, cy + s * .12], [cx + s * .14, cy + s * .14]], clamp(k * 1.5 - .5), lt); }
  if (i === 3) { g.globalAlpha = k; text(g, 'dot.', cx, cy, s * .26, '#2b2a28'); g.globalAlpha = 1; g.fillStyle = OR; g.beginPath(); g.arc(cx + s * .21, cy + s * .07, s * .035 * clamp(k * 2 - 1), 0, 6.2832); g.fill(); }
}
function storyboard(g, t) {                              // t local 0..3.2
  g.fillStyle = '#efe9dc'; g.fillRect(0, 0, W, H);
  if (t < .4) { const s = 3.4 - 2.4 * eIn3(seg(t, 0, .18)); g.save(); g.translate(W / 2, H / 2); g.scale(s, s); text(g, 'STORYBOARD', 0, 0, fit(g, 'STORYBOARD', M * .16, W * .9), INK); g.restore(); return; }
  if (t < 2.0) { const i = Math.floor((t - .4) / .4), lt = (t - .4) % .4, pw = PORT ? W * .86 : W * .62, ph = pw * .62, z = 1.06 - .06 * eOut3(seg(lt, 0, .3));
    g.save(); g.translate(W / 2, H / 2); g.scale(z, z); panel(g, i, -pw / 2, -ph / 2, pw, ph, eOut3(seg(lt, 0, .34)), t); g.restore(); return; }
  const k = eIO3(seg(t, 2.0, 2.5)), cols = PORT ? 1 : 2, rows = PORT ? 4 : 2, gap = M * .03, pw = PORT ? W * .6 : W * .38, ph = PORT ? (H * .74 - gap * 3) / 4 : pw * .56;
  const tw = cols * pw + (cols - 1) * gap, th = rows * ph + (rows - 1) * gap;
  for (let i = 0; i < 4; i++) { const cx = i % cols, ry = Math.floor(i / cols), x = W / 2 - tw / 2 + cx * (pw + gap), y = H / 2 - th / 2 + ry * (ph + gap), s = lerp(1.6, 1, k);
    g.save(); g.translate(W / 2, H / 2); g.scale(s, s); g.translate(-W / 2, -H / 2); panel(g, i, x, y, pw, ph, 1, t); g.restore(); }
}

// TITLES — #008 kinetic (stretch / slam / spin / bounce) then #005 mask reveal, then #020 zoom through the O of DOT
function titles(g, t) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H); const px = M * (PORT ? .2 : .19);
  const word = (s, col) => ({ s, col, px: fit(g, s, px, W * .9) });
  if (t < 1.6) { const i = Math.floor(t / .4), lt = t % .4, W8 = [word('SMALL.', BLUE), word('LOUD.', OR), word('ROUND.', MINT), word('ORANGE.', YEL)][i];
    const out = seg(lt, .34, .4); g.globalAlpha = 1 - out; g.save(); g.translate(W / 2, H / 2 - out * M * .05);
    if (i === 0) { const sx = .3 + .7 * spring(lt, 4.2, 12); g.scale(sx, 1 / Math.sqrt(sx)); text(g, W8.s, 0, 0, W8.px, W8.col); }
    if (i === 1) { const s = 3.4 - 2.4 * eIn3(seg(lt, .0, .12)), q = lt - .12, sh = q > 0 ? 10 * Math.exp(-9 * q) * Math.sin(38 * q) : 0, sq = q > 0 ? .2 * Math.exp(-11 * q) : 0;
      g.translate(sh * M / 540, 0); g.rotate(-.08); g.scale(s * (1 + sq * .5), s * (1 - sq)); text(g, W8.s, 0, 0, W8.px, W8.col);
      if (q > 0 && q < .4) { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = (1 - out) * (1 - q / .4); radial(g, W / 2, H / 2, M * (.32 + q), M * (.4 + q * 1.2), 8, PAPER, M * .008); } }
    if (i === 2) { g.font = F(W8.px); const tw = g.measureText(W8.s).width; let x = -tw / 2; [...W8.s].forEach((ch, k) => { const q = lt - k * .035, cw = g.measureText(ch).width, r = -2 * Math.PI * (1 - backOut(clamp(q / .3), 1.3)), s = eOut3(clamp(q / .12));
      g.save(); g.translate(x + cw / 2, 0); g.rotate(r); g.scale(s, s); text(g, ch, 0, 0, W8.px, W8.col); g.restore(); x += cw; }); }
    if (i === 3) { g.font = F(W8.px); const tw = g.measureText(W8.s).width; let x = -tw / 2; [...W8.s].forEach((ch, k) => { const q = Math.max(0, lt - k * .03), cw = g.measureText(ch).width, b = Math.abs(Math.sin(Math.PI * q / .2)) * Math.exp(-2.6 * q * 3), y = -M * .1 * b;
      const sq = b < .08 ? .16 * (1 - b / .08) : 0; g.save(); g.translate(x + cw / 2, y); g.scale(1 + sq * .5, 1 - sq); text(g, ch, 0, 0, W8.px, W8.col); g.restore(); x += cw; }); }
    g.restore(); g.globalAlpha = 1; return; }
  // mask reveal (#005 timings compressed ×0.5): line grows from centre, top text rises from behind it, sub drops below
  const lt = t - 1.6, lineW = Math.min(W * .8, M * 1.3) * eIO3(seg(lt, .05, .25)), ly = H / 2 + M * .02;
  const topPx = fit(g, 'MEET DOT.', M * .2, W * .86), subPx = fit(g, 'The speaker that listens.', M * .055, W * .8, 'Space Mono');
  g.fillStyle = OR; g.fillRect(W / 2 - lineW / 2, ly - M * .004, lineW, M * .008);
  g.save(); g.beginPath(); g.rect(0, 0, W, ly - M * .008); g.clip(); text(g, 'MEET DOT.', W / 2, ly - topPx * .55 + (1 - eOut5(seg(lt, .17, .5))) * topPx, topPx, PAPER); g.restore();
  g.save(); g.beginPath(); g.rect(0, ly + M * .008, W, H); g.clip(); text(g, 'The speaker that listens.', W / 2, ly + subPx * 1.1 - (1 - eOut5(seg(lt, .27, .57))) * subPx * 1.6, subPx, YEL, { fam: 'Space Mono' }); g.restore();
}
function titlesZoom(g, t, next) {                        // #020 zoom through the O of DOT (t local 0..0.4 at 9.2–9.6)
  g.save(); const topPx = fit(g, 'MEET DOT.', M * .2, W * .86); g.font = F(topPx); const full = g.measureText('MEET DOT.').width, pre = g.measureText('MEET D').width, ow = g.measureText('O').width;
  const ly = H / 2 + M * .02, ox = W / 2 - full / 2 + pre + ow / 2, oy = ly - topPx * .55, hole = ow * .22, maxS = 1.08 * Math.hypot(W, H) / hole;
  const p = .8 * eIn3(seg(t, 0, .3)) + .2 * eOut3(seg(t, .3, .4)), s = Math.pow(maxS, p);
  g.translate(ox, oy); g.scale(s, s); g.translate(-ox, -oy); titles(g, 1.6 + .8);
  g.beginPath(); g.arc(ox, oy, hole, 0, 6.2832); g.clip(); g.translate(ox, oy); g.scale(1 / maxS * s / s, 1 / maxS * s / s); g.translate(-W / 2, -H / 2); next(g, 0); g.restore();
}

// DATA — #038 speed ramp remaps section time; #007 count-up; #002 bars; #010 gauge overshoot
const ramp = lt => { const a = 1.2, b = 1.9; if (lt < a) return lt * 2.4; if (lt > b) return a * 2.4 + .5 * (b - a) * (2.4 + .25) + (lt - b) * .25 + Math.max(0, lt - 2.4) * .75 * 2; const k = (lt - a) / (b - a), e = eIO2(k); return a * 2.4 + (lt - a) * lerp(2.4, .25, e); };
function data(g, lt) {
  const ft = ramp(lt), speed = lt < 1.2 ? 2.4 : lt < 1.9 ? lerp(2.4, .25, eIO2((lt - 1.2) / .7)) : lt < 2.4 ? .25 : 2.4;
  g.fillStyle = PAPER; g.fillRect(0, 0, W, H);
  const p = clamp((ft - .2) / 2.5), val = Math.round(2480000 * (1 - Math.pow(1 - p, 4))), landed = p >= 1, bounce = landed ? 1 + .07 * Math.exp(-7 * (ft - 2.7)) * Math.cos(15 * (ft - 2.7)) : 1;
  const numPx = fit(g, '2,480,000', M * (PORT ? .17 : .16), W * .86), ny = H * (PORT ? .28 : .32);
  g.save(); g.translate(W / 2, ny); g.scale(bounce, bounce); text(g, val.toLocaleString('en-US'), 0, 0, numPx, landed ? OR : INK); g.restore();
  text(g, 'PRE-ORDERS · SAMPLE DATA', W / 2, ny + numPx * .72, M * .035, '#4a4740', { fam: 'Space Mono' });
  // stagger bars (#002)
  const n = 7, bw = Math.min(W * .1, M * .09), gap = bw * .45, tot = n * bw + (n - 1) * gap, by = H * (PORT ? .62 : .82);
  for (let i = 0; i < n; i++) { const k = backOut(clamp((ft - .5 - i * .08) / .5), 1.6), hh = M * (.08 + .32 * (i + 1) / n) * Math.max(0, k); g.fillStyle = i === n - 1 ? OR : '#c9c3b6'; rr(g, W / 2 - tot / 2 + i * (bw + gap), by - hh, bw, hh, bw * .12); g.fill(); }
  // gauge (#010): 0.7 × (1 − e^(−4.6t)·cos(10.5t))
  if (!PORT || true) { const gx = PORT ? W / 2 : W * .82, gy = PORT ? H * .82 : H * .62, R = M * (PORT ? .16 : .13), gt = ft - 1.0, v = gt > 0 ? .7 * (1 - Math.exp(-4.6 * gt) * Math.cos(10.5 * gt)) : 0;
    g.lineCap = 'round'; g.lineWidth = M * .03; g.strokeStyle = '#ddd7ca'; g.beginPath(); g.arc(gx, gy, R, Math.PI, 2 * Math.PI); g.stroke();
    g.strokeStyle = BLUE; g.beginPath(); g.arc(gx, gy, R, Math.PI, Math.PI + Math.PI * Math.min(v, .7)); g.stroke(); if (v > .7) { g.strokeStyle = OR; g.beginPath(); g.arc(gx, gy, R, Math.PI * 1.7, Math.PI * (1 + v)); g.stroke(); }
    g.strokeStyle = YEL; g.lineWidth = M * .008; const ta = Math.PI * 1.7; g.beginPath(); g.moveTo(gx + Math.cos(ta) * R * .8, gy + Math.sin(ta) * R * .8); g.lineTo(gx + Math.cos(ta) * R * 1.2, gy + Math.sin(ta) * R * 1.2); g.stroke();
    const na = Math.PI * (1 + v); g.strokeStyle = INK; g.lineWidth = M * .01; g.beginPath(); g.moveTo(gx, gy); g.lineTo(gx + Math.cos(na) * R * .9, gy + Math.sin(na) * R * .9); g.stroke();
    text(g, 'BASS', gx, gy + R * .3, M * .03, '#4a4740', { fam: 'Space Mono' }); }
  // speed readout (#038 top-right graph)
  const sx = W * (PORT ? .08 : .06), sy = H * (PORT ? .9 : .9); text(g, '×' + speed.toFixed(1), sx, sy, M * .04, BLUE, { fam: 'Space Mono', align: 'left' });
}

// PRODUCT UI — #069 skeleton (shine band every 0.9 s) → content; cursor; #085 ripple; #056 toast (slide 0.35 s easeOutCubic, time bar)
function ui(g, lt, frozen = false) {
  g.fillStyle = '#16171c'; g.fillRect(0, 0, W, H);
  const T = 2 * Math.PI * lt / 4.7, tilt = PORT ? 0 : .04 * Math.sin(T);
  g.save(); g.translate(W / 2, H / 2); g.rotate(tilt);
  let btn = null;
  phone(g, 0, 0, PORT ? 1.0 : .95, (g, x, y, w, hh) => {
    g.fillStyle = '#f6f4ef'; g.fillRect(x, y, w, hh);
    text(g, 'Dot', x + w * .08, y + hh * .09, w * .11, INK, { align: 'left' }); text(g, 'Smart speaker · Orange', x + w * .08, y + hh * .14, w * .045, '#6b675e', { fam: 'Space Mono', align: 'left' });
    const loaded = lt >= .8, shine = (lt % .9) / .9;
    const block = (bx, by, bw, bh, draw) => { if (!loaded) { g.fillStyle = '#e9e7e5'; rr(g, bx, by, bw, bh, w * .04); g.fill(); g.save(); rr(g, bx, by, bw, bh, w * .04); g.clip(); const sxp = lerp(x - w * .4, x + w * 1.4, shine), gr = g.createLinearGradient(sxp - w * .2, 0, sxp + w * .2, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.5, 'rgba(255,255,255,.75)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(bx, by, bw, bh); g.restore(); } else draw(); };
    block(x + w * .08, y + hh * .19, w * .84, hh * .34, () => { g.fillStyle = '#efe7dc'; rr(g, x + w * .08, y + hh * .19, w * .84, hh * .34, w * .05); g.fill(); dot(g, x + w / 2, y + hh * .36, w * .2); });
    block(x + w * .08, y + hh * .56, w * .5, hh * .04, () => text(g, '₹4,999', x + w * .08, y + hh * .58, w * .09, INK, { align: 'left' }));
    block(x + w * .08, y + hh * .62, w * .7, hh * .03, () => text(g, '12 h battery · 40 mm driver', x + w * .08, y + hh * .635, w * .045, '#6b675e', { fam: 'Space Mono', align: 'left' }));
    const bx = x + w * .08, by = y + hh * .76, bw = w * .84, bh = hh * .085; btn = [bx, by, bw, bh];
    block(bx, by, bw, bh, () => { g.fillStyle = BLUE; rr(g, bx, by, bw, bh, bh / 2); g.fill(); text(g, 'Pre-order', bx + bw / 2, by + bh / 2, bh * .42, '#fff');
      const ct = lt - 1.6; if (ct > 0) { g.save(); rr(g, bx, by, bw, bh, bh / 2); g.clip(); const cxp = bx + bw * .45, far = Math.hypot(bw * .55, bh), r = far * eOut3(clamp(ct / .6)); g.fillStyle = `rgba(255,255,255,${.4 * (1 - seg(ct, .3, .8))})`; g.beginPath(); g.arc(cxp, by + bh / 2, r, 0, 6.2832); g.fill(); g.restore(); } });
    // toast
    const tt = lt - 1.8; if (tt > 0) { const sl = (1 - eOut3(clamp(tt / .35))) * w * .9, tw = w * .78, th = hh * .07, tx = x + w - tw - w * .04 + sl, ty = y + hh * .88;
      g.fillStyle = '#26282c'; rr(g, tx, ty, tw, th, th * .3); g.fill(); g.fillStyle = BLUE; g.beginPath(); g.arc(tx + th * .55, ty + th / 2, th * .26, 0, 6.2832); g.fill();
      g.strokeStyle = '#fff'; g.lineWidth = th * .07; g.beginPath(); g.moveTo(tx + th * .43, ty + th * .5); g.lineTo(tx + th * .52, ty + th * .6); g.lineTo(tx + th * .68, ty + th * .4); g.stroke();
      text(g, 'Pre-ordered', tx + th, ty + th / 2, th * .36, '#fff', { fam: 'Space Mono', align: 'left' }); g.fillStyle = BLUE; g.fillRect(tx, ty + th - th * .05, tw * (1 - seg(tt, .35, 1.6)), th * .05); }
  });
  g.restore();
  // cursor = the dot (screen space): centre → button → rest
  if (btn) { const [bx, by, bw, bh] = btn, toX = W / 2 + (bx + bw * .45), toY = H / 2 + (by + bh / 2);
    const k = eIO3(seg(lt, 1.0, 1.55)), cxp = lerp(W * .78, toX, k), cyp = lerp(H * .3, toY, k), pr = 1 - .2 * Math.sin(Math.PI * seg(lt, 1.55, 1.7));
    g.fillStyle = OR; g.beginPath(); g.arc(cxp, cyp, M * .022 * pr, 0, 6.2832); g.fill(); g.strokeStyle = 'rgba(255,90,31,.45)'; g.lineWidth = M * .004; const rq = seg(lt, 1.58, 1.95); if (rq > 0 && rq < 1) { g.beginPath(); g.arc(cxp, cyp, M * (.022 + .05 * rq), 0, 6.2832); g.stroke(); } }
  if (frozen) { const fa = clamp(frozen / .12); g.strokeStyle = BLUE; g.lineWidth = M * .01; g.globalAlpha = fa; g.strokeRect(M * .005, M * .005, W - M * .01, H - M * .01);
    const pw = M * .1, ph = M * .06; g.fillStyle = '#fff'; rr(g, W / 2 - pw / 2, H * .9 - ph / 2, pw, ph, ph * .25); g.fill(); g.fillStyle = BLUE; g.fillRect(W / 2 - pw * .17, H * .9 - ph * .28, pw * .1, ph * .56); g.fillRect(W / 2 + pw * .07, H * .9 - ph * .28, pw * .1, ph * .56);
    text(g, 'FREEZE', W - M * .05, H - M * .05, M * .03, BLUE, { fam: 'Space Mono', align: 'right' }); g.globalAlpha = 1; }
}

// BREAK — freeze (#040) + client bubble types (#006 rhythm) + silence + SMASH (#046)
function bubble(g, msg, lt) {
  const shown = Math.floor(clamp((lt - .5) / .9) * msg.length), w = Math.min(W * .8, M * 1.2), pad = M * .04, px = M * (PORT ? .052 : .046);
  const y = H * (PORT ? .7 : .72); g.font = F(px, 'Space Mono');
  const typing = lt < .5; const bh = px * 2.6, bx = W / 2 - w / 2;
  g.fillStyle = 'rgba(255,255,255,.97)'; rr(g, bx, y - bh / 2, w, bh, bh * .3); g.fill(); g.beginPath(); g.moveTo(bx + w * .1, y + bh / 2); g.lineTo(bx + w * .06, y + bh / 2 + px * .8); g.lineTo(bx + w * .18, y + bh / 2); g.fill();
  text(g, 'Dot Audio', bx + pad, y - bh / 2 - px * .55, px * .6, PAPER, { fam: 'Space Mono', align: 'left' });
  if (typing) { for (let i = 0; i < 3; i++) { g.fillStyle = '#9a958a'; g.beginPath(); g.arc(W / 2 - px + i * px, y + Math.sin(lt * 18 + i) * px * .12, px * .18, 0, 6.2832); g.fill(); } return; }
  const s = msg.slice(0, shown), fs = fit(g, msg, px, w - pad * 2, 'Space Mono'); text(g, s, bx + pad, y + 2, fs, INK, { fam: 'Space Mono', align: 'left' });
}
function breakdown(g, t) {                               // t local 0..3.2 (global 16.0–19.2)
  if (t < 1.6) { ui(g, 2.8, t + .001); bubble(g, 'love it. can it be more ARTISTIC?', t - .1); return; }
  if (t < 2.4) { g.fillStyle = '#050506'; g.fillRect(0, 0, W, H); const z = 1 + (t - 1.6) * .08; g.save(); g.translate(W / 2, H / 2); g.scale(z, z); text(g, '“more artistic?”', 0, 0, fit(g, '“more artistic?”', M * .07, W * .8, 'Instrument Serif'), '#8d887e', { fam: 'Instrument Serif' }); g.restore(); return; }
  // SMASH CUT: tight, rolled −0.12 rad, shake ±0.03 rad @6 Hz, 18 radial lines
  const q = t - 2.4, s = 3.2 - 2.2 * eIn3(seg(q, 0, .1)); g.fillStyle = OR; g.fillRect(0, 0, W, H);
  radial(g, W / 2, H / 2, M * .35, Math.hypot(W, H), 18, 'rgba(13,13,15,.18)', M * .05, q * .4);
  g.save(); g.translate(W / 2, H / 2); g.rotate(-.12 + .03 * Math.sin(2 * Math.PI * 6 * q)); g.scale(s, s); text(g, 'BET.', 0, 0, fit(g, 'BET.', M * .42, W * .9), INK); g.restore();
  if (q > .2) { const i = Math.floor((q - .2) / .075) % STYLES.length; g.fillStyle = INK; g.globalAlpha = .9; text(g, STYLES[i], W / 2, H * .82, M * .05, PAPER); g.globalAlpha = 1; }
}

// TRANSITIONS RUN (32.4–35.2): #017 star mask, #019 liquid, #023 glitch, #020 zoom-through → render screen
function card(g, bg, fg, word, sub) { g.fillStyle = bg; g.fillRect(0, 0, W, H); dot(g, W / 2, H * (PORT ? .4 : .38), M * .14); text(g, word, W / 2, H * (PORT ? .66 : .74), fit(g, word, M * .14, W * .86), fg); if (sub) text(g, sub, W / 2, H * (PORT ? .73 : .86), M * .035, fg, { fam: 'Space Mono' }); }
const SC = [g => card(g, OR, INK, 'LOUD.'), g => card(g, BLUE, PAPER, 'CLEAR.'), g => card(g, LIME, INK, 'SMART.'), g => card(g, PAPER, INK, 'DOT.')];
function starPath(g, x, y, r, rot) { g.beginPath(); for (let i = 0; i < 10; i++) { const a = rot - Math.PI / 2 + i * Math.PI / 5, rr2 = i % 2 ? r * .45 : r; i ? g.lineTo(x + Math.cos(a) * rr2, y + Math.sin(a) * rr2) : g.moveTo(x + Math.cos(a) * rr2, y + Math.sin(a) * rr2); } g.closePath(); }
function transRun(g, t) {                                 // t local 0..2.8, 0.7 s per transition
  const i = Math.min(3, Math.floor(t / .7)), lt = t - i * .7, k = eIO3(seg(lt, .12, .62));
  if (i === 0) { SC[0](g); const r = 1150 * M / 540 * k, cx = W / 2, cy = H * (PORT ? .4 : .38); if (k > 0) { g.save(); starPath(g, cx, cy, r, 1.2 * k); g.clip(); SC[1](g); g.restore(); if (k < 1) { starPath(g, cx, cy, r, 1.2 * k); g.strokeStyle = '#fff'; g.lineWidth = M * .013; g.stroke(); } } return; }
  if (i === 1) { SC[1](g); const L1 = eIO2(seg(lt, .05, .45)), L2 = eIO2(seg(lt, .2, .62)); const front = (p) => lerp(-H * .2, H * 1.25, p);
    const liquid = (p, fill) => { const fy = front(p), st = Math.sin(Math.PI * p); g.beginPath(); g.moveTo(0, 0); g.lineTo(W, 0); g.lineTo(W, fy);
      for (let x = W; x >= 0; x -= W / 60) g.lineTo(x, fy + Math.sin(x / W * 9 + p * 6) * M * .024 * st + Math.sin(x / W * 17) * M * .015 * st); g.closePath(); fill();
      for (let d = 0; d < 7; d++) { const dx = (d + .5) / 7 * W + Math.sin(d * 2.1) * W * .04, dw = M * (.055 + .045 * hash(d)), len = M * (.055 + .15 * hash(d + 9)) * (.25 + .9 * st); g.beginPath(); g.roundRect(dx - dw / 2, fy - M * .02, dw, len + M * .02, [0, 0, dw / 2, dw / 2]); fill(); } };
    liquid(L1, () => { g.fillStyle = OR; g.fill(); }); if (L2 > 0) { g.save(); g.beginPath(); const fy = front(L2); g.rect(0, 0, W, Math.max(0, fy)); g.clip(); SC[2](g); g.restore(); } return; }
  if (i === 2) { const stepI = Math.floor(lt / .14), on = lt > .05 && lt < .6, scene = lt < .35 ? 2 : 3; SC[scene](g);
    if (on) { const r = n => hash(stepI * 13 + n); const sh = M * (.013 + .017 * r(1)); o.clearRect(0, 0, W, H); o.drawImage(cv, 0, 0);
      g.globalCompositeOperation = 'multiply'; g.fillStyle = '#ff6b5a'; g.globalAlpha = .45; g.drawImage(off, -sh, M * .004); g.fillStyle = CYAN; g.drawImage(off, sh, -M * .004); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
      for (let s2 = 0; s2 < 2 + Math.floor(r(2) * 3); s2++) { const y = H * (.2 + .6 * r(3 + s2)), hh = M * (.02 + .045 * r(7 + s2)), dx = M * (.035 + .085 * r(11 + s2)) * (r(5 + s2) > .5 ? 1 : -1); g.drawImage(off, 0, y, W, hh, dx, y, W, hh); }
      [[OR, 1], [CYAN, 2], [YEL, 3]].forEach(([col, n]) => { g.fillStyle = col; g.fillRect(W * r(20 + n), H * r(30 + n), M * (.06 + .16 * r(40 + n)), M * (.01 + .012 * r(50 + n))); }); } return; }
  // zoom through the O of DOT. into the render screen
  SC[3](g); const p = .8 * eIn3(seg(lt, .05, .5)) + .2 * eOut3(seg(lt, .5, .7)), px = fit(g, 'DOT.', M * .14, W * .86); g.font = F(px);
  const full = g.measureText('DOT.').width, pre = g.measureText('D').width, ow = g.measureText('O').width, ox = W / 2 - full / 2 + pre + ow / 2, oy = H * (PORT ? .66 : .74), hole = ow * .22, maxS = 1.08 * Math.hypot(W, H) / hole, s = Math.pow(maxS, p);
  o.clearRect(0, 0, W, H); o.drawImage(cv, 0, 0); g.fillStyle = INK; g.fillRect(0, 0, W, H); g.save(); g.translate(ox, oy); g.scale(s, s); g.translate(-ox, -oy); g.drawImage(off, 0, 0); g.restore();
  if (p > .6) { g.globalAlpha = seg(p, .6, 1); render(g, 0); g.globalAlpha = 1; }
}

// RENDER + DELIVERED — #039 clock steps, #024 slam, #003 burst, #015 particles
function render(g, lt) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H); const k = clamp(lt / 2.6), pe = 1 - Math.pow(1 - k, 2.2), fr = Math.min(1350, Math.round(pe * 1350)), bw = Math.min(W * .8, M * 1.3), bh = M * .03, by = H / 2;
  text(g, 'launch_film_dot.mp4', W / 2, by - M * .12, M * .045, PAPER, { fam: 'Space Mono' });
  g.fillStyle = '#26262c'; rr(g, W / 2 - bw / 2, by - bh / 2, bw, bh, bh / 2); g.fill(); g.fillStyle = OR; rr(g, W / 2 - bw / 2, by - bh / 2, Math.max(bh, bw * pe), bh, bh / 2); g.fill();
  text(g, `${Math.floor(pe * 100)}%  ·  frame ${fr} / 1350`, W / 2, by + M * .08, M * .035, '#a8a194', { fam: 'Space Mono' });
  const sec = Math.floor(lt * 22) % 60; text(g, `09:58:${String(sec).padStart(2, '0')}`, W / 2, by + M * .2, M * .07, PAPER, { fam: 'Space Mono' });
}
const PARTS = Array.from({ length: 84 }, (_, i) => ({ vx: (hash(i) - .5) * 2 * 190, vy: -(250 + 150 * hash(i + 1)), sz: 5 + 6 * hash(i + 2), col: [BLUE, OR, YEL, MINT][i % 4], sh: i % 3, sp: (hash(i + 3) - .5) * 9, d: hash(i + 4) * .4 }));
function delivered(g, lt) {                               // lt local 0 at 38.4
  g.fillStyle = INK; g.fillRect(0, 0, W, H);
  const land = .12, k = eIn3(seg(lt, 0, land)), sq = lt > land ? .22 * Math.exp(-14 * (lt - land)) : 0, sw = Math.min(W * .86, M * 1.45), sh = M * .26, y = lerp(-H * .5, H * .44, k);
  // burst (#003): ring r 44→90 (scaled) width 16→0 over 0.6 s quint-out, 10 lines, 10 dots
  const bq = lt - land; if (bq > 0) { const sc = M / 300; g.strokeStyle = YEL; g.lineWidth = Math.max(0, 16 * sc * (1 - eOut5(clamp(bq / .6)))); g.beginPath(); g.arc(W / 2, H * .44, (44 + 46 * eOut5(clamp(bq / .6))) * sc * 1.6, 0, 6.2832); g.stroke();
    for (let i = 0; i < 10; i++) { const a = i / 10 * 6.2832, ro = (64 + 66 * eOut5(clamp(bq / .6))) * sc * 1.8, ln = 36 * sc * (1 - seg(bq, .22, .7)); g.strokeStyle = i % 2 ? MINT : YEL; g.lineWidth = 9 * sc; g.beginPath(); g.moveTo(W / 2 + Math.cos(a) * (ro - ln), H * .44 + Math.sin(a) * (ro - ln) * .82); g.lineTo(W / 2 + Math.cos(a) * ro, H * .44 + Math.sin(a) * ro * .82); g.stroke(); }
    g.globalAlpha = 1 - seg(bq, .3, .72); for (let i = 0; i < 10; i++) { const a = (i + .5) / 10 * 6.2832, rd = (58 + 92 * eOut5(clamp(bq / .6))) * sc * 2; g.fillStyle = i % 2 ? BLUE : OR; g.beginPath(); g.arc(W / 2 + Math.cos(a) * rd * 1.45, H * .44 + Math.sin(a) * rd * .78, (8 - 3.2 * clamp(bq / .6)) * sc, 0, 6.2832); g.fill(); } g.globalAlpha = 1; }
  g.save(); g.translate(W / 2, y); g.scale(1 + sq * .6, (lt < land ? 1.12 : 1) * (1 - sq)); g.fillStyle = MINT; rr(g, -sw / 2, -sh / 2, sw, sh, M * .03); g.fill(); text(g, 'DELIVERED', 0, 0, fit(g, 'DELIVERED', M * .14, sw * .88), INK); g.restore();
  text(g, '09:59', W / 2, H * .44 + sh * .95, M * .07, PAPER, { fam: 'Space Mono' });
  // confetti (#015): gravity 470 px/s², lifetime ≤1.5 s, scale 1.15→0.7 (scaled to stage)
  const sc = M / 208; PARTS.forEach(p => { const q = lt - land - p.d; if (q < 0 || q > 1.5) return; const x = W / 2 + p.vx * q * sc * 1.6, y2 = H * 1.02 + (p.vy * q * 1.55 + .5 * 470 * q * q) * sc * 1.3, a = q < .06 ? q / .06 : q > 1.05 ? 1 - (q - 1.05) / .45 : 1;
    g.save(); g.globalAlpha = clamp(a); g.translate(x, y2); g.rotate(p.sp * q); g.scale(lerp(1.15, .7, q / 1.5), lerp(1.15, .7, q / 1.5)); g.fillStyle = p.col; const s = p.sz * sc * .5;
    if (p.sh === 0) { g.beginPath(); g.arc(0, 0, s, 0, 6.2832); g.fill(); } else if (p.sh === 1) g.fillRect(-s, -s, s * 2, s * 2); else { g.beginPath(); g.moveTo(0, -s); g.lineTo(s, s); g.lineTo(-s, s); g.closePath(); g.fill(); } g.restore(); });
  if (lt > .6) bubbleReply(g, lt - .6);
}
function bubbleReply(g, lt) { const px = M * (PORT ? .05 : .042), w = Math.min(W * .62, M * .95), y = H * (PORT ? .78 : .82), bh = px * 2.4, bx = W / 2 - w / 2, s = spring(lt, 6.5, 15);
  g.save(); g.translate(W / 2, y); g.scale(s, s); g.translate(-W / 2, -y); g.fillStyle = '#fff'; rr(g, bx, y - bh / 2, w, bh, bh * .3); g.fill(); text(g, 'perfect. ship it.', W / 2, y + 2, fit(g, 'perfect. ship it.', px, w * .85, 'Space Mono'), INK, { fam: 'Space Mono' }); g.restore(); }

// END — the Dot drops (#011 squash) into the full stop of “Chandan.”, #022 light sweep, role line
function endcard(g, lt) {
  g.fillStyle = INK; g.fillRect(0, 0, W, H);
  const px = fit(g, 'Chandan.', M * (PORT ? .26 : .3), W * .82, 'Instrument Serif'); g.font = F(px, 'Instrument Serif');
  const nameW = g.measureText('Chandan').width, dotR = px * .085, total = nameW + dotR * 3, x0 = W / 2 - total / 2, by = H * .5;
  const rise = eOut5(seg(lt, .35, 1.0)); g.save(); g.beginPath(); g.rect(0, by - px * 1.1, W, px * 1.32); g.clip(); text(g, 'Chandan', x0, by + (1 - rise) * px, px, PAPER, { fam: 'Instrument Serif', align: 'left', base: 'alphabetic' }); g.restore();
  // dot: falls from above, squashes on the baseline, settles
  const tx = x0 + nameW + dotR * 1.6, ty = by - dotR, fall = eIn3(seg(lt, 0, .35)), y = lerp(-H * .2, ty, fall), q = lt - .35, sq = q > 0 ? .35 * Math.exp(-10 * q) * Math.cos(18 * q) : 0;
  g.save(); g.translate(tx, y + dotR * sq); g.scale(1 + sq, 1 - sq); g.fillStyle = OR; g.beginPath(); g.arc(0, 0, dotR, 0, 6.2832); g.fill(); g.restore();
  // light sweep (#022): 116-wide band (opacity .72) + thin 12 band 78 away, rotated .42 rad, crossing at 0.45–1.5 (shifted to 1.4–2.45), clipped to the glyphs
  const sw = eIO2(seg(lt, 1.4, 2.45)); if (sw > 0 && sw < 1) { g.save(); g.font = F(px, 'Instrument Serif'); g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    o.clearRect(0, 0, W, H); o.save(); o.font = F(px, 'Instrument Serif'); o.textAlign = 'left'; o.textBaseline = 'alphabetic'; o.fillStyle = '#fff'; o.fillText('Chandan', x0, by); o.globalCompositeOperation = 'source-in';
    const bx = lerp(x0 - px, x0 + nameW + px, sw); o.translate(bx, by - px * .35); o.rotate(.42); const gr = o.createLinearGradient(-px * .2, 0, px * .2, 0); gr.addColorStop(0, 'rgba(255,240,228,0)'); gr.addColorStop(.5, 'rgba(255,240,228,.72)'); gr.addColorStop(1, 'rgba(255,240,228,0)'); o.fillStyle = gr; o.fillRect(-px * .2, -px * 2, px * .4, px * 4); o.fillStyle = 'rgba(255,240,228,.5)'; o.fillRect(px * .3, -px * 2, px * .04, px * 4); o.restore(); g.drawImage(off, 0, 0); g.restore(); }
  const ra = seg(lt, 1.0, 1.5); g.globalAlpha = ra; text(g, 'M O T I O N   &   V I D E O', W / 2, by + px * .42 + (1 - ra) * M * .03, M * (PORT ? .036 : .03), OR, { fam: 'Space Mono' }); g.globalAlpha = 1;
  g.globalAlpha = seg(lt, 4.2, 5.0); g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.globalAlpha = 1;
}

// ======================= EDIT =======================
// shot list: [t0, t1, fn(g, local)] — videos cover 19.2–32.4 (blitz + sing); canvas draws behind them as black.
const SHOTS = [
  [0, .8, (g, l) => hookPhone(g, l)], [.8, 1.6, (g, l) => hookType(g, l)], [1.6, 2.4, (g, l) => hookDeadline(g, l)], [2.4, 3.2, (g, l) => hookClock(g, l)],
  [3.2, 6.0, (g, l) => storyboard(g, l)],
  [6.0, 6.4, null],                                                    // whip pan (#043) handled below
  [6.4, 9.2, (g, l) => titles(g, l)], [9.2, 9.6, (g, l) => titlesZoom(g, l, (gg) => data(gg, 0))],
  [9.6, 12.8, (g, l) => data(g, l)], [12.8, 16.0, (g, l) => ui(g, l)], [16.0, 19.2, (g, l) => breakdown(g, l)],
  [19.2, 32.4, g => { g.fillStyle = '#000'; g.fillRect(0, 0, W, H); }],
  [32.4, 35.2, (g, l) => transRun(g, l)], [35.2, 38.4, (g, l) => render(g, l)], [38.4, 40.0, (g, l) => delivered(g, l)], [40.0, 45.0, (g, l) => endcard(g, l)],
];
const shotAt = t => SHOTS.find(([a, b]) => t >= a && t < b) || SHOTS[SHOTS.length - 1];
function drawRaw(g, t) { const s = shotAt(t); if (s[2]) s[2](g, t - s[0]); }
// #043 whip pan: outgoing yaw 0→+.45 (first .2 s), incoming −.45→0 (last .2 s), quadratic ease-in-out, 9 renders over ±1.6 frames averaged
function whip(g, t) {
  const lt = t - 6.0, n = 9; a2.clearRect(0, 0, W, H);
  for (let i = 0; i < n; i++) { const st = lt + (i / (n - 1) - .5) * (3.2 / 30); let x, scene;
    if (st < .2) { x = -eIO2(clamp(st / .2)) * .45; scene = l => storyboard(o, 3.0); } else { x = (1 - eIO2(clamp((st - .2) / .2))) * .45; scene = l => titles(o, 0); }
    o.setTransform(1, 0, 0, 1, 0, 0); o.clearRect(0, 0, W, H); o.save(); o.translate(x * W * 1.3 * (st < .2 ? 1 : -1) * -1, 0); scene(); o.restore();
    a2.globalAlpha = 1 / (i + 1); a2.drawImage(off, 0, 0); }
  a2.globalAlpha = 1; g.drawImage(acc, 0, 0);
}
// CapCut layer: beat punch-ins on cuts, flash frames on drops, impact shakes
const DROPS = [3.2, 19.2, 38.4], FLASH = [3.2, 6.4, 9.6, 12.8, 18.4, 19.2, 28.8, 32.4, 35.2, 38.4, 40.0];
const SHAKES = [[1.76, 1.1, 1], [6.92, .5, .7], [18.4, .6, 1.2], [38.52, 1.1, 1]];
function frame(t) {
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  let z = 1, sx = 0, sy = 0, rot = 0;
  const cutT = SHOTS.map(s => s[0]).concat([.4, 1.2, 4.0, 4.4, 4.8, 5.2, 6.8, 7.2, 7.6, 10.4, 11.2, 13.6, 14.4, 15.2]);
  for (const ct of cutT) { const q = t - ct; if (q >= 0 && q < .2 && !(ct >= 19.2 && ct < 32.4)) z = Math.max(z, 1 + .06 * (1 - q / .2) ** 2); }
  for (const [s0, d, amp] of SHAKES) { const q = t - s0; if (q >= 0 && q < d) { const e = Math.exp(-5 * q); sx += amp * 15 * M / 300 * e * Math.sin(2 * Math.PI * 5 * q); sy += amp * 11 * M / 300 * e * Math.cos(2 * Math.PI * 6.5 * q); rot += amp * .02 * e * Math.sin(2 * Math.PI * 5 * q + .6); } }
  c.save(); c.translate(W / 2 + sx, H / 2 + sy); c.rotate(rot); c.scale(z, z); c.translate(-W / 2, -H / 2);
  if (t >= 6.0 && t < 6.4) whip(c, t); else drawRaw(c, t);
  c.restore();
  for (const f of FLASH) { const q = t - f; if (q >= 0 && q < 2 / 30) { c.fillStyle = DROPS.includes(f) ? '#fff' : 'rgba(255,255,255,.55)'; c.fillRect(0, 0, W, H); } }
  drawHud(t);
}

// ======================= TIMELINE =======================
const tl = gsap.timeline({ paused: true }); const d = { t: 0 };
Promise.all(['Archivo Black', 'Space Mono', 'Instrument Serif'].map(f => document.fonts.load(`80px "${f}"`))).then(() => {
  tl.to(d, { t: 45, duration: 45, ease: 'none', onUpdate: () => frame(d.t) }, 0);
  // blitz video: punch on every style cut (0.8 s), slight push through the explainer
  for (let i = 0; i < 9; i++) tl.fromTo('#blitz-wrap', { scale: 1.08 }, { scale: 1, duration: .3, ease: 'power3.out', immediateRender: false }, 19.2 + i * .8);
  tl.fromTo('#blitz-wrap', { scale: 1 }, { scale: 1.06, duration: 2.4, ease: 'none', immediateRender: false }, 26.4);
  tl.fromTo('#sing-wrap', { scale: 1.12 }, { scale: 1, duration: .5, ease: 'expo.out', immediateRender: false }, 28.8);
  frame(0);
  window.__timelines['main'] = tl;
});
})();
