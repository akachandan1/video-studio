// 十二位画家样片：skill 里 35 种风格（15 原段＋迁移测试 A–D 的 20 段）各一段，按年代排，用作回归测试与风格目录。
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
 { id: '32_rembrandt', name: '伦勃朗明暗法', eighths: 9, transition: { type: 'chiaroscuro', dur: 0.45, cx: 580, cy: 300 },
   counter: { year: 1642, roll: 0.4, x: R, y: 134, size: 104, font: 'CormorantGaramond-500', color: '#e9c98a', spacing: 10, label: { text: 'Rembrandt · chiaroscuro', font: '34px "IMFellEnglish-400i"', color: '#c9a467', y: 184 } } },
 { id: '29_seurat', name: '修拉点彩', eighths: 9, transition: { type: 'pointill', dur: 0.34 },
   counter: { year: 1884, roll: 0.4, x: R, y: 134, size: 100, font: 'Marcellus-400', color: '#20306a', spacing: 6,
     label: { text: 'SEURAT · LA GRANDE JATTE', font: '27px "Marcellus-400"', color: '#7a3a2a', y: 182, spacing: 2 } } },
 { id: '09_postimp', name: '后印象派（梵高）', eighths: 9, transition: { type: 'swirl', dur: 0.28, cx: 560, cy: 340 },
   counter: { year: 1889, roll: 0.4, x: R, y: 134, size: 104, font: 'LilitaOne-400', color: '#f5d03b', shadow: { color: '#2a2a6a', x: 3, y: 4 },
     label: { text: 'Van Gogh · Post-Impressionism', font: '34px "LilitaOne-400"', color: '#f5d03b', y: 182, shadow: { color: '#2a2a6a', x: 2, y: 3 } } } },
 { id: '19_munch', name: '蒙克表现主义', eighths: 9, transition: { type: 'screamWarp', dur: 0.5 },
   counter: { year: 1893, roll: 0.4, x: R, y: 134, size: 100, font: 'IMFellEnglish-400', color: '#f6c040', shadow: { color: 'rgba(40,10,20,.6)', x: 4, y: 4 }, label: { text: 'Munch · The Scream', font: '38px "IMFellEnglish-400i"', color: '#f8d88a', y: 184, shadow: { color: 'rgba(40,10,20,.6)', x: 2, y: 3 } } } },
 { id: '28_monet', name: '莫奈睡莲', eighths: 9, transition: { type: 'ripple', dur: 0.34, cx: 1000, cy: 600 },
   counter: { year: 1899, roll: 0.4, x: R, y: 136, size: 104, font: 'PlayfairDisplay-400i', color: '#3e5a86', spacing: 4, shadow: { color: 'rgba(252,248,238,1)', blur: 18, x: 0, y: 0 },
     label: { text: 'Monet · Nymphéas', font: '36px "PlayfairDisplay-400i"', color: '#4a5f8e', y: 186, shadow: { color: 'rgba(252,248,238,1)', blur: 14, x: 0, y: 0 } } } },
 { id: '18_klimt', name: '克里姆特金色时期', eighths: 9, transition: { type: 'goldLeaf', dur: 0.5, cx: 1300, cy: 380 },
   counter: { year: 1907, roll: 0.4, x: R, y: 134, size: 100, font: 'Marcellus-400', color: '#f6dc8a', shadow: { color: 'rgba(40,24,6,.7)', x: 3, y: 4, blur: 6 }, label: { text: 'Klimt · Golden Phase', font: '34px "Marcellus-400"', color: '#f3d27a', y: 186, shadow: { color: 'rgba(40,24,6,.7)', x: 2, y: 3, blur: 4 } } } },
 { id: '23_dali', name: '达利超现实', eighths: 9, transition: { type: 'melt', dur: 0.36 },
   counter: { year: 1931, roll: 0.4, x: R, y: 136, size: 104, font: 'PlayfairDisplay-700i', color: '#f6e8c8', shadow: { color: 'rgba(10,20,50,.55)', x: 5, y: 5, blur: 4 },
     label: { text: 'Dalí · Surrealism', font: '34px "PlayfairDisplay-400i"', color: '#f0dcae', y: 184 } } },
 { id: '24_hopper', name: '霍珀美国现实主义', eighths: 9, transition: { type: 'sunShaft', dur: 0.34 },
   counter: { year: 1942, roll: 0.4, x: R, y: 134, size: 100, font: 'LibreBaskerville-700', color: '#f3e3b5', shadow: { color: 'rgba(20,30,25,.55)', x: 4, y: 4 },
     label: { text: 'HOPPER · AMERICAN REALISM', font: '27px "LibreBaskerville-400"', color: '#f0dca8', y: 182, spacing: 3 } } },
 { id: '30_matisse', name: '马蒂斯剪纸', eighths: 9, transition: { type: 'cutouts', dur: 0.36 },
   counter: { year: 1947, roll: 0.4, x: R, y: 136, size: 108, font: 'Caveat-600', color: '#111', spacing: 2,
     label: { text: 'Matisse · Jazz', font: '46px "Caveat-600"', color: '#c8242a', y: 188 } } },
 { id: '13_pop', name: '波普艺术', eighths: 9, transition: { type: 'zigzag', dur: 0.16 },
   counter: { year: 1962, roll: 0.4, x: 1852, y: 144, size: 104, font: 'Anton-400', color: '#111',
     box: c => { c.save(); c.fillStyle = '#111'; c.fillRect(1637, 40, 253, 170); c.fillStyle = '#f7e23a'; c.fillRect(1643, 46, 241, 158); c.restore(); },
     label: { text: 'LICHTENSTEIN', font: '28px "Anton-400"', color: '#111', x: 1852, y: 192, spacing: 1 } } },
 { id: '21_kusama', name: '草间弥生波点', eighths: 9, transition: { type: 'dotBloom', dur: 0.48, cx: 540, cy: 760 },
   counter: { year: 1965, roll: 0.4, x: R, y: 134, size: 104, font: 'Poppins-800', color: '#ffffff', shadow: { color: '#141414', x: 5, y: 5 }, label: { text: 'Kusama · Infinity Dots', font: '32px "Poppins-800"', color: '#ffffff', y: 186, shadow: { color: '#141414', x: 3, y: 3 } } } },
 { id: '31_haring', name: '哈林涂鸦', eighths: 9, transition: { type: 'radiant', dur: 0.32, cx: 1000, cy: 600 },
   counter: { year: 1982, roll: 0.4, x: R, y: 136, size: 108, font: 'Kalam-700', color: '#111', spacing: 2,
     label: { text: 'KEITH HARING', font: '40px "Kalam-700"', color: '#111', y: 188, spacing: 2 } } },
];
