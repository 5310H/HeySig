/* Optional bounded numeric diagnostics. Never record audio or accessibility text. */
if (!"1".equals(tasker.getVariable("SIG3_NoiseLogEnabled"))) return "logging off";
import org.json.JSONObject;
import java.io.*;
try {
    row=new JSONObject();row.put("time",System.currentTimeMillis());
    for(key:new String[]{"NoisePollSampled","NoiseLastSampleTime","NoiseCalibrationStageTime","NoiseSource","NoiseMode","NoiseRaw","NoiseIndex","NoiseStatus","NoiseCandidate","NoiseStrikes","NoiseProposedSlot","NoiseEnabled","VoiceBusy","WakeEnabled","ManualOverride","SleepActive","CommandOK","Error","Program"}) {
        value=tasker.getVariable("SIG3_"+key);row.put(key,value==null||value.startsWith("%")?"":value);
    }
    stage=tasker.getVariable("SIG3_NoiseCalibrationStage");
    row.put("stage","quiet".equals(stage)||"conversation".equals(stage)||"very-noisy".equals(stage)?stage:"unlabelled");
    service=tasker.getAccessibilityService();root=service==null?null:service.getRootInActiveWindow();
    row.put("foregroundPackage",root==null||root.getPackageName()==null?"":root.getPackageName().toString());
    lock=context.getSystemService("keyguard");row.put("locked",lock!=null&&lock.isKeyguardLocked());
    file=new File("/sdcard/Tasker/sig3-noise-observation.jsonl");
    // A single polling task owns this file. Bound storage even if diagnostics remain on.
    append=file.isFile()&&file.length()<262144;
    output=new FileOutputStream(file,append);
    try { output.write((row.toString()+"\n").getBytes("UTF-8")); } finally { output.close(); }
    tasker.setVariable("SIG3_NoiseLogError","");
    return "numeric sample logged";
} catch(Exception failure) {
    tasker.setVariable("SIG3_NoiseLogError","Could not record noise diagnostics: "+failure.getMessage());
    return "diagnostic write failed";
}
