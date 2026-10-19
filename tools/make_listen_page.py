import os, json, wave

idx = json.load(open('sound_out/wav/index.json'))
# group songs: sfx groups whose files are long L/R pairs
html = ['''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>DDR Mario Mix - sound rip</title>
<style>
body{font-family:Segoe UI,sans-serif;background:#0b7285;color:#fff;margin:24px}
h1{font-weight:600} h2{margin-top:32px;border-bottom:2px solid #66d9e8;padding-bottom:4px}
.track{background:#1098ad33;border:1px solid #66d9e855;border-radius:10px;padding:8px 14px;margin:8px 0}
audio{width:100%;height:36px} .dur{color:#99e9f2;font-size:13px;margin-left:8px}
code{background:#0006;padding:1px 6px;border-radius:4px}
</style></head><body>
<h1>DDR Mario Mix - extracted audio</h1>
<p>Everything below was decoded from <code>MRODDR_Snd.msm</code> (MusyX sample bank) and
<code>MRODDR_Str.pdt</code> (stream bank). Songs are the long L/R pairs under
<b>MSM groups</b>; menu/cutscene music and jingles are the <b>PDT streams</b>;
short one-shots and instruments are the small MSM groups.</p>
''']

def row(rel, meta):
    return (f'<div class="track">{rel}<span class="dur">{meta["dur"]}s '
            f'{meta["ch"]}ch {meta["rate"]}Hz</span>'
            f'<audio controls preload="none" src="{rel}"></audio></div>')

# 1. song-length MSM pairs
html.append('<h2>Gameplay songs (MSM groups, L/R pairs)</h2>')
groups = {}
for rel, meta in idx.items():
    parts = rel.split('/')
    if parts[0] == 'sfx' and meta['dur'] > 80:
        groups.setdefault(parts[1], []).append((rel, meta))
for g in sorted(groups):
    html.append(f'<h3>group {g}</h3>')
    for rel, meta in sorted(groups[g]):
        html.append(row(rel, meta))

# 2. PDT streams
html.append('<h2>PDT streams (menu / cutscene music, jingles)</h2>')
for rel, meta in sorted(idx.items()):
    if parts := rel.split('/'):
        if parts[0] == 'music':
            html.append(row(rel, meta))

# 3. short SFX
html.append('<h2>SFX & instruments (short MSM samples)</h2>')
for rel, meta in sorted(idx.items()):
    parts = rel.split('/')
    if parts[0] == 'sfx' and meta['dur'] <= 80:
        html.append(row(rel, meta))

html.append('</body></html>')
open('sound_out/listen.html', 'w', encoding='utf-8').write('\n'.join(html))
print('written', os.path.getsize('sound_out/listen.html'), 'bytes')
