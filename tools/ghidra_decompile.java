// Decompiles functions at given DOL addresses and prints pseudo-C.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;

public class ghidra_decompile extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] addrs = getScriptArgs()[0].toString().split(",");
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        for (String a : addrs) {
            Address addr = toAddr(a.trim());
            var f = getFunctionAt(addr);
            if (f == null) f = getFunctionContaining(addr);
            if (f == null) { println("### " + a + ": no function"); continue; }
            var res = ifc.decompileFunction(f, 30, monitor);
            println("### " + f.getName() + " @ " + f.getEntryPoint());
            if (res.decompileCompleted()) {
                println(res.getDecompiledFunction().getC());
            } else {
                println("(decompile failed: " + res.getErrorMessage() + ")");
            }
        }
        ifc.dispose();
    }
}
