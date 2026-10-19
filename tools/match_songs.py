"""Match ssq chunks to song names via mariowiki note counts.
Our parser counts each entry once; wiki counts jumps (2 arrows) as 2 notes.
Difficulty ids: 4=Easy, 1=Normal, 2=Hard, 3=VeryHard, 6=SuperHard.
"""
import json, itertools

WIKI = [
    ("Here We Go!", 37, 47, 110, 145, 193),
    ("Underground Mozart", 43, 53, 173, 222, 293),
    ("Pipe Pop", 49, 59, 145, 186, 260),
    ("Garden Boogie", 42, 54, 154, 201, 280),
    ("Destruction Dance", 45, 19, 148, 188, 237),
    ("Jump! Jump! Jump!", 56, 80, 112, 187, 256),
    ("Fishing Frenzy", 61, 97, 126, 160, 235),
    ("Pirate Dance", 51, 104, 142, 199, 258),
    ("In the Whirlpool", 76, 100, 125, 160, 224),
    ("Step by Step", 79, 90, 116, 155, 232),
    ("Blooper Bop", 60, 73, 126, 149, 190),
    ("Hammer Dance", 68, 95, 152, 196, 270),
    ("Rollercoasting", 114, 127, 146, 184, 243),
    ("Boo Boogie", 60, 73, 126, 149, 207),
    ("Moustache, Barrel, and Gorilla", 116, 116, 143, 173, 240),
    ("Starring Wario!", 114, 112, 140, 183, 268),
    ("Frozen Pipes", 116, 116, 143, 173, 240),
    ("Cabin Fever", 111, 132, 169, 201, 219),
    ("Ms. Mowz's Song", 121, 135, 175, 213, 239),
    ("Deep Freeze", 125, 147, 190, 237, 250),
    ("Rendezvous on Ice", 116, 129, 194, 248, 255),
    ("Midnight Drive", 129, 131, 169, 209, 224),
    ("Always Smiling", 107, 116, 144, 179, 293),
    ("Bowser's Castle", 126, 146, 177, 268, 337),
    ("Up, Down, Left, Right", 28, 36, 131, 159, 231),
    ("Choir on the Green", 47, 60, 124, 153, 203),
    ("Hop, Mario!", 62, 75, 136, 160, 216),
    ("Where's the Exit?", 61, 80, 141, 181, 266),
    ("Piroli", 60, 72, 142, 167, 252),
]

DIFF_ORDER = [4, 1, 2, 3, 6]  # Easy, Normal, Hard, VeryHard, SuperHard

def popcount2(v):
    return bin(v & 0xF).count('1')

parsed = json.load(open('assets/ssq/parsed.json'))

chunk_sigs = {}
for name, r in parsed.items():
    sig = []
    for did in DIFF_ORDER:
        sec = next((s for s in r['sections'] if s['diff'] == did), None)
        if not sec:
            sig.append(None)
            continue
        # count entries; jumps (2 bits) count as 2 for the wiki-style figure
        # entries are byte pairs (mask, gimmick); wiki counts entries with mask!=0
        masks = [a & 0xFF for a in sec['arrows']]
        steps = sum(1 for m in masks if m != 0)
        sig.append((steps, len(masks)))
    chunk_sigs[name] = sig

def score(sig, wiki):
    s = 0
    for (plain, j2), w in zip(sig, wiki):
        if plain is None:
            s += 999
            continue
        s += min(abs(plain - w), abs(j2 - w))
    return s

assign = {}
for name, sig in sorted(chunk_sigs.items()):
    if all(s is None for s in sig):
        print(f"{name}: EMPTY (credits/dummy chunk?)")
        continue
    best = min(range(len(WIKI)), key=lambda i: score(sig, WIKI[i][1:]))
    sc = score(sig, WIKI[best][1:])
    ours = '/'.join(str(s[1]) if s else '-' for s in sig)
    wiki = '/'.join(map(str, WIKI[best][1:]))
    assign[name] = WIKI[best][0]
    flag = 'OK ' if sc == 0 else f'~{sc}'
    print(f"{name} -> {WIKI[best][0]:32s} [{flag}] ours {ours}  wiki {wiki}")

# dump handled by grid_map.py
