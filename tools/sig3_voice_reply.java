/* Speak only a fresh completed voice result, using actual app readback. */
voiceValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
tasker.setVariable("sig3_speech", "");
tasker.setVariable("SIG3_VoiceReply", "");
retry = "retry".equals(voiceValue("sig3_reply_kind"));
preference = voiceValue(retry ? "SIG3_VoicePrompts" : "SIG3_VoiceResponses");
if (retry && preference.length() == 0) preference = voiceValue("SIG3_VoiceResponses");
if ("0".equals(preference)) return "disabled";
running = voiceValue("TRUN");
if (running.matches("(?s).*(?:^|,)SIG3_Worker(?:,|$).*")) return "worker-busy";
if ("retry".equals(voiceValue("sig3_reply_kind"))) {
    reply = "Command not recognized. Tap Try again to speak again, or Cancel.";
} else {
    operation = voiceValue("SIG3_OperationId");
    if (operation.length() == 0 || operation.equals(voiceValue("sig3_reply_before"))) {
        reply = "Command was not accepted. Please try again when the current command finishes.";
    } else if (!"1".equals(voiceValue("SIG3_CommandOK"))) {
        error = voiceValue("SIG3_Error");
        reply = error.length() == 0 ? "Command did not complete. Check the phone screen." : "Command stopped. " + error;
        if (error.startsWith("Turn off Do Not Disturb")) reply = "Turn off Do Not Disturb.";
        if (error.startsWith("Raise phone ")) {
            end = error.indexOf(" volume");
            if (end > 12) {
                stream = error.substring(12, end);
                reply = "Raise phone " + stream + " volume" + (error.contains("(50% minimum)") ? " to halfway." : ".");
            }
        }
    } else if (!"complete".equals(voiceValue("SIG3_MoveStage"))) {
        reply = "Command result could not be verified. Check the phone screen.";
    } else {
        family = voiceValue("SIG3_Family");
        observed = voiceValue("SIG3_Observed");
        program = voiceValue("SIG3_Program");
        reply = "Command completed. Check the phone screen.";
        if ("Program".equals(family) && program.length() > 0) reply = "Program is " + program + ".";
        if ("Volume".equals(family) || "Balance".equals(family) || "Tinnitus".equals(family)) {
            if (observed.matches("-?[0-9]+")) {
                spoken = observed.startsWith("-") ? "minus " + observed.substring(1) : observed;
                reply = family + " is " + spoken + ".";
            }
        }
        if ("Battery".equals(family)) reply = "Battery checks requested. Listen for the hearing aid indications.";
        if (("Noise".equals(family) || "Setup".equals(family) || "Sleep".equals(family) || "Settings".equals(family)) && observed.length() > 0)
            reply = observed + ".";
        if (voiceValue("SIG3_SettingsAutoError").length() > 0) reply += " Settings were not saved. " + voiceValue("SIG3_SettingsAutoError");
    }
}
tasker.setVariable("SIG3_VoiceReply", reply);
tasker.setVariable("sig3_speech", reply);
return "ready";
