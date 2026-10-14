"""Execute persistent sleep configuration, including failed writes and changed mappings."""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
jar = Path(os.environ.get('SIG3_JSON_JAR', '/tmp/sig3-orgjson.jar'))
assert jar.is_file(), 'Set SIG3_JSON_JAR to an org.json runtime JAR (test dependency only)'
source = (root / 'tools/sig3_sleep_preferences.java').read_text()
stub = '''
class FakeTasker {int timeWrites=0;java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){if(k.equals("SIG3_SleepTime")||k.equals("SIG3_WakeTime"))timeWrites++;vars.put(k,v);}}
class FakePrefs {String data="";boolean writable=true;String pending;String getString(String k,String fallback){return data.length()==0?fallback:data;}FakePrefs edit(){return this;}FakePrefs putString(String k,String v){pending=v;return this;}boolean commit(){if(!writable)return false;data=pending;return true;}}
class FakeContext {FakePrefs prefs=new FakePrefs();FakePrefs getSharedPreferences(String k,int mode){return prefs;}}
tasker=new FakeTasker();context=new FakeContext();
for(i=1;i<=6;i++)tasker.setVariable("SIG3_ProgramName"+i,"Custom "+i);
run(mode){tasker.setVariable("sig3_sleep_pref_mode",mode);return operation();}
choose(){tasker.setVariable("sig3_sleep_program_choice","2");tasker.setVariable("sig3_wake_program_choice","1");tasker.setVariable("sig3_sleep_time_choice","23.15");tasker.setVariable("sig3_wake_time_choice","06.45");}
require(ok,message){if(!ok)throw new RuntimeException(message);}
require(run("load").equals("unconfigured"),"fresh setup");
require(tasker.getVariable("SIG3_SleepEnabled").equals("0"),"unconfigured disabled");
choose();tasker.setVariable("SIG3_SleepEnabled","1");tasker.setVariable("SIG3_SleepActive","1");run("save");original=context.prefs.data;
require(tasker.getVariable("SIG3_SleepActive").equals("0"),"save clears noise suppression");
writes=tasker.timeWrites;run("load");run("load");require(tasker.timeWrites==writes,"unchanged reload must not retrigger time contexts");
tasker.setVariable("SIG3_SleepEnabled","1");tasker.setVariable("SIG3_SleepTime","21.00");run("load");
require(tasker.getVariable("SIG3_SleepEnabled").equals("0")&&tasker.getVariable("SIG3_SleepTime").equals("23.15"),"stale globals reload while disabled");
require(tasker.getVariable("SIG3_SleepEnabled").equals("0"),"save must disable switching");
tasker.vars.clear();for(i=1;i<=6;i++)tasker.setVariable("SIG3_ProgramName"+i,"Custom "+i);run("load");
require(tasker.getVariable("SIG3_SleepTime").equals("23.15")&&tasker.getVariable("SIG3_WakeProgram").equals("1"),"restart persistence");
choose();context.prefs.writable=false;tasker.setVariable("sig3_sleep_time_choice","22.00");rejected=false;try{run("save");}catch(Exception e){rejected=true;}
require(rejected&&context.prefs.data.equals(original)&&tasker.getVariable("SIG3_SleepTime").equals("23.15"),"failed write retains configuration");context.prefs.writable=true;
for(bad:new String[]{"24.00","22.60","9.30","-1.00","22:30"}){choose();tasker.setVariable("sig3_sleep_time_choice",bad);rejected=false;try{run("save");}catch(Exception e){rejected=true;}require(rejected&&context.prefs.data.equals(original),"invalid time "+bad);}
choose();tasker.setVariable("sig3_sleep_time_choice","06.45");rejected=false;try{run("save");}catch(Exception e){rejected=true;}require(rejected,"equal times");
for(bad:new String[]{"0","7","%missing"}){choose();tasker.setVariable("sig3_sleep_program_choice",bad);rejected=false;try{run("save");}catch(Exception e){rejected=true;}require(rejected&&context.prefs.data.equals(original),"invalid slot");}
tasker.setVariable("SIG3_ProgramName1","Renamed");tasker.setVariable("SIG3_SleepEnabled","1");require(run("load").equals("mapping-changed"),"changed mapping");
require(tasker.getVariable("SIG3_SleepEnabled").equals("0")&&tasker.getVariable("SIG3_SleepProgram").equals(""),"mapping changes disable switching");
tasker.setVariable("SIG3_ProgramName1","Custom 2");choose();rejected=false;try{run("save");}catch(Exception e){rejected=true;}require(rejected&&context.prefs.data.equals(original),"duplicate programs");
print("PASS: sleep settings persistence, validation, atomic save and mapping guards");
'''
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / 'sleep.bsh'
    path.write_text('operation(){' + source + '}\n' + stub)
    result = subprocess.run(['java', '-XX:-UsePerfData', '-cp', '/usr/share/java/bsh.jar:' + str(jar),
                             'bsh.Interpreter', str(path)], capture_output=True, text=True, check=True)
    assert 'PASS:' in result.stdout, result.stdout + result.stderr
    print(result.stdout.strip())
