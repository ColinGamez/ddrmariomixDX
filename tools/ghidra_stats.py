# Prints program stats: function count, defined symbols, strings
from ghidra.program.model.symbol import SymbolType

fm = currentProgram.getFunctionManager()
funcs = list(fm.getFunctions(True))
named = [f for f in funcs if not f.getName().startswith("FUN_")]
print("=== STATS for %s ===" % currentProgram.getName())
print("functions: %d (named: %d)" % (len(funcs), len(named)))
print("memory blocks:")
for b in currentProgram.getMemory().getBlocks():
    print("  %s @ %s size=%x" % (b.getName(), b.getStart(), b.getSize()))
