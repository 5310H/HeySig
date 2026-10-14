/* Persist selectable times and program mappings together; Cancel never calls save. */
import org.json.JSONObject;
import org.json.JSONArray;
sleepValue(key) {
    value = tasker.getVariable(key);
    return value == null || value.startsWith("%") ? "" : value;
}
sleepPrograms() {
    names = new JSONArray();
    for (i = 1; i <= 6; i++) {
        name = sleepValue("SIG3_ProgramName" + i).trim();
        if (name.length() == 0) throw new Exception("Configure all six program names");
        for (j = 0; j < names.length(); j++)
            if (name.equals(names.getString(j))) throw new Exception("Program names must be unique");
        names.put(name);
    }
    return names;
}
sleepTimeValid(value) { return value.matches("(?:[01][0-9]|2[0-3])\\.[0-5][0-9]"); }
prefs = context.getSharedPreferences("heysig3-sleep", 0);
mode = sleepValue("sig3_sleep_pref_mode");
if ("save".equals(mode)) {
    sleepSlot = sleepValue("sig3_sleep_program_choice"); wakeSlot = sleepValue("sig3_wake_program_choice");
    sleepTime = sleepValue("sig3_sleep_time_choice"); wakeTime = sleepValue("sig3_wake_time_choice");
    if (!sleepSlot.matches("[1-6]") || !wakeSlot.matches("[1-6]")) throw new Exception("Choose both programs");
    if (!sleepTimeValid(sleepTime) || !sleepTimeValid(wakeTime) || sleepTime.equals(wakeTime))
        throw new Exception("Choose two different valid clock times");
    config = new JSONObject(); config.put("version", 1); config.put("programs", sleepPrograms());
    config.put("sleepSlot", sleepSlot); config.put("wakeSlot", wakeSlot);
    config.put("sleepTime", sleepTime); config.put("wakeTime", wakeTime);
    if (!prefs.edit().putString("configuration", config.toString()).commit())
        throw new Exception("Could not save sleep settings; previous settings retained");
} else if ("load".equals(mode)) {
    saved = prefs.getString("configuration", "");
    if (saved.length() == 0) { tasker.setVariable("SIG3_SleepSettingsStatus", "Choose sleep and wake programs and times"); return "unconfigured"; }
    config = new JSONObject(saved);
    if (config.getInt("version") != 1 || !config.getJSONArray("programs").toString().equals(sleepPrograms().toString())) {
        tasker.setVariable("SIG3_SleepEnabled", "0");
        tasker.setVariable("SIG3_SleepProgram", ""); tasker.setVariable("SIG3_WakeProgram", "");
        tasker.setVariable("SIG3_SleepSettingsStatus", "Program mapping changed; choose sleep programs again");
        return "mapping-changed";
    }
    sleepSlot = config.getString("sleepSlot"); wakeSlot = config.getString("wakeSlot");
    sleepTime = config.getString("sleepTime"); wakeTime = config.getString("wakeTime");
    if (!sleepSlot.matches("[1-6]") || !wakeSlot.matches("[1-6]") || !sleepTimeValid(sleepTime)
        || !sleepTimeValid(wakeTime) || sleepTime.equals(wakeTime)) throw new Exception("Invalid saved sleep settings");
} else throw new Exception("Unknown sleep settings operation");
// Time contexts reevaluate immediately when their variables change.
if ("save".equals(mode)) tasker.setVariable("SIG3_SleepEnabled", "0");
tasker.setVariable("SIG3_SleepProgram", sleepSlot); tasker.setVariable("SIG3_WakeProgram", wakeSlot);
tasker.setVariable("SIG3_SleepTime", sleepTime); tasker.setVariable("SIG3_WakeTime", wakeTime);
tasker.setVariable("SIG3_SleepSettingsStatus", "Sleep " + sleepTime.replace('.', ':') + ": " + config.getJSONArray("programs").getString(Integer.parseInt(sleepSlot)-1)
    + "; wake " + wakeTime.replace('.', ':') + ": " + config.getJSONArray("programs").getString(Integer.parseInt(wakeSlot)-1));
return "sleep settings " + mode;
