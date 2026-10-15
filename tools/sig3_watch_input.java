/* Accept AutoWear's namespaced command envelope, preserving the spoken payload. */
input = tasker.getVariable("sig3_input");
tasker.setVariable("SIG3_WatchRawInput", input == null ? "" : input);
for (name : new String[] {"awcomm", "awmessage", "awcommnofilter"}) {
    value = tasker.getVariable(name);
    tasker.setVariable("SIG3_WatchEvent_" + name, value == null ? "" : value);
}
if (input == null || input.startsWith("%") || input.trim().length() == 0)
    throw new com.joaomgcd.taskerm.action.java.JavaCodeException("No command text supplied by watch event");
input = input.trim().replaceFirst("(?i)^sig3\\s*(?:=:=\\s*|\\s+)", "").trim();
if (input.length() == 0)
    throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Watch command was empty");
tasker.setVariable("sig3_input", input);
tasker.setVariable("SIG3_WatchNormalizedInput", input);
return "watch input normalized";
