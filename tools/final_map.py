"""Final 3-way song mapping:
  chunk<->song via Hungarian assignment on note counts (scipy)
  chunk<->MSM group via chart duration (ticks->seconds using audio-detected BPM)
Outputs assets/ssq/song_map.json + printed table.
"""
import json, wave, numpy as np, struct, sys
from match_songs import WIKI, DIFF_ORDER, parsed  # reuse table + parsed charts
from scipy.optimize import linear_sum_assignment

# --- 1. cost matrix: chunk x song ---
def sig_of(r):
    sig = []
    for did in DIFF_ORDER:
        sec = next((s for s in r['sections'] if s['diff'] == did), None)
        sig.append(sum(1 for a in sec['arrows'] if a & 0xFF) if sec else 0)
    return sig

chunks = sorted(k for k, v in parsed.items() if v['sections'])
cost = np.zeros((len(chunks), len(WIKI)))
for i, c in enumerate(chunks):
    sig = sig_of(parsed[c])
    for j, w in enumerate(WIKI):
        cost[i, j] = sum(abs(a - b) for a, b in zip(sig, w[1:]))
rows, cols = linear_sum_assignment(cost)
chunk2song = {chunks[r]: cols[r] for r in rows}

# --- 2. BPM detection on MSM song wavs (onset envelope autocorrelation) ---
def detect_bpm(path):
    w = wave.open(path, 'rb')
    rate = w.getframerate()
    n = w.getnframes()
    w.setpos(n // 4)  # skip intro
    data = w.readframes(min(n // 2, rate * 45))
    a = np.frombuffer(data, dtype='<i2').astype(float)
    if w.getnchannels() == 2:
        a = a[0::2]
    w.close()
    # onset envelope: rectified derivative of |signal| in 512-hop frames
    hop = 512
    frames = [np.abs(a[i:i + hop]).mean() for i in range(0, len(a) - hop, hop)]
    e = np.diff(frames)
    e[e < 0] = 0
    fr = rate / hop
    ac = np.correlate(e - e.mean(), e - e.mean(), 'full')[len(e) - 1:]
    lo, hi = int(fr * 60 / 200), int(fr * 60 / 60)  # 60-200 BPM
    lag = lo + np.argmax(ac[lo:hi])
    return 60 * fr / lag

idx = json.load(open('sound_out/wav/index.json'))
groups = {}
for rel, meta in idx.items():
    p = rel.split('/')
    if p[0] == 'sfx' and meta['dur'] > 80 and '00000 ' in p[2]:
        groups[p[1]] = meta['dur']

print('song assignments (chunk -> wiki song, cost):')
songdur = {}
for c in chunks:
    j = chunk2song[c]
    name, counts = WIKI[j][0], WIKI[j][1:]
    sig = sig_of(parsed[c])
    err = sum(abs(a - b) for a, b in zip(sig, counts))
    r = parsed[c]
    last_tick = max(s['last_tick'] for s in r['sections'])
    print(f"  {c} -> {name:32s} err={err:3d} last_tick={last_tick:#x}")
    songdur[c] = (name, last_tick, err)
json.dump({c: v[0] for c, v in songdur.items()}, open('assets/ssq/song_map.json', 'w'), indent=1)

# --- 3. bpm + duration matching ---
print('\nMSM groups (song pairs) with detected BPM:')
gr = sorted(groups)
bpms = {}
for g in gr:
    wav = f"sound_out/wav/sfx/{g}/00000.wav"
    import glob
    cand = glob.glob(f'sound_out/wav/sfx/{g}/*.wav')
    if not cand:
        continue
    bpm = detect_bpm(cand[0])
    bpms[g] = bpm
    print(f"  group {g}: {groups[g]:6.1f}s bpm~{bpm:6.1f}")

print('\nchunk -> best MSM group by duration (ticks at 16384/beat):')
used = set()
for c in chunks:
    name, last_tick, _ = songdur[c]
    best = None
    for g, bpm in bpms.items():
        dur = last_tick / 16384 * 60 / bpm
        d = abs(dur - groups[g])
        if best is None or d < best[1]:
            best = (g, d, dur)
    g, d, dur = best
    used.add(g)
    print(f"  {c} {name:30s} est {dur:6.1f}s -> group {g} ({groups[g]}s) delta {d:5.1f}")
