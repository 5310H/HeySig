/* Optional completion navigation; preserve another app's window. */
import android.accessibilityservice.AccessibilityService;
policy = tasker.getVariable("SIG3_CompletionPolicy");
if (policy == null || policy.equals("stay")) return "stayed";
if (!policy.equals("home")) return "unknown policy; stayed";
service = tasker.getAccessibilityService();
root = service == null ? null : service.getRootInActiveWindow();
if (root != null && root.getPackageName() != null && "com.signia.rta".contentEquals(root.getPackageName())) {
    if (!service.performGlobalAction(AccessibilityService.GLOBAL_ACTION_HOME)) tasker.log("Home navigation rejected");
}
return "completion navigation checked";
