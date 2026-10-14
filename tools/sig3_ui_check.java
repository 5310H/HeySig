/* Read-only live UI guard. Defaults are APK-derived and must be confirmed on the phone. */
import android.graphics.Rect;
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
    throw new JavaCodeException("Signia is not the active accessibility window");
family = tasker.getVariable("SIG3_Family");
controlId = tasker.getVariable("SIG3_" + family + "ControlId");
programId = tasker.getVariable("SIG3_ProgramId");
if (controlId == null || programId == null)
    throw new JavaCodeException("Configure the common control ID and current program ID");
// Walk the actual tree: this phone returns no matches from direct ID lookup.
queue = new java.util.ArrayList(); queue.add(root);
visible = 0; count = 0; program = null; control = null; headerCount = 0; headerProgram = null;
for (scan = 0; scan < queue.size() && scan < 300; scan++) {
    node = (AccessibilityNodeInfo) queue.get(scan);
    nodeId = node.getViewIdResourceName();
    description = node.getContentDescription();
    if (node.isVisibleToUser() && description != null) {
        header = description.toString();
        if (header.startsWith("Hearing program ") && header.endsWith(" Active")) {
            name = header.substring("Hearing program ".length(), header.length() - " Active".length()).trim();
            if (name.length() > 0) { headerProgram = name; headerCount++; }
        }
    }
    if (controlId.equals(nodeId) && node.isVisibleToUser() && node.isEnabled()) { visible++; control = node; }
    if (programId.equals(nodeId) && node.isVisibleToUser()) {
        value = node.getText();
        if (value == null || value.toString().trim().length() == 0) value = node.getContentDescription();
        if (value != null && value.toString().trim().length() > 0) {
            program = value.toString().trim(); count++;
        }
    }
    for (childIndex = 0; childIndex < node.getChildCount() && queue.size() < 300; childIndex++) {
        child = node.getChild(childIndex);
        if (child != null) queue.add(child);
    }
}
if (visible == 0 && "Tinnitus".equals(family)) throw new JavaCodeException("Tinnitus unavailable for this program");
if (visible != 1) throw new JavaCodeException("Expected exactly one enabled " + family + " common control: " + controlId);
// Signia changes the label ID with the program (Universal, TV, etc.).
// The actual visible accessibility header is stable across those programs.
if (count == 0 && headerCount == 1) { program = headerProgram; count = 1; }
if (count != 1 || headerCount > 1) throw new JavaCodeException("Cannot identify current program unambiguously");
if (headerCount == 1 && !headerProgram.equals(program)) throw new JavaCodeException("Program label and active header disagree");
savedProgram = tasker.getVariable("SIG3_SettingsExpectedProgram");
if (savedProgram != null && savedProgram.length() > 0 && !savedProgram.startsWith("%") && !savedProgram.equals(program))
    throw new JavaCodeException("Program changed during settings operation; saved program=" + savedProgram + "; current=" + program);
baseline = tasker.getVariable("SIG3_Program");
if (baseline != null && !baseline.equals(program))
    throw new JavaCodeException("Program changed during operation: " + baseline + " -> " + program);
tasker.setVariable("SIG3_Program", program);
tasker.setVariable("SIG3_UIControl", controlId);
// The numeric label's accessibility bounds extend to the bottom of the track.
// Position the gesture from native progress and explicitly calibrated track endpoints.
topText = tasker.getVariable("SIG3_" + family + "TrackTopY");
bottomText = tasker.getVariable("SIG3_" + family + "TrackBottomY");
if (topText != null && bottomText != null) {
    rect = new Rect(); control.getBoundsInScreen(rect);
    expectedBounds = tasker.getVariable("SIG3_" + family + "TrackBounds");
    actualBounds = rect.left + "," + rect.top + "," + rect.right + "," + rect.bottom;
    if (!actualBounds.equals(expectedBounds)) throw new JavaCodeException("Slider bounds changed; recalibrate track endpoints");
    top = Float.parseFloat(topText); bottom = Float.parseFloat(bottomText);
    range = control.getRangeInfo();
    if (range == null || range.getMax() <= range.getMin() || top < rect.top || bottom > rect.bottom || bottom <= top)
        throw new JavaCodeException("Invalid slider position calibration");
    thumbTopText = tasker.getVariable("SIG3_" + family + "ThumbTopY");
    thumbBottomText = tasker.getVariable("SIG3_" + family + "ThumbBottomY");
    thumbTopSet = thumbTopText != null && thumbTopText.length() > 0 && !thumbTopText.startsWith("%");
    thumbBottomSet = thumbBottomText != null && thumbBottomText.length() > 0 && !thumbBottomText.startsWith("%");
    if (thumbTopSet != thumbBottomSet) throw new JavaCodeException("Configure both slider thumb endpoints");
    if (thumbTopSet) {
        top = Float.parseFloat(thumbTopText); bottom = Float.parseFloat(thumbBottomText);
        if (Float.isNaN(top) || Float.isInfinite(top) || Float.isNaN(bottom) || Float.isInfinite(bottom)
            || top < rect.top || bottom > rect.bottom || bottom <= top)
            throw new JavaCodeException("Invalid slider thumb calibration");
    }
    fraction = (range.getCurrent() - range.getMin()) / (range.getMax() - range.getMin());
    if (Float.isNaN(fraction) || fraction < 0 || fraction > 1) throw new JavaCodeException("Invalid current native progress");
    tasker.setVariable("SIG3_" + family + "X", "" + rect.centerX());
    tasker.setVariable("SIG3_" + family + "Y", "" + Math.round(bottom - fraction * (bottom - top)));
}
return "verified";

} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
