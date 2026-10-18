// Scene written for the huashu-art-motion engine (uses its PAINT/TOON/CAM APIs) · engine: MIT License (c) 2026 alchaincyf (花叔 · 花生) · https://github.com/alchaincyf/huashu-art-motion
// Kurzgesagt-style sample · "What's inside the Great Pyramid?" — one continuous world, one camera (no transitions).
//   preview index.html?film=demos/pyramid   render: render.py --film demos/pyramid --solo pyr --no-counter --from 0 --to 16 --fps 30
window.PUNCH = 0;
window.FONT_FACES = (window.FONT_FACES || []).concat([]);
window.SCENE_LIBS = ['demos/pyramid/pyramid.js'];
window.ERAS = [{ id: 'pyr', dur: 16 }];
