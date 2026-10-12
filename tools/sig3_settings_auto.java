/* Update the last verified settings without rereading unchanged controls. */
import org.json.JSONObject;
import java.io.File;
import java.io.FileInputStream;
autoValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
keys = new String[] {"Family","CommandOK","Error","Result","MoveStage","TouchStage","Gesture","QueryData","Program","Previous","Expected","Observed","AudioDiagnostics","Target","SliderDiagnostics","ProgressAccepted","OperationId"};
mode = autoValue("sig3_settings_auto_mode");
if ("finish".equals(mode)) {
    warning = "1".equals(autoValue("SIG3_SettingsOK")) ? "" : autoValue("SIG3_Error");
    if (warning.length() == 0 && !"1".equals(autoValue("SIG3_SettingsOK"))) warning = "Settings snapshot did not complete";
    state = new JSONObject(autoValue("SIG3_SettingsCommandState"));
    for (key : keys) tasker.setVariable("SIG3_" + key, state.getString(key));
    tasker.setVariable("SIG3_SettingsAutoError", warning);
    tasker.setVariable("SIG3_SettingsCommandState", "");
    tasker.setVariable("SIG3_SettingsExpectedProgram", "");
    return "command result restored";
}
tasker.setVariable("SIG3_SettingsAutoMode", "");
family = autoValue("SIG3_Family"); operation = autoValue("sig3_request2");
slider = "Volume".equals(family) || "Balance".equals(family) || "Tinnitus".equals(family);
changed = slider && operation.matches("Set|Up|Down|Max|Mute|Sharp|Soft") && autoValue("SIG3_Previous").matches("-?[0-9]+") && autoValue("SIG3_Observed").matches("-?[0-9]+") && !autoValue("SIG3_Previous").equals(autoValue("SIG3_Observed"));
changed = changed || ("Program".equals(family) && "Switch".equals(operation) && autoValue("SIG3_Previous").length() > 0 && !autoValue("SIG3_Previous").equals(autoValue("SIG3_Program")));
if (!"1".equals(autoValue("SIG3_CommandOK")) || !changed) return "no settings change";
state = new JSONObject(); for (key : keys) state.put(key, autoValue("SIG3_" + key));
tasker.setVariable("SIG3_SettingsCommandState", state.toString());
tasker.setVariable("SIG3_SettingsOK", "0");
tasker.setVariable("SIG3_SettingsAutoMode", "full");
/* A new program or missing baseline needs one complete read. A known program
   uses the previously verified controls and replaces only the changed value. */
if (slider) {
    try {
        file = new File(context.getFilesDir(), "heysig3-settings-v1.json");
        if (!file.isFile() || file.length() < 1 || file.length() > 65536) return "full baseline needed";
        input = new FileInputStream(file); bytes = new byte[(int)file.length()]; offset = 0;
        try { while(offset < bytes.length) { count=input.read(bytes,offset,bytes.length-offset); if(count < 1) break; offset+=count; } } finally { input.close(); }
        if(offset != bytes.length) return "full baseline needed";
        snapshot = new JSONObject(new String(bytes,"UTF-8"));
        names = new org.json.JSONArray(); for(slot=1;slot<=6;slot++) names.put(autoValue("SIG3_ProgramName"+slot).trim());
        if (!"1".equals(snapshot.get("version").toString()) || !"HeySig3".equals(snapshot.getString("project")) || !autoValue("SIG3_Program").equals(snapshot.getString("program")) || !names.toString().equals(snapshot.getJSONArray("programs").toString())) return "full baseline needed";
        controls=snapshot.getJSONObject("controls");
        if (!controls.has("Volume") || !controls.has("Balance") || !controls.has("Tinnitus")) return "full baseline needed";
        controls.put(family, Integer.parseInt(autoValue("SIG3_Observed")));
        snapshot.put("savedAt",System.currentTimeMillis());
        tasker.setVariable("SIG3_SettingsDraft",snapshot.toString());
        tasker.setVariable("SIG3_SettingsAutoMode","update");
    } catch(Exception ignored) { return "full baseline needed"; }
}
return "automatic save prepared";
