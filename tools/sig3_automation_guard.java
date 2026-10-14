/* Automatic changes must not take over another app by default. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
denyAutomation(message) {
    // Tasker can abort this child on JavaCodeException before its following error guard.
    // Preserve the reason for the worker's final report before throwing.
    tasker.setVariable("SIG3_Error", message);
    throw new JavaCodeException(message);
}
if ("1".equals(tasker.getVariable("SIG3_AutomationCancelled"))) denyAutomation("Automatic change cancelled");
if ("1".equals(tasker.getVariable("SIG3_ManualOverride"))) denyAutomation("Manual override blocks automatic changes");
if (!"0".equals(tasker.getVariable("SIG3_DeferAutomation"))) {
    service = tasker.getAccessibilityService();
    root = service == null ? null : service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        denyAutomation("Automatic change deferred until Signia is foreground");
}
return "allowed";
