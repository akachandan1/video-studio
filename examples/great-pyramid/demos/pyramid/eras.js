// Kurzgesagt-style sample · "What's inside the Great Pyramid?" — one continuous world, one camera (no transitions).
//   preview index.html?film=demos/pyramid   render: render.py --film demos/pyramid --solo pyr --no-counter --from 0 --to 16 --fps 30
window.PUNCH = 0;
window.FONT_FACES = (window.FONT_FACES || []).concat([]);
window.SCENE_LIBS = ['demos/pyramid/pyramid.js'];
window.ERAS = [{ id: 'pyr', dur: 16 }];
