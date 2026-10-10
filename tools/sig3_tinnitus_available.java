/* Read-only tinnitus availability: inspect the actual tab, not a program-name allowlist. */
import android.accessibilityservice.AccessibilityServiceInfo;
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
tasker.setVariable("SIG3_TinnitusAvailable", "0");
try {
    service = tasker.getAccessibilityService();
    if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        throw new JavaCodeException("Signia is not foreground");
    queue = new java.util.ArrayList(); queue.add(root);
    tabs = 0;
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        description = node.getContentDescription();
        if (node.isVisibleToUser() && node.isEnabled() && description != null
            && ("Tinnitus Signal Tab".contentEquals(description) || "Selected Tinnitus Signal Tab".contentEquals(description))) tabs++;
        for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
            child = node.getChild(childIndex);
            if (child != null) queue.add(child);
        }
    }
    if (tabs == 1) {
        tasker.setVariable("SIG3_TinnitusAvailable", "1");
        return "available";
    }
    tasker.setVariable("SIG3_Error", "Tinnitus unavailable for this program");
    return "unavailable";
} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
