/* Read-only preflight: no volume, route, DND or lock settings are changed. */
import android.app.KeyguardManager;
import android.app.NotificationManager;
import android.media.AudioManager;
import android.media.AudioDeviceInfo;
import android.os.PowerManager;
import android.os.Build;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
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
tasker.setVariable("SIG3_AudioDiagnostics", "stream=" + streamName + " volume=" + volume + "/" + maximum + "; mode=" + mode + "; interruptionFilter=" + filter + "; outputs=" + route);
if (volume == 0) throw new JavaCodeException("Selected phone audio stream is muted");
if (mode == AudioManager.MODE_IN_CALL || mode == AudioManager.MODE_IN_COMMUNICATION)
    throw new JavaCodeException("Phone call or communication audio is active");
if (external) throw new JavaCodeException("Disconnect external audio outputs before acoustic control");
if ("ring".equals(streamName) && (am.getRingerMode() != AudioManager.RINGER_MODE_NORMAL || filter != NotificationManager.INTERRUPTION_FILTER_ALL))
    throw new JavaCodeException("Ringtone acoustic control is blocked by silent/DND state");
/* Media DND and Signia's configurable volume thresholds are recorded, not guessed. */
return "ready";
