/* Automatic changes must not take over another app by default. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
if ("1".equals(tasker.getVariable("SIG3_AutomationCancelled"))) throw new JavaCodeException("Automatic change cancelled");
if ("1".equals(tasker.getVariable("SIG3_ManualOverride"))) throw new JavaCodeException("Manual override blocks automatic changes");
if (!"0".equals(tasker.getVariable("SIG3_DeferAutomation"))) {
    service = tasker.getAccessibilityService();
    root = service == null ? null : service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        throw new JavaCodeException("Automatic change deferred until Signia is foreground");
}
return "allowed";
