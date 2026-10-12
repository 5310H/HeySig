"""Execute the actual persistent snapshot helper in BeanShell with a real JSON parser."""
import os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
jar=Path(os.environ.get('SIG3_JSON_JAR','/tmp/sig3-orgjson.jar'))
assert jar.is_file(),'Set SIG3_JSON_JAR to an org.json runtime JAR (test dependency only)'
source=(ROOT/'tools/sig3_settings_snapshot.java').read_text().replace('import com.joaomgcd.taskerm.action.java.JavaCodeException;','').replace('JavaCodeException','Exception')
stub='''import org.json.*; import java.io.*;
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){vars.put(k,v);}}
class FakeContext {File dir;File getFilesDir(){return dir;}}
tasker=new FakeTasker();context=new FakeContext();
configure(){tasker.setVariable("SIG3_ProgramName1","Universal");tasker.setVariable("SIG3_ProgramName2","TV");tasker.setVariable("SIG3_Program","Universal");tasker.setVariable("SIG3_Level","9");tasker.setVariable("SIG3_BalanceLevel","0");tasker.setVariable("SIG3_TinnitusLevel","7");tasker.setVariable("SIG3_TinnitusAvailable","1");}
configure();
'''
harness='''
step(mode){tasker.setVariable("sig3_settings_mode",mode);return operation();}
capture(family){tasker.setVariable("sig3_settings_control",family);step("capture");}
save(){step("begin-save");capture("Volume");capture("Balance");capture("Tinnitus");step("commit");}
readSaved(){return new JSONObject(new String(java.nio.file.Files.readAllBytes(file.toPath()),"UTF-8"));}
writeSaved(json){java.nio.file.Files.write(file.toPath(),json.toString().getBytes("UTF-8"),new java.nio.file.OpenOption[0]);}
expectFailure(mode){failed=false;try{step(mode);}catch(Exception failure){failed=true;}if(!failed)throw new RuntimeException("Expected rejection for "+mode);}
check(value){if(!value)throw new RuntimeException("Snapshot assertion failed");}
'''
cases=[
 ('persist/load after restarted tasker','save();tasker=new FakeTasker();configure();step("load");check(tasker.getVariable("SIG3_SettingsVolume").equals("9"));check(tasker.getVariable("SIG3_SettingsTinnitus").equals("7"));'),
 ('charging defaults do not overwrite','save();before=readSaved().toString();tasker.setVariable("SIG3_Level","0");tasker.setVariable("SIG3_TinnitusLevel","0");step("load");check(readSaved().toString().equals(before));check(tasker.getVariable("SIG3_SettingsVolume").equals("9"));'),
 ('without tinnitus','tasker.setVariable("SIG3_TinnitusAvailable","0");save();step("load");check(tasker.getVariable("SIG3_SettingsTinnitus").equals(""));step("finish-restore");check(tasker.getVariable("SIG3_SettingsOK").equals("1"));'),
 ('no saved file','expectFailure("load");'),
 ('corrupt file','java.nio.file.Files.write(file.toPath(),"broken".getBytes(),new java.nio.file.OpenOption[0]);expectFailure("load");'),
 ('out of range volume','save();j=readSaved();j.getJSONObject("controls").put("Volume",16);writeSaved(j);expectFailure("load");'),
 ('fractional value','save();j=readSaved();j.getJSONObject("controls").put("Volume",8.5);writeSaved(j);expectFailure("load");'),
 ('wrong numeric type','save();j=readSaved();j.getJSONObject("controls").put("Volume","8");writeSaved(j);expectFailure("load");'),
 ('out of range balance','save();j=readSaved();j.getJSONObject("controls").put("Balance",-9);writeSaved(j);expectFailure("load");'),
 ('out of range tinnitus','save();j=readSaved();j.getJSONObject("controls").put("Tinnitus",16);writeSaved(j);expectFailure("load");'),
 ('missing tinnitus field','save();j=readSaved();j.getJSONObject("controls").remove("Tinnitus");writeSaved(j);expectFailure("load");'),
 ('invalid version','save();j=readSaved();j.put("version",2);writeSaved(j);expectFailure("load");'),
 ('fractional version','save();j=readSaved();j.put("version",1.1);writeSaved(j);expectFailure("load");'),
 ('invalid timestamp','save();j=readSaved();j.put("savedAt",0);writeSaved(j);expectFailure("load");'),
 ('renamed configured program','save();tasker.setVariable("SIG3_ProgramName1","Renamed");expectFailure("load");'),
 ('ambiguous mapping','save();tasker.setVariable("SIG3_ProgramName2","Universal");expectFailure("load");'),
 ('unknown saved program','save();j=readSaved();j.put("program","Unknown");writeSaved(j);expectFailure("load");'),
 ('save changed program retains previous snapshot','save();before=readSaved().toString();step("begin-save");capture("Volume");capture("Balance");capture("Tinnitus");tasker.setVariable("SIG3_Program","TV");expectFailure("commit");check(readSaved().toString().equals(before));'),
 ('incomplete capture retains previous snapshot','save();before=readSaved().toString();step("begin-save");capture("Volume");expectFailure("commit");check(readSaved().toString().equals(before));'),
 ('disk failure retains previous snapshot','save();before=readSaved().toString();pending=new File(context.getFilesDir(),"heysig3-settings-v1.json.pending");check(pending.mkdir());step("begin-save");capture("Volume");capture("Balance");capture("Tinnitus");expectFailure("commit");check(readSaved().toString().equals(before));'),
 ('restore program changed','save();step("load");tasker.setVariable("SIG3_Program","TV");expectFailure("verify-program");'),
 ('restore value mismatch','save();step("load");tasker.setVariable("sig3_settings_control","Volume");tasker.setVariable("SIG3_Level","8");expectFailure("verify-control");'),
 ('restore config changed','save();step("load");tasker.setVariable("SIG3_ProgramName2","Renamed");expectFailure("verify-program");'),
 ('lost tinnitus reports partial and retains snapshot','save();before=readSaved().toString();step("load");tasker.setVariable("SIG3_TinnitusAvailable","0");step("finish-restore");check(tasker.getVariable("SIG3_SettingsOK").equals("0"));check(tasker.getVariable("SIG3_Error").startsWith("Partial restore:"));check(readSaved().toString().equals(before));'),
 ('successful fresh value verification','save();step("load");for(f:new String[]{"Volume","Balance","Tinnitus"}){tasker.setVariable("sig3_settings_control",f);step("verify-control");}step("finish-restore");check(tasker.getVariable("SIG3_SettingsOK").equals("1"));'),
]
auto_source=(ROOT/'tools/sig3_settings_auto.java').read_text()
harness+='\nautomatic(){tasker.setVariable("sig3_settings_auto_mode","prepare");autoOperation();if("update".equals(tasker.getVariable("SIG3_SettingsAutoMode")))step("commit");else if("full".equals(tasker.getVariable("SIG3_SettingsAutoMode")))save();if(tasker.getVariable("SIG3_SettingsAutoMode").length()>0){tasker.setVariable("sig3_settings_auto_mode","finish");autoOperation();}}\n'
cases += [
 ('automatic last volume preserves other controls','save();tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Set");tasker.setVariable("SIG3_Previous","9");tasker.setVariable("SIG3_Observed","8");automatic();j=readSaved();check(j.getJSONObject("controls").getInt("Volume")==8);check(j.getJSONObject("controls").getInt("Balance")==0);check(j.getJSONObject("controls").getInt("Tinnitus")==7);check(tasker.getVariable("SIG3_Observed").equals("8"));check(tasker.getVariable("SIG3_Family").equals("Volume"));'),
 ('automatic disk failure preserves command and old snapshot','save();before=readSaved().toString();pending=new File(context.getFilesDir(),"heysig3-settings-v1.json.pending");check(pending.mkdir());tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Set");tasker.setVariable("SIG3_Previous","9");tasker.setVariable("SIG3_Observed","8");tasker.setVariable("sig3_settings_auto_mode","prepare");autoOperation();expectFailure("commit");tasker.setVariable("sig3_settings_auto_mode","finish");autoOperation();check(readSaved().toString().equals(before));check(tasker.getVariable("SIG3_CommandOK").equals("1"));check(tasker.getVariable("SIG3_Observed").equals("8"));check(tasker.getVariable("SIG3_SettingsAutoError").length()>0);'),
 ('automatic no-op preserves snapshot','save();before=readSaved().toString();tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Set");tasker.setVariable("SIG3_Previous","9");tasker.setVariable("SIG3_Observed","9");automatic();check(readSaved().toString().equals(before));'),
 ('failed change preserves snapshot','save();before=readSaved().toString();tasker.setVariable("SIG3_CommandOK","0");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Set");tasker.setVariable("SIG3_Previous","9");tasker.setVariable("SIG3_Observed","8");automatic();check(readSaved().toString().equals(before));'),
 ('read does not overwrite','save();before=readSaved().toString();tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Current");tasker.setVariable("SIG3_Previous","9");tasker.setVariable("SIG3_Observed","0");automatic();check(readSaved().toString().equals(before));'),
 ('restore does not overwrite','save();before=readSaved().toString();tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Settings");tasker.setVariable("sig3_request2","Restore");automatic();check(readSaved().toString().equals(before));'),
 ('first change establishes complete baseline','tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("sig3_request2","Set");tasker.setVariable("SIG3_Previous","8");tasker.setVariable("SIG3_Observed","9");automatic();check(readSaved().getJSONObject("controls").getInt("Volume")==9);check(readSaved().getJSONObject("controls").getInt("Tinnitus")==7);'),
 ('new program establishes controls without tinnitus','save();tasker.setVariable("SIG3_Program","TV");tasker.setVariable("SIG3_TinnitusAvailable","0");tasker.setVariable("SIG3_CommandOK","1");tasker.setVariable("SIG3_Family","Program");tasker.setVariable("sig3_request2","Switch");tasker.setVariable("SIG3_Previous","Universal");automatic();check(readSaved().getString("program").equals("TV"));check(readSaved().getJSONObject("controls").isNull("Tinnitus"));'),
]
for name,setup in cases:
 with tempfile.TemporaryDirectory() as directory:
  path=Path(directory)/'snapshot.bsh'
  script=stub+'context.dir=new File("'+directory+'");file=new File(context.dir,"heysig3-settings-v1.json");\noperation(){\n'+source+'\n}\nautoOperation(){\n'+auto_source+'\n}\n'+harness+setup+'\nprint("PASS");'
  path.write_text(script)
  result=subprocess.run(['java','-XX:-UsePerfData','-cp',str(jar)+':/usr/share/java/bsh.jar','bsh.Interpreter',str(path)],capture_output=True,text=True,check=True)
  assert result.stdout.strip()=='PASS',(name,result.stdout,result.stderr)
print(f'{len(cases)} actual BeanShell snapshot cases passed: persistence, charging defaults, validation, atomic replacement and partial restore')
