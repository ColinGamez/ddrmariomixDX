import json, numpy as np, sys
from scipy.optimize import linear_sum_assignment
sys.path.insert(0, 'tools')
from match_songs import WIKI

parsed = json.load(open('assets/ssq/parsed.json'))
DIFF_ORDER = [4, 1, 2, 3, 6]
chunks = sorted(k for k, v in parsed.items() if v['sections'])
types = sorted({a & 0xFF for r in parsed.values() for s in r['sections'] for a in s['arrows']})
print("gimmick types:", types, flush=True)

# per chunk/diff: total entries and count of each type among mask==0 entries
base = np.zeros((len(chunks), 5))
tcnt = np.zeros((len(chunks), 5, len(types)))
for i, c in enumerate(chunks):
    for k, did in enumerate(DIFF_ORDER):
        sec = next((s for s in parsed[c]['sections'] if s['diff'] == did), None)
        if not sec:
            continue
        ar = sec['arrows']
        base[i, k] = sum(1 for a in ar if (a >> 8) != 0)
        for a in ar:
            if (a >> 8) == 0:
                t = a & 0xFF
                tcnt[i, k, types.index(t)] += 1

wiki = np.array([w[1:] for w in WIKI])  # 29x5
lo, hi = int(sys.argv[1]), int(sys.argv[2])
best = (1e18, None, None)
for bits in range(lo, hi):
    sel = np.array([1 if bits >> k & 1 else 0 for k in range(len(types))])
    sigs = base + tcnt @ sel          # 29x5
    cost = np.abs(sigs[:, None, :] - wiki[None, :, :]).sum(axis=2)
    rows, cols = linear_sum_assignment(cost)
    tot = cost[rows, cols].sum()
    if tot < best[0]:
        best = (tot, bits, (rows, cols, cost, sigs))
        print(f"bits {bits:#x} types {[types[k] for k in range(len(types)) if bits>>k&1]} total {tot}", flush=True)

tot, bits, (rows, cols, cost, sigs) = best
extra = [types[k] for k in range(len(types)) if bits >> k & 1]
print("BEST", tot, "stepped types:", extra)
m = {}
for r, c in zip(rows, cols):
    m[chunks[r]] = WIKI[c][0]
    print(f"{chunks[r]} -> {WIKI[c][0]:32s} cost={cost[r,c]:5.0f} ours={list(sigs[r].astype(int))} wiki={list(WIKI[c][1:])}")
json.dump(m, open('assets/ssq/song_map.json', 'w'), indent=1)
