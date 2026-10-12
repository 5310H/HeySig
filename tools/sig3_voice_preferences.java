/* Load or atomically save independent speech preferences. */
voicePreferenceValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
voicePreferenceValid(value) { return "0".equals(value) || "1".equals(value); }
prefs = context.getSharedPreferences("heysig3-voice", 0);
mode = voicePreferenceValue("sig3_voice_pref_mode");
if ("save".equals(mode)) {
    responses = voicePreferenceValue("sig3_voice_results_choice");
    prompts = voicePreferenceValue("sig3_voice_prompts_choice");
    if (!voicePreferenceValid(responses) || !voicePreferenceValid(prompts))
        throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Invalid voice preference selection");
    if (!prefs.edit().putString("responses", responses).putString("prompts", prompts).commit())
        throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Voice preferences could not be saved");
} else if ("load".equals(mode)) {
    responses = voicePreferenceValue("SIG3_VoiceResponses");
    if (!voicePreferenceValid(responses)) responses = prefs.getString("responses", "1");
    if (!voicePreferenceValid(responses)) responses = "1";
    prompts = voicePreferenceValue("SIG3_VoicePrompts");
    if (!voicePreferenceValid(prompts)) prompts = prefs.getString("prompts", responses);
    if (!voicePreferenceValid(prompts)) prompts = responses;
} else throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Unknown voice preference operation");
tasker.setVariable("SIG3_VoiceResponses", responses);
tasker.setVariable("SIG3_VoicePrompts", prompts);
tasker.setVariable("SIG3_VoiceSettingsStatus", "Spoken results " + ("1".equals(responses) ? "on" : "off") + "; voice prompts " + ("1".equals(prompts) ? "on" : "off"));
return "voice preferences " + mode;
