// "What's inside the Great Pyramid?" — Kurzgesagt-style flat science, one continuous world + one camera.
// Cross-section is to scale (1200 px base = 230.3 m → 5.21 px/m): passage angles ~26.5°, King's Chamber floor 43 m,
// Queen's Chamber 21 m, Subterranean Chamber ~30 m below ground, relieving chambers ~17 m stack above the King's Chamber.
// Beats: 0 establish · 3.0 x-ray cutaway · 4.2 passages draw + labels · 7.0 King's Chamber lights · 7.4 dive ·
//        10.4 glide up to relieving chambers · 12.0 dive into top chamber → graffiti · 13.6 long pull back · 14.4 end line.
(() => {
const W = 1920, H = 1080;
const { clamp, lerp, rng } = U;
const seg = MO.seg, flat = TOON.flat, glow = TOON.glow, layer = CAM.layer;
const K75 = MO.k75, sio = MO.sineInOut, cio = MO.cubicInOut, cout = MO.cubicOut, bout = q => MO.backOut(q, 1.2);

// ---------- palette: dark ink sky (no blue-purple), sand gold, red granite, teal accent ----------
const C = {
  sky: '#121417', sky2: '#17191D', horizon: '#2A221B', star: '#F2EFE8', moon: '#F5E6C4', moonSh: '#D9C49A',
  duneFar: '#3B2F22', duneFarHi: '#4A3B2A', dune: '#5E4A31', duneHi: '#735A3B', duneSh: '#4C3B27',
  lit: '#E2B45C', litHi: '#F2CB7A', shade: '#B4843E', shadeSh: '#9C7134',
  core: '#7A5A33', coreLine: 'rgba(40,28,14,.35)', bedrock: '#4A3A27', bedLine: 'rgba(20,14,8,.35)',
  void: '#1A1511', voidEdge: '#2C241C', granite: '#B5503F', graniteSh: '#8E3A2E', graniteHi: '#CF6A55',
  gold: '#F2B33D', teal: '#5FB3A1', ink: '#F2EFE8', pillInk: '#16181B', ochre: '#C2462F',
};

// ---------- world geometry (z = 1 frame) ----------
const G = 800, AX = 960, AY = 36, BL = 360, BR = 1560;
const faceL = y => BL + (G - y) / (G - AY) * (AX - BL), faceR = y => BR - (G - y) / (G - AY) * (BR - AX);
const ENT = [432, 711], JUNC = [590, 790], GG0 = [789, 691], GG1 = [1004, 576];
const DESC1 = [923, 956], SUB = { x: 950, y: 938, w: 74, h: 20 };
const QC = { x: 946, y: 659, w: 27, h: 32 }, KC = { x: 1012, y: 546, w: 55, h: 30 };
const RC = { x: 1012, top: 457, bot: 546, n: 5 };                       // relieving chambers
const RCc = i => { const h = (RC.bot - RC.top) / RC.n; return { y0: RC.bot - (i + 1) * h, y1: RC.bot - i * h, h }; };
const NSH = [[1012, 560], [703, 363]], SSH = [[1067, 560], [1237, 390]]; // King's Chamber shafts to the faces
const KCc = [KC.x + KC.w / 2, KC.y + KC.h / 2], TOPc = [1040, (RCc(4).y0 + RCc(4).y1) / 2];

// ---------- camera: pure function of t ----------
const CAM0 = { x: 960, y: 540, z: 1 };
const camAt = t => {
  let cam = { x: 960, y: 540, z: lerp(1, 1.03, sio(seg(t, 0, 7))) };              // establishing drift, then hold
  const e1 = K75(seg(t, 7.4, 9.3));                                                  // dive into the King's Chamber
  if (e1 > 0) cam = CAM.pushTo(cam, KCc[0], KCc[1], 15, e1);
  const e2 = sio(seg(t, 10.4, 11.5));                                                // glide up + ease back to see all 5 compartments
  if (e2 > 0) cam = { x: lerp(cam.x, 1040, e2), y: lerp(cam.y, 505, e2), z: CAM.zlerp(cam.z, 10, e2) };
  const e3 = K75(seg(t, 12.0, 13.0));                                                // dive into the top compartment
  if (e3 > 0) cam = CAM.pushTo(cam, TOPc[0], TOPc[1], 44, e3);
  const e4 = MO.longTail ? MO.longTail(seg(t, 13.6, 15.2)) : cout(seg(t, 13.6, 15.2));// long-tail pull back to the whole pyramid
  if (e4 > 0) cam = { x: lerp(cam.x, CAM0.x, e4), y: lerp(cam.y, CAM0.y, e4), z: CAM.zlerp(cam.z, 1.0, e4) };
  return cam;
};

const STARS = (() => { const r = rng(7), o = []; for (let i = 0; i < 180; i++) o.push({ x: r() * 2400 - 240, y: r() * 620 - 60, r: 0.7 + r() * r() * 2.8, ph: r() * 6.28, sp: 0.8 + r() * 2.2 }); return o; })();
const MOTES = (() => { const r = rng(9), o = []; for (let i = 0; i < 30; i++) o.push({ x: r() * W, y: 380 + r() * 520, ph: r() * 6.28, d: 0.7 + r() * 0.6, s: 1.5 + r() * 2.5 }); return o; })();
const DUST = (() => { const r = rng(5), o = []; for (let i = 0; i < 60; i++) o.push({ x: 1012 + r() * 55, y: RC.top + r() * (KC.y + KC.h - RC.top), ph: r() * 6.28, s: 0.05 + r() * 0.12 }); return o; })();

const poly = pts => { const p = new Path2D(); pts.forEach(([x, y], i) => i ? p.lineTo(x, y) : p.moveTo(x, y)); p.closePath(); return p; };
const rect = (x, y, w, h) => { const p = new Path2D(); p.rect(x, y, w, h); return p; };
const line = (g, a, b, w, col, k = 1) => { if (k <= 0) return; g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'butt'; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(lerp(a[0], b[0], k), lerp(a[1], b[1], k)); g.stroke(); };
const band = (g, a, b, th, col, k = 1) => { if (k <= 0) return; const ex = lerp(a[0], b[0], k), ey = lerp(a[1], b[1], k); g.fillStyle = col; g.fill(poly([[a[0], a[1]], [ex, ey], [ex, ey - th], [a[0], a[1] - th]])); };

// ---------- the world ----------
function drawWorld(g, t, cam) {
  const cut = seg(t, 3.0, 4.3);                        // x-ray wipe progress (apex → base)
  const wipeY = lerp(AY - 20, G + 4, cio(cut));

  // bedrock below ground (visible once cut away; also under the sand)
  g.fillStyle = C.bedrock; g.fillRect(-400, G, 2800, 700);
  g.strokeStyle = C.bedLine; g.lineWidth = 1.2; for (let y = G + 26; y < G + 700; y += 26) { g.beginPath(); g.moveTo(-400, y); g.lineTo(2400, y + Math.sin(y) * 6); g.stroke(); }
  // sand surface strip
  flat(g, rect(-400, G - 6, 2800, 40), C.dune, C.duneSh, C.duneHi, [0, -6], [0, 3]);

  // pyramid core (interior stone with courses)
  const tri = poly([[BL, G], [AX, AY], [BR, G]]);
  g.save(); g.clip(tri);
  g.fillStyle = C.core; g.fillRect(BL, AY, BR - BL, G - AY);
  g.strokeStyle = C.coreLine; g.lineWidth = 1; for (let y = G - 9; y > AY; y -= 9) { g.beginPath(); g.moveTo(BL, y); g.lineTo(BR, y); g.stroke(); }
  // staggered block joints (visible when zoomed)
  g.lineWidth = 0.6; for (let y = G - 9, row = 0; y > AY; y -= 9, row++) for (let x = BL + (row % 2) * 7; x < BR; x += 14) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 9); g.stroke(); }
  g.restore();

  // passages & chambers draw in after the cutaway
  const p = s => cout(seg(t, s, s + 0.55));
  const V = C.void;
  line(g, ENT, DESC1, 9, V, p(4.2));                                                  // descending passage
  if (p(4.75) > 0) { line(g, DESC1, [SUB.x, DESC1[1]], 9, V, p(4.75)); flat(g, rect(SUB.x, SUB.y, SUB.w * p(4.75), SUB.h), V, '#100c09', C.voidEdge, [0, 3], [0, 1.5]); }
  line(g, JUNC, GG0, 9, V, p(4.55));                                                  // ascending passage
  band(g, GG0, GG1, 45, V, p(4.95));                                                  // Grand Gallery (corbelled, 8.6 m tall)
  line(g, [GG0[0], GG0[1] - 4], [QC.x, GG0[1] - 4], 8, V, p(5.1));                    // Queen's corridor
  if (p(5.3) > 0) { g.globalAlpha = p(5.3); flat(g, poly([[QC.x, QC.y + QC.h], [QC.x, QC.y + 8], [QC.x + QC.w / 2, QC.y], [QC.x + QC.w, QC.y + 8], [QC.x + QC.w, QC.y + QC.h]]), V, '#100c09', C.voidEdge, [0, 2], [0, 1]); g.globalAlpha = 1; }
  // King's Chamber + relieving stack (granite)
  const kc = p(5.5);
  if (kc > 0) {
    g.globalAlpha = kc;
    line(g, GG1, [KC.x, GG1[1] - 6], 9, V);                                           // antechamber link
    flat(g, rect(KC.x - 3, RC.top - 18, KC.w + 6, KC.y + KC.h - RC.top + 21), C.graniteSh, '#6E2C23', C.granite, [0, 2], [0, 1]); // granite casing
    // gable roof above the stack (limestone)
    flat(g, poly([[KC.x - 10, RC.top], [KCc[0], RC.top - 22], [KC.x + KC.w + 10, RC.top]]), '#9A7442', '#7E5E36', '#B38A50', [0, 2], [0, 1]);
    for (let i = 0; i < RC.n; i++) { const r = RCc(i); flat(g, rect(KC.x + 2, r.y0 + 3.2, KC.w - 4, r.h - 3.2), '#2A1A15', '#1B110E', '#3A2620', [0, 1], [0, 0.5]); }
    // King's Chamber interior (dark) with granite joints
    // back wall: large red granite blocks (5 courses, staggered), lit from the gallery side
    flat(g, rect(KC.x, KC.y, KC.w, KC.h), '#7E3A2E', '#642C23', '#93463A', [1.2, 1.2], [0.5, 0.5]);
    g.strokeStyle = 'rgba(40,14,10,.55)'; g.lineWidth = 0.22;
    for (let r = 1; r < 5; r++) { const y = KC.y + r * KC.h / 5; g.beginPath(); g.moveTo(KC.x, y); g.lineTo(KC.x + KC.w, y); g.stroke(); }
    for (let r = 0; r < 5; r++) for (let x = KC.x + (r % 2 ? 4.5 : 9); x < KC.x + KC.w - 1; x += 9) { const y = KC.y + r * KC.h / 5; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + KC.h / 5); g.stroke(); }
    g.fillStyle = '#4E211A'; g.fillRect(KC.x, KC.y + KC.h - 1.2, KC.w, 1.2);       // floor line
    glow(g, KC.x + 6, KC.y + KC.h - 6, 18, '#FFB070', 0.10);                          // warm bounce near the entrance
    // sarcophagus (west end) — open, found empty
    flat(g, rect(KC.x + 5, KC.y + KC.h - 5.5, 11, 5.5), C.granite, C.graniteSh, C.graniteHi, [0.6, 0.6], [0.25, 0.25]);
    g.fillStyle = '#1B0F0C'; g.fillRect(KC.x + 6, KC.y + KC.h - 5, 9, 1.4);
    // shaft mouths
    g.fillStyle = '#0D0907'; g.fillRect(KC.x, KC.y + 13, 1.2, 1.2); g.fillRect(KC.x + KC.w - 1.2, KC.y + 13, 1.2, 1.2);
    g.globalAlpha = 1;
  }
  line(g, NSH[0], NSH[1], 2.4, V, p(5.8)); line(g, SSH[0], SSH[1], 2.4, V, p(5.9)); // "air" shafts

  // King's Chamber light-up before the dive (stop, then go)
  const lit = seg(t, 6.95, 7.35) * (1 - seg(t, 9.0, 9.6));
  if (lit > 0) { glow(g, KCc[0], KCc[1], 70, C.gold, 0.55 * lit); g.strokeStyle = PAINT.rgb(PAINT.hex(C.gold), lit); g.lineWidth = 2; g.strokeRect(KC.x - 1, KC.y - 1, KC.w + 2, KC.h + 2); }

  // graffiti in the top relieving chamber (red ochre work-gang marks)
  const gq = seg(t, 12.7, 13.5);
  if (gq > 0) {
    const r = RCc(4), cx = 1040, cy = (r.y0 + 3.2 + r.y1) / 2;
    g.save(); g.globalAlpha = gq; g.strokeStyle = C.ochre; g.fillStyle = C.ochre; g.lineWidth = 0.55; g.lineCap = 'round';
    const draw = (k, fn) => { if (gq > k) fn(); };
    // cartouche
    draw(0.0, () => { g.beginPath(); g.roundRect(cx - 10, cy - 4.5, 13, 9, 4.5); g.stroke(); g.beginPath(); g.moveTo(cx + 4, cy - 4.5); g.lineTo(cx + 4, cy + 4.5); g.stroke(); });
    draw(0.2, () => { g.beginPath(); g.arc(cx - 6.5, cy - 1.5, 1.4, 0, 6.29); g.fill(); });
    draw(0.35, () => { g.beginPath(); for (let i = 0; i < 4; i++) { g.lineTo(cx - 8 + i * 1.6, cy + 1.6 + (i % 2) * 1.2); } g.stroke(); });
    draw(0.5, () => { g.beginPath(); g.moveTo(cx - 1.5, cy + 2.6); g.lineTo(cx, cy - 2.6); g.lineTo(cx + 1.5, cy + 2.6); g.stroke(); });
    // gang marks to the right
    draw(0.65, () => { for (let i = 0; i < 3; i++) { g.beginPath(); g.moveTo(cx + 8 + i * 2.2, cy - 3.5); g.lineTo(cx + 8 + i * 2.2, cy + 3.5); g.stroke(); } });
    draw(0.8, () => { g.beginPath(); g.arc(cx + 17, cy, 2.2, 0, 6.29); g.stroke(); g.beginPath(); g.moveTo(cx + 15, cy + 3.8); g.lineTo(cx + 19, cy + 3.8); g.stroke(); });
    g.restore();
  }
  // dust motes inside the granite rooms (visible only when zoomed)
  if (cam.z > 3) for (const d of DUST) { g.globalAlpha = 0.25 + 0.25 * Math.sin(t * 1.4 + d.ph); g.fillStyle = '#FFE7B8'; g.beginPath(); g.arc(d.x + Math.sin(t * 0.5 + d.ph) * 1.5, d.y + Math.cos(t * 0.4 + d.ph), d.s, 0, 6.29); g.fill(); g.globalAlpha = 1; }

  // exterior faces (two-tone flat), wiped away top→down by the x-ray scan
  if (wipeY < G) {
    g.save(); g.beginPath(); g.rect(BL - 20, wipeY, BR - BL + 40, G - wipeY + 2); g.clip();
    const left = poly([[BL, G], [AX, AY], [AX, G]]), right = poly([[AX, G], [AX, AY], [BR, G]]);
    g.fillStyle = C.lit; g.fill(left); g.fillStyle = C.shade; g.fill(right);
    // highlight sliver on the lit edge + course banding
    g.save(); g.clip(left); g.fillStyle = C.litHi; g.fill(poly([[BL, G], [AX, AY], [AX - 12, AY + 18], [BL + 18, G]])); g.restore();
    g.strokeStyle = 'rgba(90,60,20,.18)'; g.lineWidth = 1.4; for (let y = G - 18; y > AY; y -= 18) { g.beginPath(); g.moveTo(faceL(y), y); g.lineTo(faceR(y), y); g.stroke(); }
    g.restore();
    if (cut > 0 && cut < 1) { g.save(); g.clip(tri); glow(g, AX, wipeY, 0, C.teal, 0); g.fillStyle = PAINT.rgb(PAINT.hex(C.teal), 0.9); g.fillRect(BL, wipeY - 1.5, BR - BL, 3); g.fillStyle = PAINT.rgb(PAINT.hex(C.teal), 0.18); g.fillRect(BL, wipeY - 26, BR - BL, 26); g.restore(); }
  } else {
    // after the cutaway: thin silhouette outline keeps the shape readable
    g.strokeStyle = 'rgba(242,203,122,.55)'; g.lineWidth = 2; g.stroke(tri);
  }
}

// ---------- labels (screen space, anchored to world points) ----------
function pill(c, text, x, y, a, { col = C.ink, ink = C.pillInk, size = 26, align = 'left' } = {}) {
  if (a <= 0) return;
  c.save(); c.globalAlpha = a; c.font = `${size}px "Poppins-600"`; const w = c.measureText(text).width + size * 1.1, h = size * 1.6;
  const s = 0.85 + 0.15 * bout(Math.min(1, a * 1.4)); const x0 = align === 'right' ? x - w : align === 'center' ? x - w / 2 : x;
  c.translate(x0 + w / 2, y); c.scale(s, s); c.fillStyle = col; c.beginPath(); c.roundRect(-w / 2, -h / 2, w, h, h / 2); c.fill();
  c.fillStyle = ink; c.textBaseline = 'middle'; c.textAlign = 'center'; c.fillText(text, 0, 1); c.restore();
}
function callout(c, cam, wpt, lx, ly, text, t0, t1, opts = {}) {
  const a = cout(seg(T, t0, t0 + 0.45)) * (1 - seg(T, t1, t1 + 0.3)); if (a <= 0) return;
  const [sx, sy] = CAM.toScreen(cam, wpt[0], wpt[1]);
  const k = cout(seg(T, t0, t0 + 0.3));
  c.save(); c.globalAlpha = a; c.strokeStyle = opts.col || C.ink; c.lineWidth = 2.2;
  c.beginPath(); c.moveTo(sx, sy); c.lineTo(lerp(sx, lx, k), lerp(sy, ly, k)); c.stroke();
  c.fillStyle = opts.col || C.ink; c.beginPath(); c.arc(sx, sy, 5, 0, 6.29); c.fill(); c.restore();
  pill(c, text, lx + (opts.align === 'right' ? -6 : 6), ly, seg(T, t0 + 0.2, t0 + 0.55) * (1 - seg(T, t1, t1 + 0.3)), opts);
}
let T = 0;

function shot(c, lt) {
  const t = lt; T = t; const cam = camAt(t);
  // sky (flat ink, faint warm band at the horizon) — parallax layers
  c.fillStyle = C.sky; c.fillRect(0, 0, W, H);
  layer(c, cam, 0.04, g => { g.fillStyle = C.sky2; g.fillRect(-2000, 300, 6000, 500); g.fillStyle = C.horizon; g.fillRect(-2000, 640, 6000, 400);
    for (const s of STARS) { g.globalAlpha = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * s.sp + s.ph)); g.fillStyle = C.star; g.beginPath(); g.arc(s.x, s.y, s.r, 0, 6.29); g.fill(); } g.globalAlpha = 1; });
  layer(c, cam, 0.1, g => { glow(g, 1560, 190, 230, '#F5E6C4', 0.16); flat(g, (() => { const p = new Path2D(); p.arc(1560, 190, 62, 0, 6.29); return p; })(), C.moon, C.moonSh, '#FFF6E2', [-12, 10], [-4, 4]); });
  layer(c, cam, 0.35, g => { flat(g, poly([[-600, 820], [-100, 700], [300, 760], [700, 690], [1250, 740], [1700, 680], [2200, 750], [2600, 820], [2600, 1400], [-600, 1400]]), C.duneFar, C.duneFar, C.duneFarHi, [0, -8], [0, 3]); });
  // two distant pyramids (Khafre, Menkaure) — small, behind
  layer(c, cam, 0.6, g => { flat(g, poly([[1540, 812], [1760, 610], [1980, 812]]), '#8C6A3A', '#735630', '#A27C45', [6, 0], [2, 0]); flat(g, poly([[1900, 815], [2010, 712], [2120, 815]]), '#7A5C33', '#634A29', '#8C6A3A', [4, 0], [2, 0]); });
  // main world
  CAM.with(c, cam, g => drawWorld(g, t, cam));
  // drifting sand motes (foreground parallax, only in the wide view)
  if (cam.z < 2) for (const m of MOTES) layer(c, cam, m.d, g => { const x = (m.x + t * 18 * m.d + Math.sin(t + m.ph) * 20) % W, y = m.y + Math.sin(t * 0.7 + m.ph) * 10; g.globalAlpha = 0.35 + 0.3 * Math.sin(t * 2 + m.ph); g.fillStyle = '#F2D9A6'; g.beginPath(); g.arc(x, y, m.s, 0, 6.29); g.fill(); g.globalAlpha = 1; });

  // ---------- type ----------
  const titleA = 1 - seg(t, 2.7, 3.1);
  if (titleA > 0) { c.save(); c.globalAlpha = titleA;
    TY.charsIn(c, "What's inside", 110, 150, t - 0.25, { font: '64px "Poppins-800"', color: C.ink, dur: 0.5, stagger: 0.035, dy: 26 });
    TY.charsIn(c, 'the Great Pyramid?', 110, 228, t - 0.55, { font: '64px "Poppins-800"', color: C.gold, dur: 0.5, stagger: 0.035, dy: 26 });
    TY.charsIn(c, 'Giza · built c. 2560 BC for Pharaoh Khufu', 112, 282, t - 1.2, { font: '26px "Poppins-600"', color: C.teal, dur: 0.4, stagger: 0.012, dy: 14 });
    c.restore(); }
  // block counter (top right) during the cutaway
  const ca = seg(t, 4.1, 4.4) * (1 - seg(t, 7.2, 7.5));
  if (ca > 0) { const n = 2.3 * cout(seg(t, 4.1, 5.6)); c.save(); c.globalAlpha = ca; c.textAlign = 'left'; c.fillStyle = C.ink;
    c.font = '72px "Poppins-800"'; c.fillText(`${n.toFixed(1)} million`, 110, 150); c.font = '28px "Poppins-600"'; c.fillStyle = C.teal; c.fillText('stone blocks · 146 m tall when finished', 112, 196); c.restore(); }
  // wide-view callouts
  callout(c, cam, [470, 730], 150, 610, 'Descending passage', 4.6, 7.2);
  callout(c, cam, [987, 948], 1290, 995, 'Subterranean Chamber · cut into bedrock', 5.0, 7.2);
  callout(c, cam, [QC.x + 13, QC.y + 16], 560, 520, "Queen's Chamber", 5.4, 7.2, { align: 'right' });
  callout(c, cam, [880, 620], 470, 430, 'Grand Gallery', 5.7, 7.2, { align: 'right' });
  callout(c, cam, [KC.x + KC.w, KCc[1]], 1330, 470, "King's Chamber", 6.0, 7.25, { col: C.gold });
  // inside the King's Chamber
  callout(c, cam, [KC.x + 10.5, KC.y + KC.h - 5], 360, 860, "Khufu's sarcophagus · found empty", 9.25, 10.4);
  callout(c, cam, [KC.x + KC.w - 6, KC.y + 4], 1500, 300, 'Walls & roof: solid red granite', 9.45, 10.4, { align: 'right' });
  // relieving chambers
  callout(c, cam, [KC.x + KC.w - 4, RCc(2).y0 + 8], 1460, 520, '5 relieving chambers', 11.4, 12.05);
  pill(c, 'Stacked to spread the weight above the King’s Chamber', 1460, 580, seg(t, 11.55, 11.9) * (1 - seg(t, 12.05, 12.35)), { col: 'rgba(22,24,27,.85)', ink: C.ink, size: 22 });
  // graffiti
  const ga = seg(t, 13.0, 13.35) * (1 - seg(t, 13.75, 14.0));
  pill(c, 'Builders’ graffiti: “Friends of Khufu”', W / 2, 860, ga, { col: C.gold, align: 'center', size: 34 });
  pill(c, 'a work gang signed the stones ~4,500 years ago', W / 2, 930, ga, { col: 'rgba(22,24,27,.85)', ink: C.ink, align: 'center', size: 24 });
  // end line
  const ea = seg(t, 14.6, 15.1);
  if (ea > 0) { c.save(); c.globalAlpha = ea; TY.charsIn(c, '4,500 years later, still standing.', W / 2, 150, t - 14.6, { font: '56px "Poppins-800"', color: C.ink, dur: 0.5, stagger: 0.025, dy: 22, align: 'center' }); c.restore(); }
}

SCENES['pyr'] = { draw: (c, lt) => shot(c, lt) };
})();
