/* Read-only preflight: no volume, route, DND or lock settings are changed. */
import android.app.KeyguardManager;
import android.app.NotificationManager;
import android.media.AudioManager;
import android.media.AudioDeviceInfo;
import android.os.PowerManager;
import android.os.Build;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
try {
pm = context.getSystemService("power");
km = context.getSystemService("keyguard");
if (!pm.isInteractive() || km.isKeyguardLocked())
    throw new JavaCodeException("Turn on and unlock the phone before controlling Signia");
am = context.getSystemService("audio");
nm = context.getSystemService("notification");
streamName = tasker.getVariable("SIG3_AudioStream");
if (!"media".equals(streamName) && !"ring".equals(streamName))
    throw new JavaCodeException("Set SIG3_AudioStream to Signia's selected media or ring stream");
stream = "ring".equals(streamName) ? AudioManager.STREAM_RING : AudioManager.STREAM_MUSIC;
volume = am.getStreamVolume(stream);
maximum = am.getStreamMaxVolume(stream);
mode = am.getMode();
ringer = am.getRingerMode();
minimumText = tasker.getVariable("SIG3_MinAudioPercent");
minimumPercent = 50;
if (minimumText != null && !minimumText.equals("") && !minimumText.startsWith("%")) {
    if (!minimumText.matches("[0-9]{1,3}"))
        throw new JavaCodeException("Set SIG3_MinAudioPercent to an integer from 1 to 100");
    minimumPercent = Integer.parseInt(minimumText);
}
if (minimumPercent < 1 || minimumPercent > 100)
    throw new JavaCodeException("Set SIG3_MinAudioPercent to an integer from 1 to 100");
required = (maximum * minimumPercent + 99) / 100;
filter = nm.getCurrentInterruptionFilter();
outputs = am.getDevices(AudioManager.GET_DEVICES_OUTPUTS);
route = "";
external = false;
for (device : outputs) {
    type = device.getType();
    route = route + type + ":" + device.getProductName() + ";";
    /* Known connected external outputs; presence is conservative, not an active-route claim. */
    if (type == 3 || type == 4 || type == 7 || type == 8 || type == 11 || type == 12 || type == 22 || type == 23 || type == 26 || type == 27)
        external = true;
}
tasker.setVariable("SIG3_AudioDiagnostics", "stream=" + streamName + " volume=" + volume + "/" + maximum + "; minimum=" + required + "/" + maximum + "; ringerMode=" + ringer + "; mode=" + mode + "; interruptionFilter=" + filter + "; outputs=" + route);
/* BEGIN AUDIO POLICY: also exercised without Android by the policy test. */
if (filter != NotificationManager.INTERRUPTION_FILTER_ALL)
    throw new JavaCodeException("Turn off Do Not Disturb (including bedtime/night mode), then retry the Signia command");
if (ringer == AudioManager.RINGER_MODE_SILENT || ("ring".equals(streamName) && ringer != AudioManager.RINGER_MODE_NORMAL))
    throw new JavaCodeException("Unmute the phone; for Ring sound, also turn off vibrate-only mode, then retry");
if (maximum <= 0 || volume < required)
    throw new JavaCodeException("Raise phone " + streamName + " volume with the phone volume slider to at least " + required + "/" + maximum + " (" + minimumPercent + "% minimum), then retry");
/* END AUDIO POLICY */
if (mode == AudioManager.MODE_IN_CALL || mode == AudioManager.MODE_IN_COMMUNICATION)
    throw new JavaCodeException("Phone call or communication audio is active");
if (external) throw new JavaCodeException("Disconnect external audio outputs before acoustic control");
return "ready";

} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString());
    throw failure;
}
