import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
try {
    family = tasker.getVariable("SIG3_Family");
    tabDescription = "Balance".equals(family) ? "Sound Sharpness Tab"
        : "Tinnitus".equals(family) ? "Tinnitus Signal Tab" : "Volume Tab";
    service = tasker.getAccessibilityService();
    // Read the actual selected tab after the coordinate click.
    for (attempt = 0; attempt < 30; attempt++) {
        java.lang.Thread.sleep(100);
        root = service.getRootInActiveWindow();
        if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
            throw new JavaCodeException("Signia left foreground during tab selection");
        queue = new java.util.ArrayList(); queue.add(root); selectedCount = 0;
        for (scan = 0; scan < queue.size() && scan < 300; scan++) {
            node = (AccessibilityNodeInfo) queue.get(scan);
            description = node.getContentDescription();
            if (node.isVisibleToUser() && node.isEnabled() && description != null
                && ("Selected " + tabDescription).contentEquals(description)) selectedCount++;
            for (i = 0; i < node.getChildCount() && queue.size() < 300; i++) {
                child = node.getChild(i); if (child != null) queue.add(child);
            }
        }
        if (selectedCount == 1) return "tab selection verified; slider readback follows";
        if (selectedCount > 1) throw new JavaCodeException("Selected tab is ambiguous");
    }
    throw new JavaCodeException(family + " tab tap completed without verified selection");
 } catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
