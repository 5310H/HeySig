/* Read-only tinnitus availability: read the active program icon before any tab search. */
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
    programIcon = "";
    tasker.setVariable("SIG3_ProgramIcon", "");
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        description = node.getContentDescription();
        if (node.isVisibleToUser() && node.isEnabled() && description != null
            && description.toString().startsWith("Hearing program ")
            && description.toString().endsWith(" Active")) {
            headerNodes = new java.util.ArrayList(); headerNodes.add(node);
            for (h = 0; h < headerNodes.size() && h < 30; h++) {
                headerNode = (AccessibilityNodeInfo) headerNodes.get(h);
                iconText = headerNode.getText();
                if (headerNode.isVisibleToUser() && iconText != null
                    && ("\uE912".contentEquals(iconText) || "\uE909".contentEquals(iconText)))
                    {
                        programIcon = iconText.toString();
                        tasker.setVariable("SIG3_ProgramIcon", programIcon);
                        if ("\uE909".equals(programIcon)) {
                            tasker.setVariable("SIG3_Error", "Tinnitus unavailable for this program");
                            return "unavailable";
                        }
                        tasker.setVariable("SIG3_TinnitusAvailable", "1");
                        return "available";
                    }
                for (hc = 0; hc < headerNode.getChildCount() && headerNodes.size() < 30; hc++) {
                    headerChild = headerNode.getChild(hc);
                    if (headerChild != null) headerNodes.add(headerChild);
                }
            }
        }
        for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
            child = node.getChild(childIndex);
            if (child != null) queue.add(child);
        }
    }
    tasker.setVariable("SIG3_ProgramIcon", programIcon);
    // Only an unknown icon needs a fallback search for the actual tinnitus tab.
    queue = new java.util.ArrayList(); queue.add(root); tabs = 0;
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
