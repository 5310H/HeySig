/* Concrete command reporting: unset Tasker tokens are not user-facing values. */
cleanValue(name) {
    value = tasker.getVariable(name);
    if (value == null || value.startsWith("%")) return "";
    return value;
}
family = cleanValue("SIG3_Family");
observed = cleanValue("SIG3_Observed");
program = cleanValue("SIG3_Program");
target = cleanValue("SIG3_Target");
if ("1".equals(cleanValue("SIG3_CommandOK"))) {
    result = family + ": " + observed;
    if (program.length() > 0) result += "; program=" + program;
    if (target.length() > 0) result += "; target=" + target;
    result += " (app state; aid receipt unverified)";
    warning = cleanValue("SIG3_SettingsAutoError");
    if (warning.length() > 0) result += "; settings not saved: " + warning;
} else {
    error = cleanValue("SIG3_Error");
    if (error.length() == 0) error = "Operation did not complete";
    tasker.setVariable("SIG3_Error", error);
    result = "Failed: " + error;
    for (name : new String[] {"SIG3_Family", "SIG3_Target", "SIG3_Previous", "SIG3_Expected", "SIG3_Observed", "SIG3_Program", "SIG3_MoveStage"}) {
        value = cleanValue(name);
        if (value.length() > 0) result += "; " + name.substring(5) + "=" + value;
    }
}
tasker.setVariable("SIG3_Result", result);
tasker.log(result + "; " + cleanValue("SIG3_AudioDiagnostics"));
tasker.showToast(result);
return "reported";
