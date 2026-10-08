/* Opens battery UI and records visible information; never invents acoustic percentages. */
import android.view.accessibility.AccessibilityNodeInfo;
import android.os.SystemClock;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
clickId(service, id) {
    if (id == null || id.trim().length() == 0) throw new JavaCodeException("Configure the battery button ID from a phone capture");
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Signia is not foreground");
    found = null;
    for (node : root.findAccessibilityNodeInfosByViewId(id)) {
        if (!node.isVisibleToUser() || !node.isEnabled()) continue;
        if (found != null) throw new JavaCodeException("Battery button is ambiguous");
        found = node;
    }
    for (int depth = 0; found != null && depth < 5; depth++) {
        if (found.isClickable()) {
            if (!found.performAction(AccessibilityNodeInfo.ACTION_CLICK)) throw new JavaCodeException("Battery click rejected");
            return;
        }
        found = found.getParent();
    }
    throw new JavaCodeException("Battery button is unavailable or not clickable");
}
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
mode = tasker.getVariable("par1");
if (!"open".equals(mode) && !"listen".equals(mode)) throw new JavaCodeException("Battery mode must be open or listen");
root = service.getRootInActiveWindow();
pageId = tasker.getVariable("SIG3_BatteryPageId");
alreadyOpen = false;
if (root != null && root.getPackageName() != null && "com.signia.rta".contentEquals(root.getPackageName()) && pageId != null) {
    count = 0;
    for (node : root.findAccessibilityNodeInfosByViewId(pageId)) if (node.isVisibleToUser()) count++;
    alreadyOpen = count == 1;
}
if (!alreadyOpen) {
    clickId(service, tasker.getVariable("SIG3_BatteryOpenId"));
    SystemClock.sleep(500);
}
root = service.getRootInActiveWindow();
if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Battery page not available");
pageId = tasker.getVariable("SIG3_BatteryPageId");
visible = 0;
for (node : root.findAccessibilityNodeInfosByViewId(pageId)) if (node.isVisibleToUser()) visible++;
if (visible != 1) throw new JavaCodeException("Battery page marker missing; configure SIG3_BatteryPageId");
text = "";
for (node : service.getChildrenRecursive(root)) {
    if (node.isVisibleToUser() && node.getText() != null) text = text + node.getText() + "\n";
}
tasker.setVariable("SIG3_BatteryText", text);
if ("listen".equals(mode)) {
    clickId(service, tasker.getVariable("SIG3_BatteryRequestId"));
    tasker.setVariable("SIG3_Observed", "Battery request clicked; listen for the aid indication. Receipt is unverified.");
} else tasker.setVariable("SIG3_Observed", "Battery page opened; visible text recorded. No aid battery percentage inferred.");
return "opened";
