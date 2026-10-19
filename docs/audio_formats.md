# DDR Mario Mix (GWZJ01) — audio formats

All offsets big-endian unless noted. Tools: `tools/msm_extract.py`,
`tools/pdt_extract.py`, `tools/dsp2wav.py`, plus Nisto's
`tools/musyx-extract/MusyXExtract.py` (cloned from github.com/Nisto/musyx-extract)
and the reference C sources in `tools/mpgc-sound-tools/` (Yoshimaster96,
github.com/Yoshimaster96/mpgc-sound-tools — note: its dump_pdt.c has a stereo
bug and a 4x stream-size bug; our Python ports fix both).

## MRODDR_Snd.msm — MusyX sample bank ("GSND" container)

Same archive as Mario Party 4-7.

```
0x00  char[4]  "GSND"
0x04  u32      version (2)
0x20  u32      group table offset   (0x100)
0x24  u32      group table size     (32 bytes/entry)
0x38  u32      group data chunk offset
0x3C  u32      group data chunk size
0x40  u32      sample data chunk offset
0x44  u32      sample data chunk size
```

Group table entry (32 bytes), entry 0 is a dummy — start at i=1:

```
+0x00  u16  group ID
+0x04  u32  group data offset (relative to group data chunk)
+0x08  u32  group data size
+0x0C  u32  samp offset (relative to sample data chunk)
+0x10  u32  samp size
```

Group data starts with 4 u32 offsets (relative to group data start):
pool, proj, sdir, SNG. Sizes are consecutive differences
(pool..proj, proj..sdir, sdir..SNG).

- **.pool** — sample pool metadata (MusyX)
- **.proj** — MusyX project (song/group definitions)
- **.sdir** — sample directory: per-sample DSP header info (coefs, rate,
  loop, offset into .samp)
- **.samp** — raw DSP ADPCM sample data

MusyXExtract.py converts an sdir/samp pair into standard .dsp files named
`ddddd (0xXXXX).dsp` (index + sample ID).

### What's in this game's bank (63 groups)

- groups `0000`-`0003`: menu/system SFX + instruments
- groups `0004`-`0022` (+ dupes 0029/002A, plus 003D/003E): **the ~30
  gameplay songs**, each group holding 2 long DSP samples = L and R channels
  (94-107 s @ 32000 Hz). Sample IDs run sequentially (0x015B, 0x015C, ...)
  so ID order is likely song order.
- remaining groups: character voices, announcer, per-stage SFX, instruments.

## MRODDR_Str.pdt — streamed music bank

PDT = a bank of DSP streams with a small header. 92 entries here.

```
0x00  u16  unknown (1)
0x02  u16  stream count
0x04  u32  unknown (4)
0x08  u32  default sample rate (32000)
0x0C  u32  unknown (2, channel count?)
0x10  u32  entry table offset
0x14  u32  coefficient table offset   (32 bytes per entry = 8 predictor pairs)
0x18  u32  stream header table offset
0x1C  u32  stream data offset
```

Entry table: u32 per stream -> stream header offset (0 = unused).

Stream header:

```
+0x00  u32  flags: 0x01000000 = stereo, 0x02000000 = loops
+0x04  u32  sample rate
+0x08  u32  nibble count (per channel)
+0x0C  u32  loop start (nibbles)
+0x10  u32  ch1 data offset        +0x14  u16  ch1 coefficient entry
+0x18  u32  ch2 data offset (stereo only)  +0x1C  u16  ch2 coef entry
```

Channel data = standard GameCube DSP ADPCM, contiguous per channel,
`ceil(nibbles/2)` bytes each (ch2 starts right after ch1).

Contents: streams 0000-0018 are looping music ~30-60 s (menu, world map,
cutscenes); 0019+ are non-looping jingles/stingers.

## GameCube DSP ADPCM (quick reference)

16-byte header fields at 0x00: sample count, nibble count, sample rate;
loop flag u16 @0x0C; loop start u32 @0x10; 16 s16 coefficients @0x1C
(8 predictor pairs); data at 0x60: 8-byte frames = 1 header byte
(predictor<<4 | scale) + 14 signed 4-bit samples. Decode:
`pcm = (nibble<<scale<<11) + 0x400 + c1*hist1 + c2*hist2 >> 11`, clip s16.

## Custom-music injection path (future)

1. Encode new song to DSP ADPCM 32000 Hz stereo (vgmstream's `test.exe -o`
   or our own encoder — decode is done, encode is the same math reversed).
2. Rebuild the target group's .samp/.sdir with MusyXExtract.py `-P` (pack
   mode expects `ddddd (0xXXXX).dsp` names), or splice the PDT.
3. Repack MSM with msm_extract.py's inverse (to be written).
4. Charts: pair with a new ssq.bin chunk at the same song slot.
