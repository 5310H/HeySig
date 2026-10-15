/* One-time label migration: no Signia actions and no slider or schedule changes. */
import org.json.*;
import java.io.*;
value(key) { v=tasker.getVariable("SIG3_"+key);return v==null||v.startsWith("%")?"":v; }
readFile(f) { in=new FileInputStream(f);try {bytes=new byte[(int)f.length()];new java.io.DataInputStream(in).readFully(bytes);return new String(bytes,"UTF-8");}finally{in.close();} }
writeFile(f,text) {tmp=new File(f.getPath()+".pending");out=new FileOutputStream(tmp);try{out.write(text.getBytes("UTF-8"));out.getFD().sync();}finally{out.close();}if(!tmp.renameTo(f))throw new Exception("Cannot replace "+f.getName());}
renameMapping(text,names,oldName) {
    if(text.length()==0)return text;
    j=new JSONObject(text);a=j.getJSONArray("programs");
    if(a.length()!=6)throw new Exception("Unexpected program mapping length");
    for(i=0;i<6;i++) {
        expected=names.getString(i);
        if(i==1) {if(!a.getString(i).equals(oldName)&&!a.getString(i).equals("Sleep"))throw new Exception("Unexpected saved slot 2");}
        else if(!a.getString(i).equals(expected))throw new Exception("Another saved program differs at slot "+(i+1));
    }
    a.put(1,"Sleep");
    if(j.has("program")&&oldName.equals(j.getString("program")))j.put("program","Sleep");
    return j.toString();
}
oldName="Off just Tinnitus";originalName=value("ProgramName2");
if(!oldName.equals(originalName)&&!"Sleep".equals(originalName))throw new Exception("Unexpected configured slot 2: "+originalName);
if("1".equals(value("NoiseEnabled"))||"1".equals(value("SleepEnabled"))||"1".equals(value("VoiceBusy")))throw new Exception("Stop automation or voice capture before renaming");
running=tasker.getVariable("TRUN");if(running!=null&&running.matches("(?s).*(?:^|,)SIG3_Worker(?:,|$).*"))throw new Exception("Worker is busy");
names=new JSONArray();for(i=1;i<=6;i++)names.put(value("ProgramName"+i));
noise=context.getSharedPreferences("heysig3-noise",0);sleep=context.getSharedPreferences("heysig3-sleep",0);
oldNoise=noise.getString("configuration","");oldSleep=sleep.getString("configuration","");
snapshot=new File(context.getFilesDir(),"heysig3-settings-v1.json");oldSnapshot=snapshot.isFile()?readFile(snapshot):"";
newNoise=renameMapping(oldNoise,names,oldName);newSleep=renameMapping(oldSleep,names,oldName);newSnapshot=renameMapping(oldSnapshot,names,oldName);
backup=new JSONObject();backup.put("ProgramName2",originalName);backup.put("noise",oldNoise);backup.put("sleep",oldSleep);backup.put("snapshot",oldSnapshot);
backupFile=new File(context.getFilesDir(),"heysig3-before-sleep-rename-"+System.currentTimeMillis()+".json");writeFile(backupFile,backup.toString(2));
try {
    if(oldSnapshot.length()>0)writeFile(snapshot,newSnapshot);
    if(oldNoise.length()>0&&!noise.edit().putString("configuration",newNoise).commit())throw new Exception("Noise mapping write failed");
    if(oldSleep.length()>0&&!sleep.edit().putString("configuration",newSleep).commit())throw new Exception("Sleep mapping write failed");
    tasker.setVariable("SIG3_ProgramName2","Sleep");
}catch(Exception failure) {
    if(oldSnapshot.length()>0)writeFile(snapshot,oldSnapshot);
    if(oldNoise.length()>0&&!noise.edit().putString("configuration",oldNoise).commit())throw new Exception("Noise rollback failed: "+failure);
    if(oldSleep.length()>0&&!sleep.edit().putString("configuration",oldSleep).commit())throw new Exception("Sleep rollback failed: "+failure);
    tasker.setVariable("SIG3_ProgramName2",originalName);throw failure;
}
result=new JSONObject();result.put("before",backup);result.put("ProgramName2",value("ProgramName2"));
result.put("noise",noise.getString("configuration",""));result.put("sleep",sleep.getString("configuration",""));result.put("snapshot",snapshot.isFile()?readFile(snapshot):"");result.put("backupFile",backupFile.getName());
writeFile(new File("/sdcard/Tasker/sig3-sleep-rename-result.json"),result.toString(2));
return "HeySig slot 2 renamed to Sleep; saved values preserved";
