# Group tracker frames into click / scroll events with the cursor position at each.
#   python3 events.py <track.json> <events.json>
# A big UI change with the cursor at rest just before it = click; mostly vertical phase shift = scroll.
# Each event has 'still' (seconds the cursor rested first) — high values are the most reliable clicks.
import json, bisect, sys
d=json.load(open(sys.argv[1]))
S=d['samples']; F=d['frames']
ts=[s[0] for s in S]
def cur_at(t):
    i=bisect.bisect_right(ts,t)-1
    return S[i] if i>=0 else None
def last_move(t):
    i=bisect.bisect_right(ts,t)-1
    while i>=0 and not S[i][3]: i-=1
    return S[i][0] if i>=0 else -9
big=[f for f in F if f[1]>=900]
ev=[];cur=None
for f in big:
    if cur and f[0]-cur['t1']<0.4: cur['t1']=f[0]; cur['n']=max(cur['n'],f[1]); cur['dy'].append(f[3]); cur['bb'].append(f[2])
    else:
        cur={'t0':f[0],'t1':f[0],'n':f[1],'dy':[f[3]],'bb':[f[2]]}; ev.append(cur)
out=[]
for e in ev:
    c=cur_at(e['t0']-0.05)
    if not c: continue
    dys=[abs(x) for x in e['dy'] if abs(x)>2]
    kind='scroll' if dys and len(dys)>=len(e['dy'])/2 else 'click'
    bb=e['bb'][0]
    # union bbox
    xs=[b[0] for b in e['bb']]+[b[2] for b in e['bb']]; ys=[b[1] for b in e['bb']]+[b[3] for b in e['bb']]
    out.append({'t':round(e['t0'],2),'kind':kind,'x':c[1],'y':c[2],'n':e['n'],'bbox':[min(xs),min(ys),max(xs),max(ys)],'still':round(e['t0']-last_move(e['t0']),2)})
json.dump({'events':out,'samples':S[::3]},open(sys.argv[2],'w'))
print(len(out), sum(o['kind']=='click' for o in out))
