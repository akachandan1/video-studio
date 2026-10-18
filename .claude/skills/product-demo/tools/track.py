# Cursor + click + scroll tracker for a screen recording.
#   python3 track.py <recording.mp4> <track.json> [--crop x,y,w,h]
# Diff-based: small isolated blobs = cursor motion; big changes = UI change (click result / scroll / navigation).
# --crop trims browser chrome / black bars; output coords are in that CROPPED content space.
# Find the crop by pulling one frame (ffmpeg -ss 5 -i rec.mp4 -frames:v 1 f.png) and looking at it.
import argparse, cv2, json, sys, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--crop', default='')
A = ap.parse_args(); SRC, OUT = A.src, A.out
_cap = cv2.VideoCapture(SRC)
CX, CY, CW, CH = [int(v) for v in A.crop.split(',')] if A.crop else (0, 0, int(_cap.get(3)), int(_cap.get(4)))
_cap.release()
S = 0.5  # analysis scale

cap = cv2.VideoCapture(SRC)
fps = cap.get(cv2.CAP_PROP_FPS)
prev = None; t_i = 0
cursor = None
samples = []   # [t, x, y, moving]
frames = []    # per-frame: [t, changed_px, bbox, dy, resp]
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(f[CY:CY+CH, CX:CX+CW], cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_AREA)
    t = t_i / fps
    moving = 0
    if prev is not None:
        d = cv2.absdiff(g, prev)
        m = (d > 22).astype(np.uint8)
        n = int(m.sum())
        bbox = None; dy = 0.0; resp = 0.0
        if n:
            ys, xs = np.nonzero(m)
            bbox = [int(xs.min()/S), int(ys.min()/S), int(xs.max()/S), int(ys.max()/S)]
        if 0 < n < 900:
            k, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
            # cursor = small component(s); take the largest small one
            best = None
            for i in range(1, k):
                w, h, a = st[i, 2], st[i, 3], st[i, 4]
                if a >= 3 and w < 60 and h < 60 and (best is None or a > st[best, 4]):
                    best = i
            if best is not None:
                x, y, w, h = st[best, :4]
                # cursor tip ~ top-left of new position: use component centre (sub-frame lag is fine)
                cursor = [float(cen[best][0]/S), float(cen[best][1]/S)]
                moving = 1
        elif n >= 900:
            a = np.float32(prev); b = np.float32(g)
            (sx, sy), resp = cv2.phaseCorrelate(a, b)
            dy = float(sy / S)
        frames.append([round(t, 3), n, bbox, round(dy, 1), round(float(resp), 3)])
    if cursor is not None:
        samples.append([round(t, 3), round(cursor[0], 1), round(cursor[1], 1), moving])
    prev = g; t_i += 1
    if t_i % 3000 == 0: print(t_i, file=sys.stderr, flush=True)

json.dump({"fps": fps, "crop": [CX, CY, CW, CH], "samples": samples, "frames": frames}, open(OUT, "w"))
print("done", t_i)
