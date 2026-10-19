# Song slot map — ddrmariomixDX

Three-way mapping between chart data (`ssq.bin` chunks), music audio
(`MRODDR_Snd.msm` groups) and story stages. Rebuilt by `tools/grid_map.py`
(chart↔song, Hungarian assignment on wiki note counts) and verified by
implied BPM (see below).

## Key facts

- **ssq timestamps: 1024 ticks/beat** (not 16384 — earlier guess was 16x off).
- **Arrow entry = BE u16: high byte = arrow bitmask (L=1 D=2 U=4 R=8),
  low byte = Mush Mode gimmick type.** Entries with mask 0 are gimmick-only
  markers; gimmick types 0-6, 8, 9 are stepped (counted by wiki note
  counts), 7/15 avoided (Spiny family), 84/88 = alignment padding artifacts.
- **MSM group `0004 + k` = song k** in the order below (sample IDs run
  0x015B + 2k for L, +1 for R). Verified: using chart last-tick ÷ 1024 =
  beats and audio duration, implied BPM lands in [99, 179] for all 29 songs
  (median 130) — only consistent at 1024 ticks/beat AND this group order.
- `ssq.bin` chunk027 is empty = the credits theme (original NES Ground BGM,
  streamed separately).
- Chart↔song confidence: exact (cost ≤ 3) for Choir on the Green,
  Where's the Exit?, Hop, Mario!, Piroli; strong (≤ 40) for most others;
  lower confidence (~50-130) for Garden Boogie, Always Smiling, Boo Boogie,
  Hammer Dance, Rendezvous on Ice, Frozen Pipes, Starring Wario!,
  Moustache Barrel and Gorilla (Mush Mode gimmick counting differences).
- d0XX stage DLL ↔ song link is **assumed** to follow story order; the
  definitive table lives in main.dol (TODO: find the song-info array).

## Table (story order; shop songs 24-28 at end)

| # | Song | Stage | ssq chunk | MSM group | ~BPM | Audio |
|---|---|---|---|---|---|---|
| 0 | Here We Go! | 1-1 | chunk010 | 0004 | 100 | 93.9s |
| 1 | Underground Mozart | 1-2 | chunk002 | 0005 | 179 | 98.0s |
| 2 | Pipe Pop | 1-2EX | chunk005 | 0006 | 117 | 106.3s |
| 3 | Garden Boogie | 1-3 | chunk001 | 0007 | 155 | 86.5s |
| 4 | Destruction Dance | 1-4 | chunk019 | 0008 | 141 | 96.8s |
| 5 | Jump! Jump! Jump! | 2-1 | chunk013 | 0009 | 134 | 101.8s |
| 6 | Fishing Frenzy | 2-2 | chunk003 | 000A | 129 | 92.9s |
| 7 | Pirate Dance | 2-2EX | chunk015 | 000B | 147 | 96.2s |
| 8 | In the Whirlpool | 2-3 | chunk000 | 000C | 125 | 94.4s |
| 9 | Step by Step | 2-3EX | chunk016 | 000D | 113 | 91.7s |
| 10 | Blooper Bop | 2-4 | chunk011 | 000E | 112 | 95.6s |
| 11 | Hammer Dance | 3-1 | chunk012 | 000F | 164 | 96.7s |
| 12 | Rollercoasting | 3-2 | chunk017 | 0010 | 134 | 104.2s |
| 13 | Boo Boogie | 3-3 | chunk014 | 0011 | 121 | 93.2s |
| 14 | Moustache, Barrel, and Gorilla | 3-3EX | chunk006 | 0012 | 142 | 89.4s |
| 15 | Starring Wario! | 3-4 | chunk020 | 0013 | 132 | 90.7s |
| 16 | Frozen Pipes | 4-1 | chunk028 | 0014 | 119 | 105.2s |
| 17 | Cabin Fever | 4-2 | chunk024 | 0015 | 137 | 98.0s |
| 18 | Ms. Mowz's Song | 4-2EX | chunk023 | 0016 | 139 | 95.3s |
| 19 | Deep Freeze | 4-3 | chunk021 | 0017 | 130 | 107.2s |
| 20 | Rendezvous on Ice | 4-4 | chunk004 | 0018 | 121 | 99.6s |
| 21 | Midnight Drive | 4-4EX | chunk022 | 0019 | 125 | 96.1s |
| 22 | Always Smiling | 5-1 | chunk008 | 001A | 125 | 99.6s |
| 23 | Bowser's Castle | 5-2 | chunk018 | 001B | 175 | 96.3s |
| 24 | Up, Down, Left, Right | shop | chunk007 | 001C | 119 | 107.0s |
| 25 | Choir on the Green | shop | chunk009 | 001D | 129 | 92.9s |
| 26 | Hop, Mario! | shop | chunk025 | 001E | 113 | 106.7s |
| 27 | Where's the Exit? | shop | chunk026 | 001F | 154 | 88.7s |
| 28 | Piroli | shop | chunk029 | 0020 | 136 | 93.8s |

(chunk assignments for rows 17-19/21: Deep Freeze=chunk021 per Hungarian
cost table; stage column from mariowiki song order.)
