// Decompiles ALL functions in the current program, prints pseudo-C.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;

public class ghidra_decompile_all extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        for (var f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.getName().startsWith("_")) continue;
            var res = ifc.decompileFunction(f, 60, monitor);
            println("### " + f.getName() + " @ " + f.getEntryPoint());
            if (res.decompileCompleted()) {
                println(res.getDecompiledFunction().getC());
            } else {
                println("(failed: " + res.getErrorMessage() + ")");
            }
        }
        ifc.dispose();
    }
}
