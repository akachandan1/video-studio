// Adapted from huashu-art-motion (scripts/engine/eras_gallery.js) · MIT License (c) 2026 alchaincyf (花叔 · 花生) · https://github.com/alchaincyf/huashu-art-motion
// 八个时代样片：skill 里 35 种风格（15 原段＋迁移测试 A–D 的 20 段）各一段，按年代排，用作回归测试与风格目录。
//   打开：index.html?film=gallery    渲染：render.py --film gallery    验收：qa.py --project scripts/engine --film gallery
// 每段 5 个八分音符（128 BPM ≈ 1.17s），最后一段 6 个。相邻段用「进入段」的签名转场（原 16 段沿用原片转场，A–D 组用各自配方卡里的转场；
// 每组第一段原来在片头没有进入转场，样片补了 inkBloom / redWedge / comicPanels / chiaroscuro）。
// 角标：年份严格单调，所以全片一个年份计数器连续滚动；各段沿用自己风格的字体与版式，label 写风格名。转场中点硬切新旧角标（引擎默认）。
// name 字段只给总览图/文档用（「年份＋风格名」），引擎不读。
const R = 1866;
const box = (x0, y0, x1, y1, fill, stroke, lw = 4, inset = 0) => c => {
  c.save(); c.fillStyle = fill; c.fillRect(x0, y0, x1 - x0, y1 - y0);
  if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw; c.strokeRect(x0 + inset, y0 + inset, x1 - x0 - 2 * inset, y1 - y0 - 2 * inset); }
  c.restore();
};
window.ERAS = [
 { id: '01_cave', name: '洞穴壁画', eighths: 11,
   counter: { year: -40000, roll: 0, x: R, y: 114, size: 84, font: 'GochiHand-400', color: '#f3ead8', spacing: 14,
     suffix: { text: 'BC', size: 44, gap: 18, dy: 0 }, label: { text: 'Cave painting', font: '38px "Kalam-700"', color: '#efe4cf', y: 178 } } },
 { id: '02_egypt', name: '古埃及壁画', eighths: 11, transition: { type: 'tiles', dur: 0.42 },
   counter: { year: -1350, roll: 0.4, x: R, y: 129, size: 100, font: 'IMFellEnglish-400', color: '#6b2318', spacing: 6,
     suffix: { text: 'BC', size: 50, gap: 14 }, label: { text: 'Egyptian wall painting', font: '34px "EBGaramond-400"', color: '#4a3424', y: 186 } } },
 { id: '03_greek', name: '古希腊黑绘陶', eighths: 11, transition: { type: 'cube', dur: 0.32 },
   counter: { year: -530, roll: 0.4, x: 1855, y: 136, size: 98, font: 'Cinzel-700', color: '#e3a066',
     box: box(1544, 42, 1888, 208, '#1b1310', '#c8743c', 3, 4),
     suffix: { text: 'BC', size: 48, gap: 14 }, label: { text: 'ATTIC BLACK-FIGURE', font: '29px "Cinzel-700"', color: '#e8b27c', x: 1855, y: 184, spacing: 2 } } },
 { id: '20_dunhuang', name: '敦煌壁画', eighths: 11, transition: { type: 'apsara', dur: 0.5 },
   counter: { year: 720, roll: 0.4, x: 1852, y: 132, size: 92, font: 'LXGWWenKai-500', color: '#2a1a14', box: box(1500, 44, 1880, 204, '#e6d6b2', '#5a2414', 4, 6), suffix: { text: 'AD', size: 40, gap: 14, font: 'Cinzel-700' }, label: { text: 'Dunhuang · Tang', font: '34px "Marcellus-400"', color: '#8a2a1c', x: 1852, y: 184, spacing: 4 } } },
 { id: '05_gothic', name: '哥特手抄本', eighths: 11, transition: { type: 'pageTurn', dur: 0.32 },
   counter: { year: 1290, roll: 0.4, x: R, y: 134, size: 100, font: 'LibreBaskerville-700', color: '#b3222b',
     label: { text: 'Gothic illumination', font: '36px "IMFellEnglish-400"', color: '#2b211a', y: 184 } } },
 { id: '06_renaissance', name: '文艺复兴', eighths: 11, transition: { type: 'godRays', dur: 0.4, cx: 560, cy: 290 },
   counter: { year: 1503, roll: 0.4, x: R, y: 142, size: 104, font: 'CormorantGaramond-500', color: '#ece0bf', spacing: 22,
     label: { text: 'HIGH RENAISSANCE', font: '30px "Cinzel-700"', color: '#e7d9b4', y: 184, spacing: 2 } } },
 { id: '51_persian_miniature', eighths: 11, transition: { type: 'mosaic', dur: 0.4 },
   counter: { year: 1540, roll: 0.4, x: R, y: 134, box: box(1440, 40, 1890, 212, 'rgba(24,16,10,.82)', '#d9b25c', 2, 6), size: 100, font: 'Marcellus-400', color: '#f3dc9a', shadow: { color: 'rgba(30,20,10,.7)', x: 3, y: 4, blur: 4 },
     label: { text: 'Persian miniature · Safavid', font: '34px "Marcellus-400"', color: '#f3dc9a', y: 184, shadow: { color: 'rgba(30,20,10,.7)', x: 2, y: 3, blur: 4 } } } },
 { id: '17_ink', name: '水墨写意', eighths: 11, transition: { type: 'inkBloom', dur: 0.45, cx: 560, cy: 740 },
   counter: { year: 1690, roll: 0.4, x: R, y: 132, size: 100, font: 'LXGWWenKai-500', color: '#1a1612', spacing: 4, label: { text: 'Chinese ink · Bada Shanren', font: '34px "Marcellus-400"', color: '#3a2c22', y: 186, spacing: 4 } } },
];
