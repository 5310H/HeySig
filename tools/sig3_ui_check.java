/* Read-only live UI guard. Defaults are APK-derived and must be confirmed on the phone. */
import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
root = service.getRootInActiveWindow();
if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
    throw new JavaCodeException("Signia is not the active accessibility window");
family = tasker.getVariable("SIG3_Family");
controlId = tasker.getVariable("SIG3_" + family + "ControlId");
programId = tasker.getVariable("SIG3_ProgramId");
if (controlId == null || programId == null)
    throw new JavaCodeException("Configure the common control ID and current program ID");
controls = root.findAccessibilityNodeInfosByViewId(controlId);
visible = 0;
for (node : controls) {
    if (node.isVisibleToUser() && node.isEnabled()) visible++;
}
if (visible != 1) throw new JavaCodeException("Expected exactly one enabled " + family + " common control: " + controlId);
programNodes = root.findAccessibilityNodeInfosByViewId(programId);
program = null;
count = 0;
for (node : programNodes) {
    if (!node.isVisibleToUser()) continue;
    value = node.getText();
    if (value == null || value.toString().trim().length() == 0) value = node.getContentDescription();
    if (value != null && value.toString().trim().length() > 0) {
        program = value.toString().trim();
        count++;
    }
}
if (count != 1) throw new JavaCodeException("Cannot identify current program; configure SIG3_ProgramId from a UI capture");
baseline = tasker.getVariable("SIG3_Program");
if (baseline != null && !baseline.equals(program))
    throw new JavaCodeException("Program changed during operation: " + baseline + " -> " + program);
tasker.setVariable("SIG3_Program", program);
tasker.setVariable("SIG3_UIControl", controlId);
return "verified";
