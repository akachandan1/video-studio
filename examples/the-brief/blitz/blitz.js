// Scene written for the huashu-art-motion engine (uses its PAINT/TOON/CAM APIs) · engine: MIT License (c) 2026 alchaincyf (花叔 · 花生) · https://github.com/alchaincyf/huashu-art-motion
// 'The Brief' art blitz. One product scene — DOT, an orange sphere speaker on a pedestal — drawn once as flat geometry,
// then repainted per style with huashu's renderers. Layout is relative to the stage (works at 1920×1080 and 1080×1920).
(() => {
let W = 1920, H = 1080; U.onStage((w, h) => { W = w; H = h; });
const { clamp, lerp, rng } = U, P = PAINT, flat = TOON.flat, glow = TOON.glow, seg = MO.seg;
const ORANGE = '#FF5A1F';
const G = () => { const m = Math.min(W, H); return { cx: W / 2, cy: H * 0.46, r: m * 0.2, floor: H * 0.46 + m * 0.2 + m * 0.11, m }; };

// flat base: wall, floor, pedestal, sphere with grille dots + light ring. pal = palette per style; bob = product breathing
function scene(g, pal, lt, { grille = true, line = null } = {}) {
  const { cx, cy, r, floor, m } = G(), bob = Math.sin(lt * 7.85) * m * 0.006;
  g.fillStyle = pal.wall; g.fillRect(0, 0, W, H);
  g.fillStyle = pal.floor; g.fillRect(0, floor, W, H - floor);
  // spotlight pool
  g.fillStyle = pal.pool; g.beginPath(); g.ellipse(cx, floor + m * 0.02, r * 1.9, r * 0.32, 0, 0, 6.28); g.fill();
  // pedestal
  const pw = r * 1.5, ph = m * 0.11; g.fillStyle = pal.ped; g.fillRect(cx - pw / 2, floor - ph, pw, ph); g.fillStyle = pal.pedTop; g.fillRect(cx - pw / 2 - m * 0.01, floor - ph - m * 0.012, pw + m * 0.02, m * 0.016);
  // sphere
  const y = cy + bob; g.fillStyle = pal.dot; g.beginPath(); g.arc(cx, y, r, 0, 6.28); g.fill();
  g.fillStyle = pal.dotSh; g.beginPath(); g.arc(cx + r * 0.18, y + r * 0.18, r * 0.92, 0, 6.28); g.globalAlpha = pal.shA ?? 0.35; g.fill(); g.globalAlpha = 1;
  g.fillStyle = pal.dot; g.beginPath(); g.arc(cx - r * 0.06, y - r * 0.06, r * 0.86, 0, 6.28); g.fill();
  if (grille) { g.fillStyle = pal.grille; for (let row = -5; row <= 5; row++) for (let col = -5; col <= 5; col++) { const x = cx + col * r * 0.16 + (row % 2) * r * 0.08, yy = y + r * 0.1 + row * r * 0.14; if (Math.hypot(x - cx, (yy - y) * 1.05) < r * 0.78 && yy > y - r * 0.1) { g.beginPath(); g.arc(x, yy, r * 0.03, 0, 6.28); g.fill(); } } }
  // light ring on top
  g.strokeStyle = pal.ring; g.lineWidth = m * 0.01; g.beginPath(); g.ellipse(cx, y - r * 0.55, r * 0.42, r * 0.12, 0, 0, 6.28); g.stroke();
  g.fillStyle = pal.hi; g.beginPath(); g.ellipse(cx - r * 0.42, y - r * 0.45, r * 0.16, r * 0.1, -0.6, 0, 6.28); g.fill();
  if (line) { g.strokeStyle = line.col; g.lineWidth = line.w; g.beginPath(); g.arc(cx, y, r, 0, 6.28); g.stroke(); g.strokeRect(cx - pw / 2, floor - ph, pw, ph); g.beginPath(); g.moveTo(0, floor); g.lineTo(W, floor); g.stroke(); }
}
const base = (key, pal, lt, opt) => { const b = P.scratch(key), g = b.getContext('2d'); g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H); scene(g, pal, lt, opt); return b; };
const PAL = (o) => Object.assign({ wall: '#2A2F45', floor: '#1C1F2E', pool: 'rgba(255,220,180,.18)', ped: '#E9E4DA', pedTop: '#FFFFFF', dot: ORANGE, dotSh: '#B8380C', grille: 'rgba(60,20,8,.55)', ring: '#FFE2C8', hi: 'rgba(255,255,255,.55)' }, o);

// 1 Van Gogh — swirling strokes around the sphere
SCENES['b_vg'] = { draw(c, lt, t) { const { cx, cy } = G(); const b = base('vg', PAL({ wall: '#1D2C7C', floor: '#B5553B', ped: '#E3AD38', pedTop: '#F4D06F', dot: '#F08A24', dotSh: '#B2501A', pool: 'rgba(246,216,74,.35)' }), lt);
  c.drawImage(b, 0, 0); const ang = (x, y) => y < G().floor ? Math.atan2(y - cy, x - cx) + Math.PI / 2 + 0.3 * Math.sin(Math.hypot(x - cx, y - cy) / 70 - t * 2) : 0.1 * Math.sin(x / 120);
  P.strokes(c, b, { cell: 10, len: 24, width: 6.5, angle: ang, seed: 2, t, boil: 8, outline: 0.75, outlineMix: 0.45 }); } };
// 2 Lichtenstein — primaries, black line, Ben-Day wall, SPEECH word
SCENES['b_pop'] = { draw(c, lt) { const b = base('pop', PAL({ wall: '#F7F2E4', floor: '#2B5DD9', ped: '#F7E23A', pedTop: '#111', dot: '#E8322E', dotSh: '#E8322E', shA: 0, grille: '#111', ring: '#111', hi: '#fff', pool: 'rgba(0,0,0,0)' }), lt, { line: { col: '#111', w: G().m * 0.012 } });
  c.drawImage(b, 0, 0); const d = b.getContext('2d').getImageData(0, 0, W, H).data, st = Math.round(G().m * 0.018); c.fillStyle = '#4FA3E8';
  for (let y = st; y < H; y += st) for (let x = (y / st % 2) * st / 2 + st / 2; x < W; x += st) { const i = ((y | 0) * W + (x | 0)) * 4; if (d[i] > 240 && d[i + 2] > 210 && d[i + 2] < 235) { c.beginPath(); c.arc(x, y, st * 0.28, 0, 6.28); c.fill(); } }
  const { cx, cy, r, m } = G(); c.save(); c.translate(cx + r * 1.15, cy - r * 1.1); c.rotate(-0.12); c.fillStyle = '#F7E23A'; c.strokeStyle = '#111'; c.lineWidth = m * 0.01;
  c.beginPath(); for (let k = 0; k < 16; k++) { const a = k / 16 * 6.28, rr = (k % 2 ? 0.55 : 1) * m * 0.13; c.lineTo(Math.cos(a) * rr * 1.4, Math.sin(a) * rr); } c.closePath(); c.fill(); c.stroke();
  c.fillStyle = '#111'; c.font = `${Math.round(m * 0.075)}px "Bangers-400"`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('BOOM!', 0, 4); c.restore(); } };
// 3 Chinese ink — paper, wash pedestal, vermilion sphere as a seal, a brushed stroke
SCENES['b_ink'] = { draw(c, lt) { const { cx, cy, r, floor, m } = G(); c.drawImage(P.texture('paper', '#EFE6D2', { amt: 14, grain: 10 }), 0, 0);
  P.inkWash(c, 'ped', 1, g => { g.fillStyle = 'rgba(20,18,15,.7)'; g.fillRect(cx - r * 0.75, floor - m * 0.11, r * 1.5, m * 0.11); }, { blur: 4, halo: 14, haloA: 0.25 });
  P.brush(c, [[cx - W * 0.4, floor + 4], [cx, floor - 6], [cx + W * 0.4, floor + 2]], { w: m * 0.012, tone: 0.75, dry: 0.5, seed: 4 });
  c.fillStyle = 'rgba(200,40,30,.92)'; c.beginPath(); c.arc(cx, cy + Math.sin(lt * 7.85) * m * 0.006, r, 0, 6.28); c.fill();
  c.fillStyle = 'rgba(239,230,210,.9)'; c.font = `${Math.round(r * 0.9)}px "NotoSerifJP-600"`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('点', cx, cy + r * 0.05);
  P.brush(c, [[cx - r * 2.2, cy - r * 1.3], [cx - r * 1.2, cy - r * 1.6], [cx, cy - r * 1.35]], { w: m * 0.02, tone: 0.8, dry: 0.6, seed: 9, reveal: MO.cubicOut(seg(lt, 0, 0.5)) }); } };
// 4 8-bit — pixelated at 12 fps with a HUD
SCENES['b_px'] = { draw(c, lt) { const ts = Math.floor(lt * 12) / 12, b = base('px', PAL({ wall: '#1B1D3A', floor: '#45B36B', ped: '#E8D8B0', pedTop: '#FFFFFF' }), ts); P.pixelate(c, b, { size: Math.round(G().m * 0.014) });
  c.fillStyle = '#fff'; c.font = `${Math.round(G().m * 0.028)}px "PressStart2P-400"`; c.textAlign = 'left'; c.fillText('1UP  DOT', W * 0.06, H * 0.1); } };
// 5 Kusama — dots everywhere, the product is the biggest dot
SCENES['b_kus'] = { draw(c, lt) { const { cx, cy, r, m } = G(); c.fillStyle = '#E8322E'; c.fillRect(0, 0, W, H); const st = m * 0.05, pulse = 1 + 0.1 * Math.sin(lt * 15.7);
  c.fillStyle = '#fff'; for (let row = 0, y = 0; y < H + st; y += st * 0.866, row++) for (let x = (row % 2) * st / 2; x < W + st; x += st) { const d = Math.hypot(x - cx, y - cy); if (d < r * 1.25) continue; c.beginPath(); c.arc(x, y, st * 0.26 * pulse * (0.7 + 0.5 * Math.sin(d * 0.01 - lt * 6)), 0, 6.28); c.fill(); }
  c.fillStyle = '#FFD21F'; c.beginPath(); c.arc(cx, cy, r, 0, 6.28); c.fill(); c.fillStyle = '#111'; for (let k = 0; k < 14; k++) { const a = k * 2.4, rr = r * Math.sqrt((k + 0.5) / 14) * 0.85; c.beginPath(); c.arc(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr, r * 0.1, 0, 6.28); c.fill(); } } };
// 6 Cubism — faceted planes, shifted per facet
SCENES['b_cub'] = { draw(c, lt, t) { const b = base('cub', PAL({ wall: '#8A7A5E', floor: '#5C5040', ped: '#D8CDB4', dot: '#C9672E', dotSh: '#6E3418' }), lt); P.facets(c, b, { nx: 26, ny: 16, seed: 6, t, shiftAmt: G().m * 0.01 }); } };
// 7 Roman mosaic — tesserae + grout
SCENES['b_mos'] = { draw(c, lt) { const b = base('mos', PAL({ wall: '#E9DFC8', floor: '#7A4A2E', ped: '#2F4F6F', pedTop: '#C9B37E', dot: '#D2552A', dotSh: '#8A2E14', grille: 'rgba(40,20,10,.6)' }), lt); P.mosaic(c, b, { tile: Math.round(G().m * 0.018), grout: '#3B352E', seed: 3 }); } };
// 8 Monet — impressionist dabs, shimmering
SCENES['b_mon'] = { draw(c, lt, t) { const b = base('mon', PAL({ wall: '#9FC3D9', floor: '#7FAF7A', ped: '#F2E6D8', pedTop: '#FFF8EC', dot: '#F07A3A', dotSh: '#C25A2A', pool: 'rgba(255,240,200,.4)' }), lt); c.drawImage(b, 0, 0); P.dabs(c, b, { cell: Math.round(G().m * 0.011), size: G().m * 0.011, seed: 2, t, boil: 8, angle: -0.6, shift: 22 }); } };
// 9 Matisse — cut paper, ragged scissor edges, seaweed shapes
SCENES['b_mat'] = { draw(c, lt) { const { cx, cy, r, floor, m } = G(); c.fillStyle = '#2E5BB8'; c.fillRect(0, 0, W, H); c.fillStyle = '#F2E8D5'; c.fillRect(0, floor, W, H - floor);
  const cut = (pts, col, seed) => { const q = P.cut(pts, seed, m * 0.02, m * 0.004); c.save(); c.shadowColor = 'rgba(0,0,0,.18)'; c.shadowOffsetY = m * 0.006; c.fillStyle = col; c.fill(q); c.restore(); };
  for (let s = 0; s < 4; s++) { const x0 = W * (0.1 + s * 0.26), pts = []; for (let k = 0; k <= 12; k++) { const yy = H * 0.15 + k * H * 0.05; pts.push([x0 + Math.sin(k * 1.3 + s + lt * 4) * m * 0.03 + (k % 2 ? m * 0.04 : -m * 0.04), yy]); } for (let k = 12; k >= 0; k--) pts.push([pts[k][0] + m * 0.03, pts[k][1]]); cut(pts, ['#F2C14E', '#F2E8D5', '#E8322E', '#F2C14E'][s], s + 3); }
  cut(Array.from({ length: 48 }, (_, k) => [cx + Math.cos(k / 48 * 6.28) * r, cy + Math.sin(k / 48 * 6.28) * r + Math.sin(lt * 7.85) * m * 0.006]), ORANGE, 11);
  cut([[cx - r * 0.75, floor], [cx - r * 0.75, floor - m * 0.11], [cx + r * 0.75, floor - m * 0.11], [cx + r * 0.75, floor]], '#111', 12); } };

// 10 Inside — Kurzgesagt flat exploded view: shell splits, parts fan out, labels pop
SCENES['b_inside'] = { draw(c, lt) { const { cx, cy, r, m } = G(); c.fillStyle = '#121417'; c.fillRect(0, 0, W, H);
  const e = MO.k75(seg(lt, 0.15, 0.85)), sp = r * 1.05 * e, port = H > W;
  const parts = [['Grille shell', '#FF5A1F', '#C9410F', 1.0], ['Mic array', '#5CC8E0', '#2E8FA8', 0.55], ['40 mm driver', '#E9E4DA', '#A9A397', 0.8], ['Chip', '#2FBF71', '#1E8A50', 0.42], ['12 h battery', '#F2B33D', '#B9821E', 0.62]];
  parts.forEach(([name, col, sh, sz], i) => { const k = i - 2, ox = port ? 0 : k * sp * 1.15, oy = port ? k * sp * 0.95 : 0, x = cx + ox, y = cy + oy, rr = r * sz * (i === 0 ? 1 : 0.9) * (port ? 0.8 : 1);
    glow(c, x, y, rr * 1.6, col, 0.18 * e);
    if (i === 0) { const p = new Path2D(); p.arc(x, y, rr, Math.PI * 0.5, Math.PI * 1.5); p.closePath(); flat(c, p, col, sh, '#FF9C6E', [rr * 0.1, rr * 0.1], [rr * 0.03, rr * 0.03]); }
    else { const p = new Path2D(); if (i === 3) p.roundRect(x - rr * 0.8, y - rr * 0.8, rr * 1.6, rr * 1.6, rr * 0.2); else p.arc(x, y, rr, 0, 6.28); flat(c, p, col, sh, '#ffffff', [rr * 0.12, rr * 0.12], [rr * 0.04, rr * 0.04]); }
    const la = clamp((lt - 0.7 - i * 0.12) / 0.25); if (la > 0) { c.save(); c.globalAlpha = la; c.font = `${Math.round(m * 0.03)}px "Poppins-700"`; const tw = c.measureText(name).width + m * 0.04, hh = m * 0.05;
      const lx = port ? x + rr + m * 0.04 + tw / 2 : x, ly = port ? y : y + (k % 2 ? -1 : 1) * (rr + m * 0.08);
      c.fillStyle = '#F2EFE8'; c.beginPath(); c.roundRect(lx - tw / 2, ly - hh / 2, tw, hh, hh / 2); c.fill(); c.fillStyle = '#16181B'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(name, lx, ly + 1); c.restore(); } });
  const ta = clamp((lt - 0.1) / 0.3); c.save(); c.globalAlpha = ta; c.fillStyle = '#F2EFE8'; c.font = `${Math.round(m * 0.05)}px "Poppins-800"`; c.textAlign = 'center'; c.fillText("What's inside Dot?", cx, port ? H * 0.12 : H * 0.14); c.restore(); } };
})();
