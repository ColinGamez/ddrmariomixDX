// Decompile all functions whose entry point lies in [start, end).
// Args: <hex start> <hex end>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;

public class ghidra_range extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        long start = Long.parseLong(args[0], 16);
        long end = Long.parseLong(args[1], 16);
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            long ep = f.getEntryPoint().getOffset();
            if (ep >= start && ep < end) {
                println("##### " + f.getName() + " @ " + f.getEntryPoint());
                DecompileResults r = decomp.decompileFunction(f, 60, monitor);
                if (r.decompileCompleted()) {
                    println(r.getDecompiledFunction().getC());
                } else {
                    println("decompile failed: " + r.getErrorMessage());
                }
            }
        }
    }
}
