/* Program selection through visible accessibility nodes, never fixed coordinates. */
import android.view.accessibility.AccessibilityNodeInfo;
import android.accessibilityservice.AccessibilityServiceInfo;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
import android.os.SystemClock;
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


performStroke(service, stroke, phase) {
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
    gesture = new GestureDescription.Builder().addStroke(stroke).build();
    if (!service.dispatchGesture(gesture, callback, new Handler(Looper.getMainLooper())))
        throw new JavaCodeException(phase + ": dispatchGesture rejected");
    if (!signal.await(3, TimeUnit.SECONDS))
        throw new JavaCodeException(phase + ": completion timed out after 3000 ms");
    if (!result.get().equals("completed"))
        throw new JavaCodeException(phase + ": Android cancelled gesture");
}

visibleNodes(root, id) {
    result = new java.util.ArrayList();
    queue = new java.util.ArrayList(); queue.add(root);
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        node = (AccessibilityNodeInfo) queue.get(scan);
        if (node.isVisibleToUser() && node.isEnabled() && id != null && id.equals(node.getViewIdResourceName())) result.add(node);
        for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
            child = node.getChild(childIndex); if (child != null) queue.add(child);
        }
    }
    return result;
}
clickNode(service, node, backend) {
    if ("gesture-tap".equals(backend)) {
        if (Build.VERSION.SDK_INT < 24) throw new JavaCodeException("Program tap requires Android 7 or later");
        rect = new android.graphics.Rect(); node.getBoundsInScreen(rect);
        metrics = service.getResources().getDisplayMetrics();
        x = rect.centerX(); y = rect.centerY();
        if (rect.isEmpty() || x < 0 || y < 0 || x >= metrics.widthPixels || y >= metrics.heightPixels)
            throw new JavaCodeException("Program button bounds are outside the display");
        tasker.setVariable("SIG3_Gesture", "Program button tap at " + x + "," + y + "; bounds=" + rect);
        path = new Path(); path.moveTo(x, y);
        performStroke(service, new GestureDescription.StrokeDescription(path, 0, 100, false), "program-tap");
        return;
    }
    if (!"accessibility-click".equals(backend)) throw new JavaCodeException("Set SIG3_ProgramBackend to accessibility-click or gesture-tap");
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
    if (id == null || id.trim().length() == 0 || id.startsWith("%")) throw new JavaCodeException("Configure SIG3_ProgramId");
    root = service.getRootInActiveWindow();
    if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Signia is not foreground");
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
    return program;
}
try {
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
info = service.getServiceInfo();
if (info == null) throw new JavaCodeException("Tasker accessibility information unavailable");
info.flags = info.flags | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
service.setServiceInfo(info);
backend = tasker.getVariable("SIG3_ProgramBackend");
if (backend == null || backend.length() == 0 || backend.startsWith("%")) backend = "accessibility-click";
requested = tasker.getVariable("par1");
if (requested == null || !requested.matches("[1-6]")) throw new JavaCodeException("Program slot must be 1–6");
target = tasker.getVariable("SIG3_ProgramName" + requested);
if (target == null || target.trim().length() == 0 || target.startsWith("%")) throw new JavaCodeException("Configure SIG3_ProgramName" + requested + " from the actual program list");
target = target.trim();
id = tasker.getVariable("SIG3_ProgramId");
prepareProgramRead(service);
previous = readProgram(service, id);
tasker.setVariable("SIG3_Previous", previous);
tasker.setVariable("SIG3_Expected", target);
if (!previous.equals(target)) {
    root = service.getRootInActiveWindow();
    open = visibleNodes(root, tasker.getVariable("SIG3_ProgramOpenId"));
    if (open.size() != 1) throw new JavaCodeException("Program opener missing/ambiguous; configure SIG3_ProgramOpenId");
    clickNode(service, open.get(0), backend);
    selected = false;
    for (int attempt = 0; attempt < 20 && !selected; attempt++) {
        SystemClock.sleep(150);
        root = service.getRootInActiveWindow();
        if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName())) throw new JavaCodeException("Program chooser not in Signia");
        candidates = new java.util.ArrayList();
        queue = new java.util.ArrayList(); queue.add(root);
        for (scan = 0; scan < queue.size() && scan < 300; scan++) {
            item = (AccessibilityNodeInfo) queue.get(scan); candidates.add(item);
            for (childIndex = 0; childIndex < item.getChildCount() && queue.size() < 300; childIndex++) {
                child = item.getChild(childIndex); if (child != null) queue.add(child);
            }
        }
        exact = new java.util.ArrayList();
        for (node : candidates) if (node.isVisibleToUser() && node.isEnabled() && node.getText() != null && target.equals(node.getText().toString().trim())) exact.add(node);
        if (exact.size() > 1) throw new JavaCodeException("Program name matches multiple visible items");
        if (exact.size() == 1) { clickNode(service, exact.get(0), backend); selected = true; }
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

} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
