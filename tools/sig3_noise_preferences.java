/* Save role assignments and noise-index settings atomically; never enable on save. */
import org.json.*;
nv(key) { v=tasker.getVariable(key); return v==null || v.startsWith("%") ? "" : v; }
programs() {
    a=new JSONArray();
    for(i=1;i<=6;i++) {
        v=nv("SIG3_ProgramName"+i).trim();
        if(v.length()==0) throw new Exception("Configure all six program names");
        for(j=0;j<a.length();j++) if(v.equals(a.getString(j))) throw new Exception("Program names must be unique");
        a.put(v);
    }
    return a;
}
validate(c) {
    for(k:new String[]{"quiet","middle","loud"}) if(!c.getString(k).matches("[1-6]")) throw new Exception("Choose all three programs");
    low=c.getDouble("low"); high=c.getDouble("high"); margin=c.getDouble("margin");
    if(Double.isNaN(low)||Double.isNaN(high)||Double.isNaN(margin)||Double.isInfinite(low)||Double.isInfinite(high)||Double.isInfinite(margin)||low>=high||margin<0||2*margin>=high-low) throw new Exception("Choose ordered thresholds and a smaller hysteresis margin");
    if(c.getInt("strikes")<1||c.getInt("strikes")>20) throw new Exception("Confirmation count must be 1–20");
    if(c.getInt("cooldown")<0||c.getInt("cooldown")>3600) throw new Exception("Cooldown must be 0–3600 seconds");
    if(!"phone".equals(c.getString("source"))) throw new Exception("Only the verified phone sampler is supported by these settings");
}
prefs=context.getSharedPreferences("heysig3-noise",0);
mode=nv("sig3_noise_pref_mode");
if("save".equals(mode)) {
    config=new JSONObject();config.put("version",1);config.put("programs",programs());
    for(k:new String[]{"quiet","middle","loud","low","high","margin","strikes","cooldown"}) config.put(k,nv("sig3_noise_choice_"+k));
    config.put("source","phone");config.put("confirmed","1".equals(nv("sig3_noise_choice_confirmed")));
    validate(config);
    if(!prefs.edit().putString("configuration",config.toString()).commit()) throw new Exception("Could not save noise settings; previous settings retained");
} else if("load".equals(mode)) {
    saved=prefs.getString("configuration","");
    if(saved.length()==0) {
        tasker.setVariable("SIG3_NoiseEnabled","0");
        tasker.setVariable("SIG3_NoiseSettingsReady","0");
        tasker.setVariable("SIG3_NoiseSettingsStatus","Choose programs and measured noise-index thresholds");
        return "unconfigured";
    }
    config=new JSONObject(saved);
    if(config.getInt("version")!=1||!config.getJSONArray("programs").toString().equals(programs().toString())) {
        tasker.setVariable("SIG3_NoiseEnabled","0");tasker.setVariable("SIG3_NoiseSettingsReady","0");
        tasker.setVariable("SIG3_NoiseSettingsStatus","Program mapping changed; choose noise programs again");
        return "mapping-changed";
    }
    validate(config);
} else throw new Exception("Unknown noise settings operation");
fields=new String[]{"QuietProgram","MiddleProgram","LoudProgram","Low","High","Hysteresis","StrikeLimit","CooldownSeconds"};
keys=new String[]{"quiet","middle","loud","low","high","margin","strikes","cooldown"};
changed="save".equals(mode)||!"phone".equals(nv("SIG3_NoiseSource"))||!"0".equals(nv("SIG3_NoiseInvert"));
for(i=0;i<fields.length;i++) if(!config.getString(keys[i]).equals(nv("SIG3_Noise"+fields[i]))) changed=true;
confirmed=config.getBoolean("confirmed")?"1":"0";
if(!confirmed.equals(nv("SIG3_NoiseScaleConfirmed"))) changed=true;
if(changed) {
    tasker.setVariable("SIG3_NoiseEnabled","0");tasker.setVariable("SIG3_NoiseMode","observe");
    for(k:new String[]{"Candidate","StableTier","LastSource","LastSampleTime","LastSwitchTime","ProposedSlot"}) tasker.setVariable("SIG3_Noise"+k,"");
    tasker.setVariable("SIG3_NoiseStrikes","0");tasker.setVariable("SIG3_AutoProgramSlot","");
}
for(i=0;i<fields.length;i++) tasker.setVariable("SIG3_Noise"+fields[i],config.getString(keys[i]));
tasker.setVariable("SIG3_NoiseSource","phone");tasker.setVariable("SIG3_NoiseInvert","0");tasker.setVariable("SIG3_NoiseScaleConfirmed",confirmed);
tasker.setVariable("SIG3_NoiseSettingsReady","1");
tasker.setVariable("SIG3_NoiseSettingsStatus","Quiet: "+config.getJSONArray("programs").getString(Integer.parseInt(config.getString("quiet"))-1)+"; Noisy: "+config.getJSONArray("programs").getString(Integer.parseInt(config.getString("middle"))-1)+"; Very noisy: "+config.getJSONArray("programs").getString(Integer.parseInt(config.getString("loud"))-1)+"; saved with switching off");
return "noise settings "+mode;
