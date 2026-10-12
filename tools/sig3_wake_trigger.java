/* Accept only the wake phrase while our listener is enabled and idle. */
wakeValue(name) {
    value = tasker.getVariable(name);
    return value == null || value.startsWith("%") ? "" : value;
}
tasker.setVariable("sig3_wake_accepted", "0");
if (!"1".equals(wakeValue("SIG3_WakeEnabled")) || "1".equals(wakeValue("SIG3_VoiceBusy"))) return "disabled-or-busy";
if (wakeValue("TRUN").matches("(?s).*(?:^|,)SIG3_Worker(?:,|$).*")) return "worker-busy";
heard = wakeValue("par1");
if (heard.length() == 0) heard = wakeValue("avcommnofilter");
if (heard.length() == 0) heard = wakeValue("avcomm");
if (!heard.trim().matches("(?i)^hey\\s+sig[.!?]?$")) return "not-wake-phrase";
tasker.setVariable("sig3_wake_accepted", "1");
return "wake-accepted";
