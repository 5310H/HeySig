"""Execute the shipped noise decision and persistence helpers in BeanShell."""
from pathlib import Path
import os
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
JAR = Path(os.environ.get("SIG3_JSON_JAR", "/tmp/sig3-orgjson.jar"))
assert JAR.is_file(), "Set SIG3_JSON_JAR to the test-only org.json runtime JAR"
engine = (ROOT/'tools/sig3_noise.java').read_text().replace('import com.joaomgcd.taskerm.action.java.JavaCodeException;', '').replace('JavaCodeException', 'Exception')
finish = (ROOT/'tools/sig3_noise_finish.java').read_text()
prefs = (ROOT/'tools/sig3_noise_preferences.java').read_text()
stub = '''
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,Object v){vars.put(k,v.toString());}}
class FakePrefs {String data="";boolean writable=true;String pending;String getString(String k,String fallback){return data.length()==0?fallback:data;}FakePrefs edit(){return this;}FakePrefs putString(String k,String v){pending=v;return this;}boolean commit(){if(!writable)return false;data=pending;return true;}}
class FakeContext {FakePrefs prefs=new FakePrefs();FakePrefs getSharedPreferences(String k,int mode){return prefs;}}
tasker=new FakeTasker();context=new FakeContext();
require(ok,message){if(!ok)throw new RuntimeException(message);}
set(k,v){tasker.setVariable("SIG3_Noise"+k,v);}
get(k){return tasker.getVariable("SIG3_Noise"+k);}
sample(raw){tasker.setVariable("sig3_noise_raw",raw);return decide();}
seed(){tasker.vars.clear();for(i=1;i<=6;i++)tasker.setVariable("SIG3_ProgramName"+i,"Custom "+i);set("Enabled","1");set("Mode","observe");set("ScaleConfirmed","1");set("Low","-60");set("High","-40");set("Hysteresis","3");set("StrikeLimit","3");set("QuietProgram","1");set("MiddleProgram","2");set("LoudProgram","3");set("CooldownSeconds","60");set("Source","phone");}
three(raw){sample(raw);sample(raw);return sample(raw);}
seed();three("-65");require(get("StableTier").equals("quiet")&&get("ProposedSlot").equals("1"),"quiet observation");require(tasker.getVariable("SIG3_AutoProgramSlot").equals(""),"observation cannot dispatch");
three("-59");require(get("StableTier").equals("quiet"),"quiet hysteresis");three("-55");require(get("StableTier").equals("middle"),"exit quiet");three("-62");require(get("StableTier").equals("middle"),"middle hysteresis");three("-65");require(get("StableTier").equals("quiet"),"exit middle");
three("-35");require(get("StableTier").equals("loud"),"direct quiet-to-loud");three("-42");require(get("StableTier").equals("loud"),"loud hysteresis");three("-45");require(get("StableTier").equals("middle"),"exit loud");
seed();sample("-65");sample("-65");bad=false;try{sample("bad");}catch(Exception e){bad=true;}require(bad&&get("Strikes").equals("0"),"invalid sample clears pending");sample("-65");require(get("Strikes").equals("1"),"no stale confirmation");
set("LastSampleTime",""+(System.currentTimeMillis()-31000));sample("-65");require(get("Strikes").equals("1"),"sample gap resets");set("Source","watch");sample("-65");require(get("Strikes").equals("1"),"source isolation");
tasker.setVariable("SIG3_ManualOverride","1");sample("-65");require(get("Strikes").equals("0"),"manual override");tasker.setVariable("SIG3_ManualOverride","0");
tasker.setVariable("SIG3_AutomationCancelled","1");sample("-65");require(get("Strikes").equals("0"),"cancel");tasker.setVariable("SIG3_AutomationCancelled","0");
tasker.setVariable("SIG3_SleepActive","1");sample("-65");require(get("Strikes").equals("0"),"sleep");tasker.setVariable("SIG3_SleepActive","0");
seed();set("Mode","auto");three("-65");require(tasker.getVariable("SIG3_AutoProgramSlot").equals("1"),"confirmed automatic target");
tasker.setVariable("SIG3_ProgramOK","0");finishAttempt();require(get("Strikes").equals("0")&&get("LastSwitchTime")==null,"failure clears without cooldown");
three("-65");tasker.setVariable("SIG3_ProgramOK","1");tasker.setVariable("SIG3_Previous","Custom 2");tasker.setVariable("SIG3_Expected","Custom 1");finishAttempt();first=get("LastSwitchTime");three("-35");require(tasker.getVariable("SIG3_AutoProgramSlot").equals("")&&get("Strikes").equals("0"),"cooldown");
set("CooldownSeconds","0");three("-65");tasker.setVariable("SIG3_Previous","Custom 1");finishAttempt();require(get("LastSwitchTime").equals(first),"no-op does not extend cooldown");
seed();for(raw:new String[]{"NaN","Infinity","1e999","%missing"}){bad=false;try{sample(raw);}catch(Exception e){bad=true;}require(bad,"invalid sample "+raw);}
set("Hysteresis","10");bad=false;try{sample("-65");}catch(Exception e){bad=true;}require(bad,"overlapping hysteresis");

choose(){for(k:new String[]{"quiet","middle","loud","low","high","margin","strikes","cooldown"})tasker.setVariable("sig3_noise_choice_"+k,k.equals("quiet")?"1":k.equals("middle")?"2":k.equals("loud")?"3":k.equals("low")?"-60":k.equals("high")?"-40":k.equals("cooldown")?"60":"3");tasker.setVariable("sig3_noise_choice_confirmed","1");}
preferences(mode){tasker.setVariable("sig3_noise_pref_mode",mode);return configure();}
seed();preferences("load");require(get("Enabled").equals("0")&&get("SettingsReady").equals("0"),"fresh configuration off");
choose();preferences("save");original=context.prefs.data;require(get("Enabled").equals("0")&&get("Mode").equals("observe"),"save cannot start switching");
set("Enabled","1");preferences("load");require(get("Enabled").equals("1"),"unchanged load preserves polling");
tasker.vars.clear();for(i=1;i<=6;i++)tasker.setVariable("SIG3_ProgramName"+i,"Custom "+i);preferences("load");require(get("QuietProgram").equals("1")&&get("Enabled").equals("0"),"restart reload");
choose();context.prefs.writable=false;tasker.setVariable("sig3_noise_choice_low","-61");bad=false;try{preferences("save");}catch(Exception e){bad=true;}require(bad&&context.prefs.data.equals(original)&&get("Low").equals("-60"),"failed save retains settings");context.prefs.writable=true;
choose();tasker.setVariable("sig3_noise_choice_high","-65");bad=false;try{preferences("save");}catch(Exception e){bad=true;}require(bad&&context.prefs.data.equals(original),"invalid thresholds");
tasker.setVariable("SIG3_ProgramName1","Renamed");set("Enabled","1");require(preferences("load").equals("mapping-changed")&&get("Enabled").equals("0"),"renamed programs pause");
print("PASS: actual noise hysteresis, observations, invalid/gapped/source samples, override/cancel/sleep, cooldown/no-op, atomic preferences and restart/mapping guards");
'''
with tempfile.TemporaryDirectory() as folder:
    p = Path(folder)/'noise.bsh'
    p.write_text('decide(){'+engine+'}\nfinishAttempt(){'+finish+'}\nconfigure(){'+prefs+'}\n'+stub)
    r = subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar:'+str(JAR),'bsh.Interpreter',str(p)],capture_output=True,text=True)
    assert r.returncode == 0 and 'PASS:' in r.stdout, r.stdout+r.stderr
    print(r.stdout.strip())
