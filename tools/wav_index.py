import os, wave, json
idx = {}
for cat in ('music', 'sfx'):
    base = os.path.join('sound_out/wav', cat)
    for root, _, files in os.walk(base):
        for f in sorted(files):
            if not f.endswith('.wav'):
                continue
            p = os.path.join(root, f)
            w = wave.open(p, 'rb')
            rel = os.path.relpath(p, 'sound_out/wav').replace(os.sep, '/')
            idx[rel] = {'dur': round(w.getnframes() / w.getframerate(), 1),
                        'ch': w.getnchannels(), 'rate': w.getframerate()}
            w.close()
json.dump(idx, open('sound_out/wav/index.json', 'w'), indent=0)
long = [(k, v['dur']) for k, v in idx.items() if v['dur'] > 60]
long.sort(key=lambda x: -x[1])
for k, d in long[:50]:
    print(f"{d:7.1f}s  {k}")
print(len(idx), "total wavs")
