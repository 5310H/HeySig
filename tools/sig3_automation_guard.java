/* Automatic changes must not take over another app by default. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
denyAutomation(message) {
    // Tasker can abort this child on JavaCodeException before its following error guard.
    // Preserve the reason for the worker's final report before throwing.
    tasker.setVariable("SIG3_Error", message);
    if ("Noise".equals(tasker.getVariable("SIG3_Family"))) {
        tasker.setVariable("SIG3_NoiseCandidate", ""); tasker.setVariable("SIG3_NoiseStrikes", "0");
        tasker.setVariable("SIG3_AutoProgramSlot", "");
        tasker.setVariable("SIG3_NoiseStatus", "deferred; waiting for fresh samples");
    }
    throw new JavaCodeException(message);
}
if ("1".equals(tasker.getVariable("SIG3_AutomationCancelled"))) denyAutomation("Automatic change cancelled");
if ("1".equals(tasker.getVariable("SIG3_ManualOverride"))) denyAutomation("Manual override blocks automatic changes");
lock = context.getSystemService("keyguard");
if (lock != null && lock.isKeyguardLocked()) denyAutomation("Automatic change deferred until the phone is unlocked");
if (!"0".equals(tasker.getVariable("SIG3_DeferAutomation"))) {
    service = tasker.getAccessibilityService();
    root = service == null ? null : service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        denyAutomation("Automatic change deferred until Signia is foreground");
}
return "allowed";
