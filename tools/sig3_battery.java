/* Opens battery UI and records visible information; never invents acoustic percentages. */
import android.view.accessibility.AccessibilityNodeInfo;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.os.SystemClock;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
visibleTree(service) {
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        throw new JavaCodeException("Signia is not foreground");
    queue = new java.util.ArrayList(); queue.add(root);
    visible = new java.util.ArrayList();
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        if (node.isVisibleToUser() && node.isEnabled()) visible.add(node);
        for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
            child = node.getChild(childIndex); if (child != null) queue.add(child);
        }
    }
    return visible;
}
matching(nodes, id, description) {
    found = new java.util.ArrayList();
    for (node : nodes) {
        if (id != null && id.equals(node.getViewIdResourceName())) found.add(node);
    }
    if (found.size() == 0 && description != null && description.length() > 0 && !description.startsWith("%")) {
        for (node : nodes) if (node.getContentDescription() != null && description.contentEquals(node.getContentDescription())) found.add(node);
    }
    return found;
}
try {
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
info = service.getServiceInfo();
if (info == null) throw new JavaCodeException("Tasker accessibility information unavailable");
info.flags = info.flags | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS; service.setServiceInfo(info);
mode = tasker.getVariable("par1");
if (!"open".equals(mode) && !"listen".equals(mode)) throw new JavaCodeException("Battery mode must be open or listen");
pageId = tasker.getVariable("SIG3_BatteryPageId");
if (pageId == null || pageId.length() == 0 || pageId.startsWith("%")) throw new JavaCodeException("Configure SIG3_BatteryPageId");
if (pickerProgram(service.getRootInActiveWindow()).length() > 0) prepareProgramRead(service);
nodes = visibleTree(service);
page = matching(nodes, pageId, null);
if (page.size() > 1) throw new JavaCodeException("Battery page marker is ambiguous");
if (page.size() == 0) {
    open = matching(nodes, tasker.getVariable("SIG3_BatteryOpenId"), tasker.getVariable("SIG3_BatteryOpenDescription"));
    if (open.size() != 1) throw new JavaCodeException("Battery opener missing/ambiguous; configure its captured ID or description");
    found = (AccessibilityNodeInfo) open.get(0); clicked = false;
    for (depth = 0; found != null && depth < 5; depth++) {
        if (found.isClickable()) {
            if (!found.performAction(AccessibilityNodeInfo.ACTION_CLICK)) throw new JavaCodeException("Battery click rejected");
            clicked = true; break;
        }
        found = found.getParent();
    }
    if (!clicked) throw new JavaCodeException("Battery opener has no clickable ancestor");
    for (attempt = 0; attempt < 20; attempt++) {
        SystemClock.sleep(150);
        nodes = visibleTree(service); page = matching(nodes, pageId, null);
        if (page.size() > 1) throw new JavaCodeException("Battery page marker is ambiguous");
        if (page.size() == 1) break;
    }
    if (page.size() != 1) throw new JavaCodeException("Battery page marker missing; configure SIG3_BatteryPageId");
}
text = "";
for (node : nodes) if (node.getText() != null) text = text + node.getText() + "\n";
tasker.setVariable("SIG3_BatteryText", text);
tasker.setVariable("SIG3_Observed", "Battery page opened; visible text recorded. No aid battery percentage inferred.");
return "opened";
} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString()); throw failure;
}
