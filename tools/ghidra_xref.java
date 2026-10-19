// Find xrefs to an address and decompile the containing functions.
// Args: <hex address>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;

public class ghidra_xref extends GhidraScript {
    public void run() throws Exception {
        String arg = getScriptArgs()[0];
        Address addr = toAddr(Long.parseLong(arg, 16));
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        for (Reference ref : getReferencesTo(addr)) {
            Address from = ref.getFromAddress();
            Function f = getFunctionContaining(from);
            println("xref from " + from + " in " + (f == null ? "?" : f.getName() + " @ " + f.getEntryPoint()));
            if (f != null) {
                DecompileResults r = decomp.decompileFunction(f, 60, monitor);
                if (r.decompileCompleted()) {
                    println(r.getDecompiledFunction().getC());
                } else {
                    println("decompile failed: " + r.getErrorMessage());
                }
                println("=====");
            }
        }
    }
}
