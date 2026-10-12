/* Preserve the media level across AutoVoice continuous mute cycles. */
import android.media.AudioManager;
wakeAudioValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
am = context.getSystemService("audio");
mode = wakeAudioValue("sig3_wake_audio_mode");
if ("capture".equals(mode)) {
    tasker.setVariable("SIG3_WakeMediaLevel", "" + am.getStreamVolume(AudioManager.STREAM_MUSIC));
    return "media captured";
}
if (!"restore".equals(mode)) throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Unknown wake audio operation");
saved = wakeAudioValue("SIG3_WakeMediaLevel");
if (!saved.matches("[0-9]+")) return "no captured media level";
level = Integer.parseInt(saved);
if (level > am.getStreamMaxVolume(AudioManager.STREAM_MUSIC))
    throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Captured media level is outside the phone range");
// Allow the stopped plugin to finish releasing its suppression before restoration.
Thread.sleep(500);
if (am.getStreamVolume(AudioManager.STREAM_MUSIC) != level)
    am.setStreamVolume(AudioManager.STREAM_MUSIC, level, 0);
if (level > 0 && am.isStreamMute(AudioManager.STREAM_MUSIC))
    am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_UNMUTE, 0);
if (am.getStreamVolume(AudioManager.STREAM_MUSIC) != level)
    throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Phone media volume did not restore");
return "media restored";
