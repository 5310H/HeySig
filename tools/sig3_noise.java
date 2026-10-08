/* Sample indices are not calibrated sound-pressure dB. Never infer sensor units. */
import com.joaomgcd.taskerm.action.java.JavaCodeException;
readSetting(key, fallback) { value = tasker.getVariable(key); return value == null ? fallback : value; }
raw = tasker.getVariable("sig3_noise_raw");
if (raw == null || !raw.matches("-?[0-9]+(?:\\.[0-9]+)?")) throw new JavaCodeException("Noise source did not return a numeric sample");
sample = Double.parseDouble(raw);
if (Double.isNaN(sample) || Double.isInfinite(sample)) throw new JavaCodeException("Invalid noise sample");
if ("1".equals(readSetting("SIG3_NoiseInvert", "0"))) sample = -sample;
tasker.setVariable("SIG3_NoiseRaw", raw);
tasker.setVariable("SIG3_NoiseIndex", sample);
tasker.setVariable("SIG3_Observed", "Uncalibrated noise index " + sample);
tasker.setVariable("SIG3_AutoProgramSlot", "");
if (!"1".equals(readSetting("SIG3_NoiseEnabled", "0"))) return "sample-only";
if (!"1".equals(readSetting("SIG3_NoiseScaleConfirmed", "0"))) throw new JavaCodeException("Confirm noise index sign and units before enabling automation");
if ("1".equals(readSetting("SIG3_ManualOverride", "0"))) { tasker.setVariable("SIG3_NoiseCandidate", ""); tasker.setVariable("SIG3_NoiseStrikes", "0"); return "manual-override"; }
if ("1".equals(readSetting("SIG3_SleepActive", "0"))) return "sleep-active";
lowText = tasker.getVariable("SIG3_NoiseLow"); highText = tasker.getVariable("SIG3_NoiseHigh");
if (lowText == null || highText == null) throw new JavaCodeException("Configure thresholds in the measured noise index units");
low = Double.parseDouble(lowText); high = Double.parseDouble(highText);
limit = Integer.parseInt(readSetting("SIG3_NoiseStrikeLimit", "3"));
if (Double.isNaN(low) || Double.isNaN(high) || Double.isInfinite(low) || Double.isInfinite(high) || low >= high || limit < 1 || limit > 20) throw new JavaCodeException("Invalid noise thresholds or strike limit");
tier = sample >= high ? "loud" : sample <= low ? "quiet" : "middle";
if ("middle".equals(tier)) { tasker.setVariable("SIG3_NoiseCandidate", ""); tasker.setVariable("SIG3_NoiseStrikes", "0"); return "dead-band"; }
candidate = readSetting("SIG3_NoiseCandidate", "");
strikes = tier.equals(candidate) ? Integer.parseInt(readSetting("SIG3_NoiseStrikes", "0")) + 1 : 1;
if (strikes > limit) strikes = limit;
tasker.setVariable("SIG3_NoiseCandidate", tier);
tasker.setVariable("SIG3_NoiseStrikes", strikes);
if (strikes < limit) return "collecting";
slot = tasker.getVariable("loud".equals(tier) ? "SIG3_NoiseLoudProgram" : "SIG3_NoiseQuietProgram");
if (slot == null || !slot.matches("[1-6]")) throw new JavaCodeException("Configure the noise program slot (1–6)");
tasker.setVariable("SIG3_AutoProgramSlot", slot);
return "target-ready";
