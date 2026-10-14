/* Commit settled state only after fresh program readback; clear pending history. */
if ("1".equals(tasker.getVariable("SIG3_ProgramOK"))) {
    tasker.setVariable("SIG3_NoiseStableTier",tasker.getVariable("SIG3_NoiseCandidate"));
    previous = tasker.getVariable("SIG3_Previous"); expected = tasker.getVariable("SIG3_Expected");
    if (expected != null && !expected.equals(previous))
        tasker.setVariable("SIG3_NoiseLastSwitchTime",""+System.currentTimeMillis());
    tasker.setVariable("SIG3_NoiseStatus","selected");
} else tasker.setVariable("SIG3_NoiseStatus","deferred or failed; waiting for fresh samples");
tasker.setVariable("SIG3_NoiseCandidate", ""); tasker.setVariable("SIG3_NoiseStrikes", "0");
tasker.setVariable("SIG3_AutoProgramSlot", "");
return "noise attempt finished";
