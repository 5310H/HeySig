/* Tasker 6.6.20 Java Code (BeanShell). No root, ADB or helper app. */
import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicReference;
import com.joaomgcd.taskerm.action.java.ClassImplementation;
import com.joaomgcd.taskerm.action.java.JavaCodeException;

/* Wait for Android's actual completion/cancellation, not merely acceptance. */
performTabDoubleTap(service, stroke, stroke2, phase) {
    signal = new CountDownLatch(1);
    result = new AtomicReference("timeout");
    callback = tasker.implementClass(AccessibilityService.GestureResultCallback.class,
        new ClassImplementation() {
            run(Callable superCaller, String methodName, Object[] args) {
                if (methodName.equals("onCompleted")) {
                    result.set("completed");
                    signal.countDown();
                    return null;
                }
                if (methodName.equals("onCancelled")) {
                    result.set("cancelled");
                    signal.countDown();
                    return null;
                }
                return superCaller.call();
            }
        });
    tasker.setVariable("SIG3_TouchStage", phase);
    gesture = new GestureDescription.Builder().addStroke(stroke).addStroke(stroke2).build();
    if (!service.dispatchGesture(gesture, callback, new Handler(Looper.getMainLooper())))
        throw new JavaCodeException(phase + ": dispatchGesture rejected");
    if (!signal.await(3, TimeUnit.SECONDS))
        throw new JavaCodeException(phase + ": completion timed out after 3000 ms");
    if (!result.get().equals("completed"))
        throw new JavaCodeException(phase + ": Android cancelled gesture");
}

/* Resolve live tab bounds and activate with a double tap. */
/* Select the actual requested tab before querying its numeric label. */
import android.view.accessibility.AccessibilityNodeInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
try {
    family = tasker.getVariable("SIG3_Family");
    if (!"Volume".equals(family) && !"Balance".equals(family) && !"Tinnitus".equals(family))
        throw new JavaCodeException("Unknown slider family");
    tabDescription = "Balance".equals(family) ? "Sound Sharpness Tab"
        : "Tinnitus".equals(family) ? "Tinnitus Signal Tab" : "Volume Tab";
    service = tasker.getAccessibilityService();
    root = service == null ? null : service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        throw new JavaCodeException("Signia is not foreground");
    queue = new java.util.ArrayList(); queue.add(root);
    tab = null; count = 0; selected = false;
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        description = node.getContentDescription();
        if (node.isVisibleToUser() && node.isEnabled() && description != null
            && (tabDescription.contentEquals(description) || ("Selected " + tabDescription).contentEquals(description))) {
            tab = node; count++; selected = ("Selected " + tabDescription).contentEquals(description);
        }
        for (i = 0; i < node.getChildCount() && queue.size() < 300; i++) {
            child = node.getChild(i); if (child != null) queue.add(child);
        }
    }
    if (count != 1) throw new JavaCodeException("Expected exactly one enabled " + family + " tab");
    tasker.setVariable("sig3_tab_selected", selected ? "1" : "0");
    if (selected) return "already selected";
    if (Build.VERSION.SDK_INT < 24) throw new JavaCodeException("Tab double tap requires Android 7 or later");
    // A program header can change before Signia accepts tab touches.
    // Re-read the tab after settling so a changed layout cannot leave stale X/Y.
    java.lang.Thread.sleep(3000);
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
        throw new JavaCodeException("Signia is not foreground");
    queue = new java.util.ArrayList(); queue.add(root);
    tab = null; count = 0; selected = false;
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        description = node.getContentDescription();
        if (node.isVisibleToUser() && node.isEnabled() && description != null
            && (tabDescription.contentEquals(description) || ("Selected " + tabDescription).contentEquals(description))) {
            tab = node; count++; selected = ("Selected " + tabDescription).contentEquals(description);
        }
        for (i = 0; i < node.getChildCount() && queue.size() < 300; i++) {
            child = node.getChild(i); if (child != null) queue.add(child);
        }
    }
    if (count != 1) throw new JavaCodeException("Expected exactly one enabled " + family + " tab");
    if (selected) return "selected while settling";
    rect = new android.graphics.Rect(); tab.getBoundsInScreen(rect);
    metrics = service.getResources().getDisplayMetrics();
    x = rect.centerX(); y = rect.centerY();
    if (rect.isEmpty() || rect.left < 0 || rect.top < 0
        || rect.right > metrics.widthPixels || rect.bottom > metrics.heightPixels)
        throw new JavaCodeException("Tab bounds are outside the display");
    // Prefer the visible label inside the resolved tab, away from icon/layout gaps.
    labelNodes = new java.util.ArrayList(); labelNodes.add(tab); labelCount = 0;
    for (labelScan = 0; labelScan < labelNodes.size() && labelScan < 30; labelScan++) {
        labelNode = (AccessibilityNodeInfo) labelNodes.get(labelScan);
        labelText = labelNode.getText();
        if (labelNode.isVisibleToUser() && labelNode.isEnabled() && labelText != null
            && family.contentEquals(labelText)) {
            labelRect = new android.graphics.Rect(); labelNode.getBoundsInScreen(labelRect);
            if (!labelRect.isEmpty() && labelRect.left >= rect.left && labelRect.top >= rect.top
                && labelRect.right <= rect.right && labelRect.bottom <= rect.bottom) {
                labelCount++; labelX = labelRect.centerX(); labelY = labelRect.centerY();
            }
        }
        for (labelChildIndex = 0; labelChildIndex < labelNode.getChildCount() && labelNodes.size() < 30; labelChildIndex++) {
            labelChild = labelNode.getChild(labelChildIndex);
            if (labelChild != null) labelNodes.add(labelChild);
        }
    }
    if (labelCount > 1) throw new JavaCodeException("Ambiguous tab label");
    if (labelCount == 1) { x = labelX; y = labelY; }
    tasker.setVariable("sig3_tab_x", "" + x);
    tasker.setVariable("sig3_tab_y", "" + y);
    tasker.setVariable("SIG3_Gesture", family + " tab double tap at " + x + "," + y + "; bounds=" + rect);
    path = new Path(); path.moveTo(x, y);
    performTabDoubleTap(service, new GestureDescription.StrokeDescription(path, 0, 50),
        new GestureDescription.StrokeDescription(path, 150, 50), "tab-double-tap");
    tasker.setVariable("SIG3_TouchStage", "released");
    return "tab double tap completed; selection verification follows";
} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
