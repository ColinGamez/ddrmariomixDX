"""Compiler flag sweep: compile a unit with many flag combos, score vs original asm."""
import subprocess, re, sys, os

ROOT = r"C:\Users\Colin\Desktop\DDR Mario Mix\decomp"
MWCC_DIR = os.path.join(ROOT, r"build\compilers\GC")
OBJDUMP = r"C:\devkitPro\devkitPPC\bin\powerpc-eabi-objdump.exe"

def norm(lines):
    out = []
    for ln in lines:
        m = re.match(r"\s*[0-9a-f]+:\s+[0-9a-f ]+\t(\S+)\s*(.*)", ln)
        if not m: continue
        op, rest = m.group(1), m.group(2)
        out.append(op)
    return out

def orig_instrs(asmfile, fn):
    txt = open(asmfile, encoding="utf-8", errors="replace").read()
    m = re.search(r"\.fn %s,.*?\.endfn" % re.escape(fn), txt, re.S)
    if not m: return None
    lines = []
    for ln in m.group(0).splitlines():
        c = re.search(r"\*/\s*(\w+)\s*(.*)", ln)
        if c: lines.append("    0:\t00 00 00 00 \t%s\t%s" % (c.group(1), c.group(2)))
    return norm(lines)

def compiled_instrs(obj, fn):
    out = subprocess.run([OBJDUMP, "-d", obj], capture_output=True, text=True).stdout
    sec = re.search(r"<%s>:\n(.*?)(?:\n\n|\Z)" % re.escape(fn), out, re.S)
    if not sec: return None
    return norm(sec.group(1).splitlines())

def score(a, b):
    n = max(len(a), len(b))
    same = sum(1 for x, y in zip(a, b) if x == y)
    return same / n if n else 0

BASE = ["-nodefaults","-proc","gekko","-align","powerpc","-enum","int","-fp","hardware",
        "-Cpp_exceptions","off","-inline","auto","-maxerrors","1","-nosyspath","-RTTI","off",
        "-sdata","0","-sdata2","0"]

COMBOS = []
for o in ["-O1","-O2","-O2,p","-O2,s","-O3","-O4,p","-O4","-O3,p"]:
    for opt in [[], ["-opt","nopeephole"], ["-opt","nostrength"], ["-opt","nopeephole,nostrength,noloop"]]:
        COMBOS.append([o]+opt)

def sweep(ver, src, asmfile, fn, tmp=r"C:\Users\Colin\Desktop\DDR Mario Mix\tools\sweep_tmp.o"):
    orig = orig_instrs(asmfile, fn)
    best = []
    for flags in COMBOS:
        r = subprocess.run([os.path.join(MWCC_DIR, ver, "mwcceppc.exe")] + BASE + flags +
                           ["-c", src, "-o", tmp], capture_output=True)
        if r.returncode != 0: continue
        comp = compiled_instrs(tmp, fn)
        if comp: best.append((score(orig, comp), " ".join(flags), len(orig), len(comp)))
    best.sort(reverse=True)
    for s, f, lo, lc in best[:5]:
        print(f"  {s*100:5.1f}%  [{f}]  orig {lo} instrs, got {lc}")

if __name__ == "__main__":
    sweep(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
