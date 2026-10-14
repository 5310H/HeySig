/* Sample indices are not calibrated sound-pressure dB. Never infer sensor units. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
readSetting(key, fallback) { value = tasker.getVariable(key); return value == null || value.length()==0 || value.startsWith("%") ? fallback : value; }
resetNoise() { tasker.setVariable("SIG3_NoiseCandidate", ""); tasker.setVariable("SIG3_NoiseStrikes", "0"); }
noiseStatus(status) { tasker.setVariable("SIG3_NoiseStatus",status); return status; }
tasker.setVariable("SIG3_AutoProgramSlot", "");
tasker.setVariable("SIG3_NoiseProposedSlot", "");
raw = tasker.getVariable("sig3_noise_raw");
if (raw == null || !raw.matches("-?[0-9]+(?:\\.[0-9]+)?")) { resetNoise(); throw new JavaCodeException("Noise source did not return a numeric sample"); }
sample = Double.parseDouble(raw);
if (Double.isNaN(sample) || Double.isInfinite(sample)) { resetNoise(); throw new JavaCodeException("Invalid noise sample"); }
if ("1".equals(readSetting("SIG3_NoiseInvert", "0"))) sample = -sample;
tasker.setVariable("SIG3_NoiseRaw", raw); tasker.setVariable("SIG3_NoiseIndex", sample);
tasker.setVariable("SIG3_Observed", "Uncalibrated noise index " + sample);
now = System.currentTimeMillis();
source = readSetting("SIG3_NoiseSource","phone");
previousTime = Long.parseLong(readSetting("SIG3_NoiseLastSampleTime","0"));
if (!source.equals(readSetting("SIG3_NoiseLastSource","")) || now < previousTime || now-previousTime > 30000) resetNoise();
tasker.setVariable("SIG3_NoiseLastSource",source); tasker.setVariable("SIG3_NoiseLastSampleTime",""+now);
if (!"1".equals(readSetting("SIG3_NoiseEnabled", "0"))) { resetNoise(); return noiseStatus("sample-only"); }
if (!"1".equals(readSetting("SIG3_NoiseScaleConfirmed", "0"))) { resetNoise(); throw new JavaCodeException("Confirm noise index direction before enabling automation"); }
if ("1".equals(readSetting("SIG3_ManualOverride", "0")) || "1".equals(readSetting("SIG3_AutomationCancelled","0")) || "1".equals(readSetting("SIG3_SleepActive", "0"))) { resetNoise(); return noiseStatus("paused"); }
try {
    low = Double.parseDouble(readSetting("SIG3_NoiseLow","")); high = Double.parseDouble(readSetting("SIG3_NoiseHigh",""));
    margin = Double.parseDouble(readSetting("SIG3_NoiseHysteresis","0"));
    limit = Integer.parseInt(readSetting("SIG3_NoiseStrikeLimit", "3"));
    cooldown = Long.parseLong(readSetting("SIG3_NoiseCooldownSeconds","0"));
    if (Double.isNaN(low) || Double.isNaN(high) || Double.isNaN(margin) || Double.isInfinite(low) || Double.isInfinite(high) || Double.isInfinite(margin) || low >= high || margin < 0 || 2*margin >= high-low || limit < 1 || limit > 20 || cooldown < 0 || cooldown > 3600) throw new Exception("Invalid configuration");
} catch(Exception e) { resetNoise(); throw new JavaCodeException("Invalid noise thresholds, hysteresis, confirmation count or cooldown"); }
tier = sample >= high ? "loud" : sample <= low ? "quiet" : "middle";
currentTier = readSetting("SIG3_NoiseStableTier", "");
// Hold a settled role until its exit boundary is crossed. Large jumps may skip a role.
if ("quiet".equals(currentTier) && sample < low+margin) tier="quiet";
if ("loud".equals(currentTier) && sample > high-margin) tier="loud";
if ("middle".equals(currentTier) && sample > low-margin && sample < high+margin) tier="middle";
middleSlot = readSetting("SIG3_NoiseMiddleProgram", "");
if ("middle".equals(tier) && middleSlot.length()==0) { resetNoise(); return noiseStatus("dead-band"); }
candidate = readSetting("SIG3_NoiseCandidate", "");
strikes = tier.equals(candidate) ? Integer.parseInt(readSetting("SIG3_NoiseStrikes", "0")) + 1 : 1;
strikes = Math.min(strikes,limit);
tasker.setVariable("SIG3_NoiseCandidate", tier); tasker.setVariable("SIG3_NoiseStrikes", strikes);
if (strikes < limit) return noiseStatus("collecting " + tier + " " + strikes + "/" + limit);
slot = "middle".equals(tier) ? middleSlot : readSetting("loud".equals(tier) ? "SIG3_NoiseLoudProgram" : "SIG3_NoiseQuietProgram", "");
if (!slot.matches("[1-6]")) { resetNoise(); throw new JavaCodeException("Configure the noise program slot (1–6)"); }
tasker.setVariable("SIG3_NoiseProposedSlot", slot);
if ("observe".equals(readSetting("SIG3_NoiseMode","auto"))) {
    tasker.setVariable("SIG3_NoiseStableTier",tier);
    tasker.setVariable("SIG3_Observed", "Noise index " + sample + "; proposed " + tier + ": " + readSetting("SIG3_ProgramName"+slot,"slot "+slot) + "; observation only");
    return noiseStatus("observation");
}
lastSwitch = Long.parseLong(readSetting("SIG3_NoiseLastSwitchTime","0"));
if (now < lastSwitch || now-lastSwitch < cooldown*1000) { resetNoise(); return noiseStatus("cooldown"); }
tasker.setVariable("SIG3_AutoProgramSlot", slot);
return noiseStatus("target-ready");
