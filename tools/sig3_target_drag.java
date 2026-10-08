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

if (Build.VERSION.SDK_INT < 26)
    throw new JavaCodeException("Continuous touch requires Android 8 or later");
service = tasker.getAccessibilityService();
if (service == null)
    throw new JavaCodeException("Enable Tasker in Android Settings > Accessibility > Installed apps");
x = Float.parseFloat(tasker.getVariable("sig3_x"));
y = Float.parseFloat(tasker.getVariable("sig3_y"));
endY = Float.parseFloat(tasker.getVariable("sig3_end_y"));
if (x < 0 || endY < 0 || Math.abs(y - endY) < 1 || Math.abs(y - endY) > 200)
    throw new JavaCodeException("Invalid calibrated step coordinates");
metrics = service.getResources().getDisplayMetrics();
if (x >= metrics.widthPixels || y < 0 || y >= metrics.heightPixels || endY >= metrics.heightPixels)
    throw new JavaCodeException("Gesture coordinates outside display bounds");
holdPath = new Path();
holdPath.moveTo(x, y);
/* willContinue=true keeps this pointer DOWN after the stationary 200 ms. */
holdStroke = new GestureDescription.StrokeDescription(holdPath, 0, 200, true);
movePath = new Path();
movePath.moveTo(x, y);
movePath.lineTo(x, endY);
/* Continue the SAME pointer; false releases it at the end of the 300 ms MOVE. */
moveStroke = holdStroke.continueStroke(movePath, 0, 300, false);
held = false;
try {
    held = true;
    performStroke(service, holdStroke, "down-hold");
    performStroke(service, moveStroke, "move");
    held = false;
    tasker.setVariable("SIG3_TouchStage", "released");
} finally {
    if (held) {
        /* Best-effort release of a held pointer after rejection/timeout/error. */
        try {
            releaseStroke = holdStroke.continueStroke(holdPath, 0, 1, false);
            service.dispatchGesture(new GestureDescription.Builder().addStroke(releaseStroke).build(), null, null);
        } catch (Exception releaseError) {
            tasker.log("SIG3 held-pointer cleanup: " + releaseError.toString());
        }
    }
}
return "completed";
