/* Read-only current program query; no program picker clicks or acoustic command. */
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
import android.os.SystemClock;
visibleNodes(root, id) {
    nodes = root.findAccessibilityNodeInfosByViewId(id);
    result = new java.util.ArrayList();
    for (node : nodes) if (node.isVisibleToUser() && node.isEnabled()) result.add(node);
    return result;
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
id = tasker.getVariable("SIG3_ProgramId");
if (id == null || id.trim().length() == 0) throw new JavaCodeException("Configure SIG3_ProgramId");
observed = readProgram(service, id);
tasker.setVariable("SIG3_Program", observed);
tasker.setVariable("SIG3_Observed", observed);
return "displayed";
