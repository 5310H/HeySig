/* Prepare the readiness cue before opening microphone capture. */
import android.content.pm.PackageManager;
import android.app.NotificationManager;
import android.media.AudioManager;
readyValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
tasker.setVariable("sig3_ready_speech", "");
tasker.setVariable("SIG3_VoiceReady", "0");
tasker.setVariable("SIG3_VoiceCaptureAllowed", "0");
status = "";
pm = context.getSystemService("power"); km = context.getSystemService("keyguard");
if (!pm.isInteractive() || km.isKeyguardLocked()) status = "Turn on and unlock the phone to speak a command";
else if (context.checkSelfPermission("android.permission.RECORD_AUDIO") != PackageManager.PERMISSION_GRANTED) status = "Allow Tasker microphone access to speak a command";
else if (readyValue("TRUN").matches("(?s).*(?:^|,)SIG3_Worker(?:,|$).*")) status = "Wait for the current command to finish";
if (status.length() > 0) {
    tasker.setVariable("SIG3_VoiceStatus", status); tasker.showToast(status); return "capture blocked";
}
tasker.setVariable("SIG3_VoiceCaptureAllowed", "1");
tasker.setVariable("SIG3_VoiceStatus", "Opening command prompt");
tasker.showToast("Sig here");
am = context.getSystemService("audio"); nm = context.getSystemService("notification");
if (!"0".equals(readyValue("SIG3_VoiceResponses")) && nm.getCurrentInterruptionFilter() == NotificationManager.INTERRUPTION_FILTER_ALL && am.getStreamVolume(AudioManager.STREAM_MUSIC) > 0 && am.getMode() == AudioManager.MODE_NORMAL)
    tasker.setVariable("sig3_ready_speech", "Sig here");
return "cue prepared";
