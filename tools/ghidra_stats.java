// Prints program stats
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class ghidra_stats extends GhidraScript {
    @Override
    public void run() throws Exception {
        var fm = currentProgram.getFunctionManager();
        int total = 0, named = 0;
        for (Function f : fm.getFunctions(true)) {
            total++;
            if (!f.getName().startsWith("FUN_")) named++;
        }
        println("=== STATS " + currentProgram.getName() + " ===");
        println("functions: " + total + " (named: " + named + ")");
        for (var b : currentProgram.getMemory().getBlocks()) {
            println("  block " + b.getName() + " @ " + b.getStart() + " size=0x" + Long.toHexString(b.getSize()));
        }
    }
}
