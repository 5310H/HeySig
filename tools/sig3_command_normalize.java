/* Normalize numeric commands and configured semantic program aliases. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
input = tasker.getVariable("sig3_command");
if (input == null || input.trim().length() == 0) throw new JavaCodeException("No command text supplied");
input = input.trim().replaceAll("(?i)^sig(?:3)?\\s+", "");
// A short spoken name for tinnitus; do not rewrite program names.
input = input.replaceAll("(?i)^((?:(?:set|change|current|maximum|mute)\\s+|what is\\s+(?:the\\s+)?(?:current\\s+)?)?)tin(?=\\s|$)", "$1tinnitus");
alias = input.toLowerCase().replaceAll("^(?:mode|program)\\s+", "");
key = null;
if (alias.equals("conversation") || alias.equals("normal")) key = "SIG3_ModeConversationProgram";
if (alias.equals("noisy")) key = "SIG3_ModeNoisyProgram";
if (alias.equals("vnoisy") || alias.equals("very noisy") || alias.equals("verynoisy")) key = "SIG3_ModeVeryNoisyProgram";
if (key != null) {
    slot = tasker.getVariable(key);
    if (slot == null || !slot.matches("[1-6]")) throw new JavaCodeException("Configure " + key + " to an actual program slot");
    input = "program " + slot;
}
if (alias.equals("sleep")) input = "sleep";
if (alias.equals("awake") || alias.equals("wake")) input = "wake";
tasker.setVariable("sig3_command", input);
return "normalized";
