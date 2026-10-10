/* Explicit legacy caller adapter; original SIG tasks are not overwritten. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
name = tasker.getVariable("par1");
value = tasker.getVariable("par2");
request = null;
for (family : new String[] {"Volume", "Balance", "Tinnitus"}) {
    for (operation : new String[] {"Current", "Set", "Max", "Mute", "Sharp", "Soft"}) {
        if (("SIG_" + family + operation).equals(name)) {
            if (operation.equals("Set") && (value == null || value.length() == 0)) value = tasker.getVariable("SIG_Target" + family);
            if (operation.equals("Set") && (value == null || !value.matches("-?[0-9]+"))) throw new JavaCodeException("Supply the absolute target in Parameter 2");
            if ((family.equals("Balance") && (operation.equals("Max") || operation.equals("Mute"))) || (!family.equals("Balance") && (operation.equals("Sharp") || operation.equals("Soft"))))
                throw new JavaCodeException("Unsupported legacy operation");
            request = family + "," + operation + "," + (operation.equals("Set") ? value : "");
        }
    }
}
if ("SIG_BatteryCheck".equals(name)) request = "Battery,Check,listen";
if ("SIG_ProgramSwitch".equals(name)) {
    if (value == null || !value.matches("[1-6]")) throw new JavaCodeException("Supply the program slot in Parameter 2");
    request = "Program,Switch," + value;
}
if (request == null) throw new JavaCodeException("Unsupported legacy caller; use an absolute SIG3 command");
tasker.setVariable("sig3_legacy_request", request);
return "mapped";
