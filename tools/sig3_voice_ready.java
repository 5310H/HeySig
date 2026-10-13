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
    tasker.setVariable("SIG3_VoiceStatus", status); tasker.showToast(status);
    if (status.equals("Turn on and unlock the phone to speak a command")) {
        audio = context.getSystemService("audio"); notification = context.getSystemService("notification");
        preference = readyValue("SIG3_VoicePrompts");
        if (preference.length() == 0) preference = readyValue("SIG3_VoiceResponses");
        if (!"0".equals(preference)
            && notification.getCurrentInterruptionFilter() == NotificationManager.INTERRUPTION_FILTER_ALL
            && !audio.isStreamMute(AudioManager.STREAM_MUSIC)
            && audio.getStreamVolume(AudioManager.STREAM_MUSIC) > 0
            && audio.getMode() == AudioManager.MODE_NORMAL)
            tasker.setVariable("sig3_ready_speech", "Unlock the phone, then say Hey Sig again.");
    }
    return "capture blocked";
}
tasker.setVariable("SIG3_VoiceCaptureAllowed", "1");
tasker.setVariable("SIG3_VoiceStatus", "Opening command prompt");
tasker.showToast("Sig here");
am = context.getSystemService("audio"); nm = context.getSystemService("notification");
prompts = readyValue("SIG3_VoicePrompts");
if (prompts.length() == 0) prompts = readyValue("SIG3_VoiceResponses");
// AutoVoice Media suppression can release mute after its stop action returns.
// Wait only for an enabled wake handoff; never change the user's volume.
if (!"0".equals(prompts) && "1".equals(readyValue("SIG3_WakeEnabled"))
    && nm.getCurrentInterruptionFilter() == NotificationManager.INTERRUPTION_FILTER_ALL
    && am.getMode() == AudioManager.MODE_NORMAL) {
    for (settle = 0; settle < 20; settle++) {
        if (!am.isStreamMute(AudioManager.STREAM_MUSIC)
            && am.getStreamVolume(AudioManager.STREAM_MUSIC) > 0) break;
        Thread.sleep(100);
    }
}
if (!"0".equals(prompts) && nm.getCurrentInterruptionFilter() == NotificationManager.INTERRUPTION_FILTER_ALL && !am.isStreamMute(AudioManager.STREAM_MUSIC) && am.getStreamVolume(AudioManager.STREAM_MUSIC) > 0 && am.getMode() == AudioManager.MODE_NORMAL)
    tasker.setVariable("sig3_ready_speech", "Sig here");
return "cue prepared";
