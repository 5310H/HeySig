"""Verify listener handoff, cancellation cleanup and wake-only dispatch."""
import json,subprocess,tempfile,xml.etree.ElementTree as E
from pathlib import Path
from check_sig3_migration import phone
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_wake_trigger.java').read_text()
profile=E.parse(root/'projects/HeySig3.prj.xml').find('Profile')
assert profile.findtext('Event/Bundle/Vals/configregexsub')=='true'
assert profile.findtext('Event/Bundle/Vals/configexactsub')=='false', 'Exact Command disables regex in AutoVoice'

stub='class Tasker {java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}}tasker=new Tasker();'
cases=[({'SIG3_WakeEnabled':'1','par1':'hey cig'},True),({'SIG3_WakeEnabled':'1','par1':'hey cig volume 10'},False),({'SIG3_WakeEnabled':'1','par1':'Hey Sig'},True),({'SIG3_WakeEnabled':'1','avcommnofilter':'hey sig!'},True),({'SIG3_WakeEnabled':'0','par1':'hey sig'},False),({'SIG3_WakeEnabled':'1','SIG3_VoiceBusy':'1','par1':'hey sig'},False),({'SIG3_WakeEnabled':'1','TRUN':',SIG3_Worker,','par1':'hey sig'},False),({'SIG3_WakeEnabled':'1','par1':'hey sig volume 10'},False),({'SIG3_WakeEnabled':'1','par1':'volume 10'},False)]
for variables,accepted in cases:
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/'wake.bsh';setup=''.join('tasker.setVariable('+json.dumps(k)+','+json.dumps(v)+');' for k,v in variables.items());f.write_text(stub+setup+'check(){'+source+'}check();if(!tasker.getVariable("sig3_wake_accepted").equals('+json.dumps('1' if accepted else '0')+'))throw new RuntimeException("wrong acceptance");print("PASS");')
  r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True);assert r.stdout.strip()=='PASS',r.stdout+r.stderr
for phrase in ['current program','','nonsense']:
 p=phone();p.run('SIG3_WakeEnable');assert p.globals['SIG3_WakeEnabled']=='1'
 p.prompt_response=phrase;p.retry_choices=['cancel'];p.run('SIG3_WakeTrigger','Hey Sig')
 assert p.continuous_calls==[True,False,True] and p.continuous_active
 assert p.globals['SIG3_VoiceBusy']=='0' and p.globals['SIG3_VoiceReady']=='0'
 p.run('SIG3_WakeDisable');assert not p.continuous_active and p.globals['SIG3_WakeEnabled']=='0'
p=phone();p.globals['SIG3_WakeEnabled']='1';p.continuous_failure='stop';p.run('SIG3_VoiceCommand');assert not getattr(p,'spoken',[]) and p.globals['SIG3_VoiceBusy']=='0'
p=phone();p.globals['SIG3_WakeEnabled']='1';p.continuous_failure='start';p.prompt_response='';p.run('SIG3_VoiceCommand');assert p.globals['SIG3_WakeEnabled']=='0' and p.globals['SIG3_VoiceBusy']=='0'
p=phone();p.globals['SIG3_WakeEnabled']='1';p.voice_capture_hook=lambda: p.run('SIG3_WakeDisable');p.prompt_response='';p.run('SIG3_VoiceCommand');assert p.continuous_calls==[False,False] and not p.continuous_active
p=phone();p.globals['SIG3_WakeEnabled']='1';before=p.globals.get('SIG3_OperationId');p.run('SIG3_AutoVoiceCommand','volume 10');assert not p.drags and p.globals.get('SIG3_OperationId')==before
p=phone();p.globals.update(SIG3_WakeEnabled='1',SIG3_VoiceBusy='1');p.run('SIG3_WakeTrigger','Hey Sig');assert not getattr(p,'continuous_calls',[])
for entry in ['SIG3_WakeEnable','SIG3_VoiceCommand']:
 p=phone();p.globals['SIG3_WakeEnabled']='1';p.prompt_response=''
 def disable_during_start(enabled):
  if enabled:
   p.continuous_hook=None;p.run('SIG3_WakeDisable')
 p.continuous_hook=disable_during_start;p.run(entry)
 assert p.globals['SIG3_WakeEnabled']=='0' and not p.continuous_active
print('9 actual wake-phrase cases passed; listener pauses/resumes, cancels cleanly, respects disable and blocks direct continuous commands')
