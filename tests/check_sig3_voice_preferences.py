"""Execute preference persistence and verify independent speech routing."""
from pathlib import Path
import json,subprocess,tempfile
from heysig3_runtime import Phone
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_voice_preferences.java').read_text().replace('com.joaomgcd.taskerm.action.java.JavaCodeException','RuntimeException')
stub='''class Preferences {java.util.Map data=new java.util.HashMap();boolean writable=true;String getString(String k,String d){return data.containsKey(k)?(String)data.get(k):d;}Editor edit(){return new Editor(this);}}
class Editor {Preferences prefs;java.util.Map staged=new java.util.HashMap();Editor(Preferences p){prefs=p;}Editor putString(String k,String v){staged.put(k,v);return this;}boolean commit(){if(!prefs.writable)return false;prefs.data.putAll(staged);return true;}}
class Context {Preferences prefs=new Preferences();Preferences getSharedPreferences(String n,int mode){return prefs;}}
class Tasker {java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}}
context=new Context();tasker=new Tasker();'''
cases=[('defaults','tasker.setVariable("sig3_voice_pref_mode","load");run();', '1','1'),('legacy silence','tasker.setVariable("SIG3_VoiceResponses","0");tasker.setVariable("sig3_voice_pref_mode","load");run();','0','0'),('stored fallback','context.prefs.data.put("responses","0");context.prefs.data.put("prompts","1");tasker.setVariable("sig3_voice_pref_mode","load");run();','0','1'),('global override','context.prefs.data.put("responses","0");tasker.setVariable("SIG3_VoiceResponses","1");tasker.setVariable("SIG3_VoicePrompts","0");tasker.setVariable("sig3_voice_pref_mode","load");run();','1','0')]
for results in ['0','1']:
 for prompts in ['0','1']:
  setup='tasker.setVariable("sig3_voice_pref_mode","save");tasker.setVariable("sig3_voice_results_choice",'+json.dumps(results)+');tasker.setVariable("sig3_voice_prompts_choice",'+json.dumps(prompts)+');tasker.setVariable("SIG3_WakeEnabled","1");run();tasker.vars.clear();tasker.setVariable("sig3_voice_pref_mode","load");run();'
  cases.append(('saved pair survives new globals',setup,results,prompts))
checks='''tasker.setVariable("SIG3_VoiceResponses","1");tasker.setVariable("SIG3_VoicePrompts","0");tasker.setVariable("SIG3_WakeEnabled","1");tasker.setVariable("sig3_voice_pref_mode","save");tasker.setVariable("sig3_voice_results_choice","0");tasker.setVariable("sig3_voice_prompts_choice","1");context.prefs.writable=false;failed=false;try{run();}catch(Exception e){failed=true;}if(!failed||!context.prefs.data.isEmpty()||!tasker.getVariable("SIG3_VoiceResponses").equals("1")||!tasker.getVariable("SIG3_VoicePrompts").equals("0")||!tasker.getVariable("SIG3_WakeEnabled").equals("1"))throw new RuntimeException("failed save changed preferences");context.prefs.writable=true;tasker.setVariable("sig3_voice_prompts_choice","bad");failed=false;try{run();}catch(Exception e){failed=true;}if(!failed||!context.prefs.data.isEmpty())throw new RuntimeException("invalid choice saved");'''
with tempfile.TemporaryDirectory() as d:
 for name,setup,results,prompts in cases:
  script=stub+'run(){'+source+'}'+setup+'if(!tasker.getVariable("SIG3_VoiceResponses").equals('+json.dumps(results)+')||!tasker.getVariable("SIG3_VoicePrompts").equals('+json.dumps(prompts)+'))throw new RuntimeException("wrong preferences");print("PASS");'
  f=Path(d)/'prefs.bsh';f.write_text(script);r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True);assert r.stdout.strip()=='PASS',(name,r.stdout,r.stderr)
 f.write_text(stub+'run(){'+source+'}'+checks+'print("PASS");');r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True);assert r.stdout.strip()=='PASS',r.stdout+r.stderr
for results in ['0','1']:
 for prompts in ['0','1']:
  p=Phone(9);p.globals.update(SIG3_VoiceResponses=results,SIG3_VoicePrompts=prompts,SIG3_WakeEnabled='0');p.prompt_response='current program';p.run('SIG3_VoiceCommand')
  assert p.globals['SIG3_CommandOK']=='1' and not p.drags
  assert ('Sig here' in getattr(p,'spoken',[]))==(prompts=='1')
  assert ('Voice result' in getattr(p,'spoken',[]))==(results=='1')
p=Phone(9);p.globals.update(SIG3_VoiceResponses='1',SIG3_VoicePrompts='0',SIG3_WakeEnabled='0');p.voice_settings_choice=None;p.run('SIG3_VoiceSettings');assert p.globals['SIG3_VoiceResponses']=='1' and p.globals['SIG3_VoicePrompts']=='0'
p.voice_settings_choice=('0','1');p.run('SIG3_VoiceSettings');assert p.voice_preferences=={'responses':'0','prompts':'1'} and p.globals['SIG3_WakeEnabled']=='0'
print('8 actual preference cases plus invalid/write-failure checks passed; four speech combinations retain command capture; settings Save/Cancel preserve wake state')
