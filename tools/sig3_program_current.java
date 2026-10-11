/* Read-only current program query; no picker click or acoustic command. */
import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
try {
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
info = service.getServiceInfo();
if (info == null) throw new JavaCodeException("Tasker accessibility information unavailable");
info.flags = info.flags | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
service.setServiceInfo(info);
root = service.getRootInActiveWindow();
if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
    throw new JavaCodeException("Signia is not foreground");
id = tasker.getVariable("SIG3_ProgramId");
if (id == null || id.trim().length() == 0) throw new JavaCodeException("Configure SIG3_ProgramId");
queue = new java.util.ArrayList(); queue.add(root);
count = 0; program = null; headerCount = 0; headerProgram = null;
for (scan = 0; scan < queue.size() && scan < 300; scan++) {
    node = (AccessibilityNodeInfo) queue.get(scan);
    if (node.isVisibleToUser() && node.isEnabled()) {
        description = node.getContentDescription();
        if (description != null) {
            header = description.toString();
            if (header.startsWith("Hearing program ") && header.endsWith(" Active")) {
                name = header.substring("Hearing program ".length(), header.length() - " Active".length()).trim();
                if (name.length() > 0) { headerProgram = name; headerCount++; }
            }
        }
        if (id.equals(node.getViewIdResourceName())) {
            value = node.getText();
            if (value != null && value.toString().trim().length() > 0) {
                program = value.toString().trim(); count++;
            }
        }
    }
    for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
        child = node.getChild(childIndex);
        if (child != null) queue.add(child);
    }
}
if (count == 0 && headerCount == 1) { program = headerProgram; count = 1; }
if (count != 1 || headerCount > 1) throw new JavaCodeException("Cannot identify current program unambiguously");
if (headerCount == 1 && !headerProgram.equals(program)) throw new JavaCodeException("Program label and active header disagree");
tasker.setVariable("SIG3_Program", program);
tasker.setVariable("SIG3_Observed", program);
return "displayed";
} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
