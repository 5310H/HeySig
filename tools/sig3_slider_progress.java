/* Direct numeric slider action: no simulated touch and no automatic touch fallback. */
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityManager;
import android.accessibilityservice.AccessibilityServiceInfo;
import android.os.Bundle;
import android.graphics.Rect;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
service = tasker.getAccessibilityService();
if (service == null) throw new JavaCodeException("Enable Tasker accessibility");
serviceInfo = service.getServiceInfo();
if (serviceInfo == null) throw new JavaCodeException("Tasker accessibility service information unavailable");
serviceInfo.flags = serviceInfo.flags | AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
service.setServiceInfo(serviceInfo);
root = service.getRootInActiveWindow();
if (root == null || root.getPackageName() == null || !"com.signia.rta".contentEquals(root.getPackageName()))
    throw new JavaCodeException("Signia is not foreground");
family = tasker.getVariable("SIG3_Family");
id = tasker.getVariable("SIG3_" + family + "ControlId");
if (id == null) throw new JavaCodeException("Configure the slider control ID");
// Save a read-only tree capture even when the configured selector fails.
inspect = "Inspect".equals(tasker.getVariable("sig3_slider_mode"));
matches = root.findAccessibilityNodeInfosByViewId(id);
lookupCount = matches.size();
visibleCount = 0;
enabledCount = 0;
node = null;
for (candidate : matches) {
    if (candidate.isVisibleToUser()) visibleCount++;
    if (candidate.isEnabled()) enabledCount++;
    if (!candidate.isVisibleToUser() || !candidate.isEnabled()) continue;
    if (node == null) node = candidate;
    else throw new JavaCodeException("Slider ID is ambiguous");
}
lookupDiagnostic = "family=" + family + "; requestedId=" + id + "; matches=" + lookupCount
    + "; visible=" + visibleCount + "; enabled=" + enabledCount
    + "; serviceFlags=" + serviceInfo.flags;
if (inspect || node == null) {
    queue = new java.util.ArrayList();
    queue.add(root);
    capture = lookupDiagnostic;
    treeMatches = 0;
    treeEligible = 0;
    for (scan = 0; scan < queue.size() && scan < 300; scan++) {
        item = (AccessibilityNodeInfo) queue.get(scan);
        itemId = item.getViewIdResourceName();
        itemRange = item.getRangeInfo();
        if (id.equals(itemId)) {
            treeMatches++;
            if (lookupCount == 0 && item.isVisibleToUser() && item.isEnabled()) {
                treeEligible++;
                if (treeEligible == 1) node = item;
            }
        }
        if (itemRange != null || (itemId != null && itemId.toLowerCase().contains("slider"))) {
            itemRect = new Rect(); item.getBoundsInScreen(itemRect);
            capture = capture + "\n" + itemId + " | " + item.getClassName()
                + " | visible=" + item.isVisibleToUser() + " enabled=" + item.isEnabled()
                + " | " + itemRect;
            if (itemRange != null) capture = capture + " | min=" + itemRange.getMin()
                + " max=" + itemRange.getMax() + " current=" + itemRange.getCurrent();
        }
        for (childIndex = 0; childIndex < item.getChildCount() && queue.size() < 300; childIndex++) {
            child = item.getChild(childIndex);
            if (child != null) queue.add(child);
        }
    }
    lookupDiagnostic = lookupDiagnostic + "; treeMatches=" + treeMatches;
    tasker.setVariable("SIG3_QueryData", capture + "\ntreeMatches=" + treeMatches);
    if (treeEligible > 1) throw new JavaCodeException("Slider ID is ambiguous in screen tree: " + id);
    if (lookupCount == 0 && node != null) lookupDiagnostic = lookupDiagnostic + "; lookup=exact-tree-id";
}
tasker.setVariable("SIG3_SliderDiagnostics", lookupDiagnostic);
if (node == null) throw new JavaCodeException("Slider lookup failed: " + lookupDiagnostic + "; see SIG3_QueryData");
manager = context.getSystemService("accessibility");
range = node.getRangeInfo();
actions = "";
canSet = false;
for (entry : node.getActionList()) {
    actions = actions + entry.getId() + ":" + entry.getLabel() + ";";
    if (entry.getId() == AccessibilityNodeInfo.AccessibilityAction.ACTION_SET_PROGRESS.getId()) canSet = true;
}
rect = new Rect(); node.getBoundsInScreen(rect);
diagnostic = "family=" + family + "; id=" + node.getViewIdResourceName() + "; class=" + node.getClassName()
    + "; matches=" + lookupCount + "; visible=" + node.isVisibleToUser()
    + "; enabled=" + node.isEnabled() + "; bounds=" + rect + "; accessibility=" + manager.isEnabled()
    + "; touchExploration=" + manager.isTouchExplorationEnabled() + "; actions=" + actions;
if (range != null) diagnostic = diagnostic + "; rangeType=" + range.getType() + "; min=" + range.getMin() + "; max=" + range.getMax() + "; current=" + range.getCurrent();
tasker.setVariable("SIG3_SliderDiagnostics", diagnostic);
tasker.log(diagnostic);
if ("Inspect".equals(tasker.getVariable("sig3_slider_mode"))) {
    tasker.setVariable("SIG3_Observed", diagnostic);
    return "inspected";
}
// The range alone cannot prove the displayed-level mapping. Require explicit confirmation.
if (!"1".equals(tasker.getVariable("SIG3_" + family + "RangeConfirmed")))
    throw new JavaCodeException("Inspect slider and confirm displayed/native mapping; set SIG3_" + family + "RangeConfirmed=1 only after checking");
if (!canSet || range == null) throw new JavaCodeException("Slider does not expose ACTION_SET_PROGRESS and RangeInfo");
if (!manager.isEnabled() || !manager.isTouchExplorationEnabled())
    throw new JavaCodeException("Signia's accessibility commit requires touch exploration; no action sent. See SIG3_SliderDiagnostics");
low = "Balance".equals(family) ? -8.0 : 0.0;
high = "Balance".equals(family) ? 7.0 : 15.0;
minimum = (double) range.getMin(); maximum = (double) range.getMax();
if (Double.isNaN(minimum) || Double.isNaN(maximum) || Double.isInfinite(minimum) || Double.isInfinite(maximum) || maximum <= minimum)
    throw new JavaCodeException("Invalid native slider range");
target = Double.parseDouble(tasker.getVariable("SIG3_Target"));
if (target < low || target > high || target != Math.rint(target)) throw new JavaCodeException("Invalid displayed target");
// Confirmed ascending linear domain: native endpoints correspond to displayed endpoints.
nativeTarget = minimum + (target - low) * (maximum - minimum) / (high - low);
bundle = new Bundle();
bundle.putFloat(AccessibilityNodeInfo.ACTION_ARGUMENT_PROGRESS_VALUE, (float) nativeTarget);
tasker.setVariable("SIG3_MoveStage", "set-progress");
tasker.setVariable("SIG3_ProgressAccepted", "0");
accepted = node.performAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SET_PROGRESS.getId(), bundle);
tasker.setVariable("SIG3_ProgressAccepted", accepted ? "1" : "0");
tasker.setVariable("SIG3_SliderDiagnostics", diagnostic + "; displayedTarget=" + target + "; nativeTarget=" + nativeTarget + "; accepted=" + accepted);
if (!accepted) throw new JavaCodeException("ACTION_SET_PROGRESS rejected; no touch fallback");
return "accepted; verify displayed target and audible aid response separately";
