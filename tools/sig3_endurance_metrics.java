/* Test-only bounded endurance summary; called after the production numeric logger. */
import org.json.*;
import java.io.*;
ev(key) { v=tasker.getVariable("SIG3_"+key);return v==null||v.startsWith("%")?"":v; }
if(!"1".equals(ev("EnduranceEnabled"))) return "endurance off";
try {
    now=System.currentTimeMillis();uptime=android.os.SystemClock.elapsedRealtime();
    deadline=Long.parseLong(ev("EnduranceDeadline"));deadlineUptime=Long.parseLong(ev("EnduranceDeadlineUptime"));
    file=new File("/sdcard/Tasker/sig3-endurance-summary.json");
    if(file.isFile()) {
        in=new FileInputStream(file);bytes=new byte[(int)file.length()];in.read(bytes);in.close();
        summary=new JSONObject(new String(bytes,"UTF-8"));
        if(!ev("EnduranceRunId").equals(summary.getString("runId")))throw new Exception("Existing summary belongs to another run");
    } else {
        summary=new JSONObject();summary.put("runId",ev("EnduranceRunId"));summary.put("started",now);summary.put("startedUptime",uptime);summary.put("deadline",deadline);summary.put("deadlineUptime",deadlineUptime);
        for(key:new String[]{"ticks","freshSamples","failedAttempts","skippedTicks","lockedTicks","chargingTicks","maxSampleGapMillis","maxTickGapMillis","lastSampleTime"})summary.put(key,0);
    }
    battery=new JSONObject();intent=context.registerReceiver(null,new android.content.IntentFilter("android.intent.action.BATTERY_CHANGED"));
    if(intent!=null)for(key:new String[]{"level","scale","plugged","temperature","voltage"})battery.put(key,intent.getIntExtra(key,-1));
    manager=context.getSystemService("batterymanager");if(manager!=null)battery.put("chargeCounterMicroAh",manager.getIntProperty(1));
    if(!summary.has("startBattery"))summary.put("startBattery",battery);summary.put("lastBattery",battery);
    if(summary.has("lastUptime"))summary.put("maxTickGapMillis",Math.max(summary.getLong("maxTickGapMillis"),uptime-summary.getLong("lastUptime")));
    summary.put("ticks",summary.getLong("ticks")+1);summary.put("lastTick",now);summary.put("lastUptime",uptime);
    if(battery.optInt("plugged",-1)>0)summary.put("chargingTicks",summary.getLong("chargingTicks")+1);
    lock=context.getSystemService("keyguard");if(lock!=null&&lock.isKeyguardLocked())summary.put("lockedTicks",summary.getLong("lockedTicks")+1);
    if("1".equals(ev("NoisePollSampled"))) {
        sample=ev("NoiseLastSampleTime");stamp=sample.length()==0?0:Long.parseLong(sample);
        if(stamp>summary.getLong("lastSampleTime")) {
            previous=summary.getLong("lastSampleTime");if(previous>0)summary.put("maxSampleGapMillis",Math.max(summary.getLong("maxSampleGapMillis"),stamp-previous));
            summary.put("lastSampleTime",stamp);
            raw=Double.parseDouble(ev("NoiseIndex"));
            if("1".equals(ev("CommandOK"))&&ev("Error").length()==0&&!Double.isNaN(raw)&&!Double.isInfinite(raw))summary.put("freshSamples",summary.getLong("freshSamples")+1);
            else summary.put("failedAttempts",summary.getLong("failedAttempts")+1);
        } else summary.put("failedAttempts",summary.getLong("failedAttempts")+1);
    } else summary.put("skippedTicks",summary.getLong("skippedTicks")+1);
    summary.put("noiseMode",ev("NoiseMode"));summary.put("lastError",ev("Error"));
    if(uptime<summary.getLong("startedUptime"))throw new Exception("Phone restarted during the run");
    complete=uptime>=deadlineUptime;summary.put("status",complete?"completed":"running");if(complete)summary.put("stopDelayMillis",uptime-deadlineUptime);
    tmp=new File(file.getPath()+".pending");out=new FileOutputStream(tmp);out.write(summary.toString(2).getBytes("UTF-8"));out.getFD().sync();out.close();if(!tmp.renameTo(file))throw new Exception("Summary replacement failed");
    if(complete) {
        tasker.setVariable("SIG3_NoiseEnabled","0");tasker.setVariable("SIG3_NoiseLogEnabled","0");tasker.setVariable("SIG3_EnduranceEnabled","0");
        tasker.setVariable("SIG3_NoiseCandidate","");tasker.setVariable("SIG3_NoiseStrikes","0");tasker.setVariable("SIG3_NoiseStableTier","");tasker.setVariable("SIG3_NoiseStatus","stopped");
    }
    tasker.setVariable("SIG3_EnduranceStatus",complete?"completed":"running");return "endurance summary saved";
} catch(Exception failure) {
    tasker.setVariable("SIG3_EnduranceStatus","failed: "+failure.getMessage());tasker.setVariable("SIG3_NoiseEnabled","0");tasker.setVariable("SIG3_NoiseLogEnabled","0");tasker.setVariable("SIG3_EnduranceEnabled","0");return "endurance stopped after diagnostic failure";
}
