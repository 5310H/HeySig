/* Program selection through visible accessibility nodes, never fixed coordinates. */
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
import android.os.SystemClock;
visibleNodes(root, id) {
    nodes = root.findAccessibilityNodeInfosByViewId(id);
    result = new java.util.ArrayList();
    for (node : nodes) if (node.isVisibleToUser() && node.isEnabled()) result.add(node);
    return result;
}
clickNode(node) {
    for (int depth = 0; depth < 5 && node != null; depth++) {
        if (node.isClickable()) {
            if (!node.performAction(AccessibilityNodeInfo.ACTION_CLICK)) throw new JavaCodeException("Accessibility click rejected");
            return;
        }
        node = node.getParent();
    }
    throw new JavaCodeException("No clickable ancestor for selected node");
}
readProgram(service, id) {
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Signia is not foreground");
    nodes = visibleNodes(root, id);
    if (nodes.size() != 1) throw new JavaCodeException("Current program is ambiguous; configure SIG3_ProgramId");
    value = nodes.get(0).getText();
    if (value == null || value.toString().trim().length() == 0) throw new JavaCodeException("Current program has no readable text");
    return value.toString().trim();
}
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
requested = tasker.getVariable("par1");
if (requested == null || !requested.matches("[1-6]")) throw new JavaCodeException("Program slot must be 1–6");
target = tasker.getVariable("SIG3_ProgramName" + requested);
if (target == null || target.trim().length() == 0) throw new JavaCodeException("Configure SIG3_ProgramName" + requested + " from the actual program list");
id = tasker.getVariable("SIG3_ProgramId");
previous = readProgram(service, id);
tasker.setVariable("SIG3_Previous", previous);
tasker.setVariable("SIG3_Expected", target);
if (!previous.equals(target)) {
    root = service.getRootInActiveWindow();
    open = visibleNodes(root, tasker.getVariable("SIG3_ProgramOpenId"));
    if (open.size() != 1) throw new JavaCodeException("Program opener missing/ambiguous; configure SIG3_ProgramOpenId");
    clickNode(open.get(0));
    selected = false;
    for (int attempt = 0; attempt < 20 && !selected; attempt++) {
        SystemClock.sleep(150);
        root = service.getRootInActiveWindow();
        if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Program chooser not in Signia");
        candidates = root.findAccessibilityNodeInfosByText(target);
        exact = new java.util.ArrayList();
        for (node : candidates) if (node.isVisibleToUser() && node.isEnabled() && node.getText() != null && target.equals(node.getText().toString().trim())) exact.add(node);
        if (exact.size() > 1) throw new JavaCodeException("Program name matches multiple visible items");
        if (exact.size() == 1) { clickNode(exact.get(0)); selected = true; }
    }
    if (!selected) throw new JavaCodeException("Configured program not found");
}
for (int attempt = 0; attempt < 20; attempt++) {
    SystemClock.sleep(150);
    try {
        observed = readProgram(service, id);
        tasker.setVariable("SIG3_Observed", observed);
        if (target.equals(observed)) {
            tasker.setVariable("SIG3_Program", observed);
            return "displayed";
        }
    } catch (JavaCodeException unavailable) { }
}
throw new JavaCodeException("Program did not become the configured target; inspect Signia before retrying");
