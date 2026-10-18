// Scene written for the huashu-art-motion engine (uses its PAINT/TOON/CAM APIs) · engine: MIT License (c) 2026 alchaincyf (花叔 · 花生) · https://github.com/alchaincyf/huashu-art-motion
// 'The Brief' · art blitz: the Dot speaker repainted in nine styles (0.8 s each, hard cuts on the beat) + Kurzgesagt-style exploded view.
window.PUNCH = 0;
window.SCENE_LIBS = ['demos/blitz/blitz.js'];
const NOC = { draw() {} };
const CUT = { type: 'cut', dur: 0.01 };
window.ERAS = ['vg', 'pop', 'ink', 'px', 'kus', 'cub', 'mos', 'mon', 'mat'].map((id, i) => ({ id: 'b_' + id, dur: 0.8, counter: NOC, ...(i ? { transition: CUT } : {}) }))
  .concat([{ id: 'b_inside', dur: 2.4, counter: NOC, transition: CUT }]);
