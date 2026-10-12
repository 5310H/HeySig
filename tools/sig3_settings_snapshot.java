/* Persistent user-triggered snapshot. Charging/reconnect never overwrites this file. */
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import com.joaomgcd.taskerm.action.java.JavaCodeException;
settingsValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
settingsPrograms() {
    names = new JSONArray(); seen = new java.util.HashSet();
    for (slot = 1; slot <= 6; slot++) {
        name = settingsValue("SIG3_ProgramName" + slot).trim();
        if (name.length() > 0 && !seen.add(name)) throw new JavaCodeException("Ambiguous configured program names");
        names.put(name);
    }
    return names;
}
settingsSlot(names, program) {
    found = 0;
    for (slot = 0; slot < names.length(); slot++) if (program.equals(names.getString(slot))) found = slot + 1;
    if (found == 0) throw new JavaCodeException("Saved program is not configured");
    return found;
}
settingsLevel(text, family) {
    if (!text.matches("-?[0-9]+")) throw new JavaCodeException("Invalid saved " + family + " level");
    level = Integer.parseInt(text);
    minimum = "Balance".equals(family) ? -8 : 0;
    maximum = "Balance".equals(family) ? 7 : 15;
    if (level < minimum || level > maximum) throw new JavaCodeException("Saved " + family + " level outside range");
    return level;
}
settingsSavedLevel(controls, family) {
    value = controls.get(family);
    if (!(value instanceof Number)) throw new JavaCodeException("Invalid saved " + family + " type");
    return settingsLevel(value.toString(), family);
}
try {
    mode = settingsValue("sig3_settings_mode");
    file = new File(context.getFilesDir(), "heysig3-settings-v1.json");
    if ("begin-save".equals(mode)) {
        program = settingsValue("SIG3_Program");
        if (program.length() == 0) throw new JavaCodeException("Cannot save an unknown program");
        names = settingsPrograms(); settingsSlot(names, program);
        snapshot = new JSONObject(); snapshot.put("version", 1); snapshot.put("project", "HeySig3");
        snapshot.put("savedAt", System.currentTimeMillis()); snapshot.put("program", program);
        snapshot.put("programs", names); snapshot.put("controls", new JSONObject());
        tasker.setVariable("SIG3_SettingsDraft", snapshot.toString());
        tasker.setVariable("SIG3_SettingsExpectedProgram", program);
        return "capture started";
    }
    if ("capture".equals(mode) || "commit".equals(mode)) {
        snapshot = new JSONObject(settingsValue("SIG3_SettingsDraft"));
        if (!snapshot.getString("program").equals(settingsValue("SIG3_Program")))
            throw new JavaCodeException("Program changed while saving settings");
        if (!snapshot.getJSONArray("programs").toString().equals(settingsPrograms().toString()))
            throw new JavaCodeException("Program configuration changed while saving settings");
        controls = snapshot.getJSONObject("controls");
        if ("capture".equals(mode)) {
            family = settingsValue("sig3_settings_control");
            if ("Tinnitus".equals(family) && !"1".equals(settingsValue("SIG3_TinnitusAvailable"))) controls.put(family, JSONObject.NULL);
            else {
                if (!"Volume".equals(family) && !"Balance".equals(family) && !"Tinnitus".equals(family)) throw new JavaCodeException("Unknown saved control");
                key = "Volume".equals(family) ? "SIG3_Level" : "SIG3_" + family + "Level";
                controls.put(family, settingsLevel(settingsValue(key), family));
            }
            tasker.setVariable("SIG3_SettingsDraft", snapshot.toString()); return "captured " + family;
        }
        settingsSavedLevel(controls, "Volume"); settingsSavedLevel(controls, "Balance");
        if (!controls.has("Tinnitus")) throw new JavaCodeException("Incomplete settings snapshot");
        if (!controls.isNull("Tinnitus")) settingsSavedLevel(controls, "Tinnitus");
        temporary = new File(context.getFilesDir(), "heysig3-settings-v1.json.pending");
        output = new FileOutputStream(temporary);
        try { output.write(snapshot.toString().getBytes("UTF-8")); output.getFD().sync(); } finally { output.close(); }
        if (!temporary.renameTo(file)) throw new JavaCodeException("Could not replace saved settings; previous snapshot retained");
        tasker.setVariable("SIG3_SettingsSavedAt", Long.toString(snapshot.getLong("savedAt")));
        tasker.setVariable("SIG3_SettingsDraft", "");
        tasker.setVariable("SIG3_Observed", "Settings saved for " + snapshot.getString("program") + (controls.isNull("Tinnitus") ? "; tinnitus unavailable and omitted" : ""));
        tasker.setVariable("SIG3_SettingsOK", "1"); return "saved";
    }
    if ("load".equals(mode)) {
        if (!file.isFile()) throw new JavaCodeException("No saved settings; run Save settings first");
        if (file.length() < 1 || file.length() > 65536) throw new JavaCodeException("Invalid saved settings file size");
        input = new FileInputStream(file); bytes = new byte[(int) file.length()]; offset = 0;
        try { while (offset < bytes.length) { length = input.read(bytes, offset, bytes.length - offset); if (length < 1) break; offset += length; } } finally { input.close(); }
        if (offset != bytes.length) throw new JavaCodeException("Incomplete saved settings file");
        snapshot = new JSONObject(new String(bytes, "UTF-8"));
        if (!(snapshot.get("version") instanceof Number) || !"1".equals(snapshot.get("version").toString()) || !"HeySig3".equals(snapshot.getString("project")) || !(snapshot.get("savedAt") instanceof Number) || !snapshot.get("savedAt").toString().matches("[0-9]+") || snapshot.getLong("savedAt") <= 0)
            throw new JavaCodeException("Unsupported or invalid settings snapshot");
        names = settingsPrograms();
        if (!names.toString().equals(snapshot.getJSONArray("programs").toString())) throw new JavaCodeException("Program mapping changed since Save settings; snapshot retained");
        program = snapshot.getString("program"); slot = settingsSlot(names, program); controls = snapshot.getJSONObject("controls");
        volume = settingsSavedLevel(controls, "Volume"); balance = settingsSavedLevel(controls, "Balance");
        if (!controls.has("Tinnitus")) throw new JavaCodeException("Incomplete settings snapshot");
        tinnitus = controls.isNull("Tinnitus") ? "" : Integer.toString(settingsSavedLevel(controls, "Tinnitus"));
        tasker.setVariable("SIG3_SettingsSnapshot", snapshot.toString());
        tasker.setVariable("SIG3_SettingsExpectedProgram", program);
        tasker.setVariable("SIG3_SettingsProgram", program); tasker.setVariable("SIG3_SettingsSlot", Integer.toString(slot));
        tasker.setVariable("SIG3_SettingsVolume", Integer.toString(volume)); tasker.setVariable("SIG3_SettingsBalance", Integer.toString(balance));
        tasker.setVariable("SIG3_SettingsTinnitus", tinnitus); tasker.setVariable("SIG3_SettingsSavedAt", Long.toString(snapshot.getLong("savedAt")));
        return "validated before restore";
    }
    if ("verify-program".equals(mode) || "verify-control".equals(mode) || "finish-restore".equals(mode)) {
        snapshot = new JSONObject(settingsValue("SIG3_SettingsSnapshot"));
        if (!snapshot.getString("program").equals(settingsValue("SIG3_Program"))) throw new JavaCodeException("Program changed during restore");
        if (!snapshot.getJSONArray("programs").toString().equals(settingsPrograms().toString())) throw new JavaCodeException("Program mapping changed during restore");
        if ("verify-program".equals(mode)) return "saved program verified";
        controls = snapshot.getJSONObject("controls");
        if ("verify-control".equals(mode)) {
            family = settingsValue("sig3_settings_control");
            key = "Volume".equals(family) ? "SIG3_Level" : "SIG3_" + family + "Level";
            if (controls.isNull(family) || settingsLevel(settingsValue(key), family) != settingsSavedLevel(controls, family))
                throw new JavaCodeException(family + " restoration readback did not match saved settings");
            return "verified " + family;
        }
        if (!controls.isNull("Tinnitus") && !"1".equals(settingsValue("SIG3_TinnitusAvailable"))) {
            tasker.setVariable("SIG3_Error", "Partial restore: program, volume and balance restored; saved tinnitus unavailable and skipped; snapshot retained");
            tasker.setVariable("SIG3_SettingsOK", "0"); return "partial restoration";
        }
        tasker.setVariable("SIG3_Observed", "Settings restored for " + snapshot.getString("program") + (controls.isNull("Tinnitus") ? "; tinnitus was not saved and skipped" : ""));
        tasker.setVariable("SIG3_SettingsOK", "1"); return "restored";
    }
    throw new JavaCodeException("Unknown settings snapshot operation");
} catch (Exception failure) {
    tasker.setVariable("SIG3_Error", failure.toString()); tasker.setVariable("SIG3_SettingsOK", "0"); throw failure;
}
