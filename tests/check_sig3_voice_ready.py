"""Execute the readiness preflight and verify speech precedes capture."""
import subprocess,tempfile,json,xml.etree.ElementTree as E
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_voice_ready.java').read_text()
for name in ['android.content.pm.PackageManager','android.app.NotificationManager','android.media.AudioManager']:source=source.replace('import '+name+';','')
stub="""class PackageManager{static int PERMISSION_GRANTED=0;}class AudioManager{static int STREAM_MUSIC=3;static int MODE_NORMAL=0;}
class NotificationManager{static int INTERRUPTION_FILTER_ALL=1;int filter=1;int getCurrentInterruptionFilter(){return filter;}}
class Power{boolean interactive=true;boolean isInteractive(){return interactive;}}class Keyguard{boolean locked=false;boolean isKeyguardLocked(){return locked;}}
class Audio{int volume=17;int mode=0;boolean muted=false;int releaseAfter=0;boolean isStreamMute(int stream){if(releaseAfter>0){releaseAfter--;return true;}return muted;}int getStreamVolume(int stream){return volume;}int getMode(){return mode;}}
class Context{Power power=new Power();Keyguard keyguard=new Keyguard();Audio audio=new Audio();NotificationManager notification=new NotificationManager();int permission=0;Object getSystemService(String n){if(n.equals("power"))return power;if(n.equals("keyguard"))return keyguard;if(n.equals("audio"))return audio;return notification;}int checkSelfPermission(String p){return permission;}}
class Tasker{java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}void showToast(String s){}}
context=new Context();tasker=new Tasker();"""
cases=[('context.keyguard.locked=true;tasker.setVariable("SIG3_VoicePrompts","0");',False,False),('context.keyguard.locked=true;context.notification.filter=2;',False,False),('tasker.setVariable("SIG3_WakeEnabled","1");context.audio.releaseAfter=3;',True,True),('tasker.setVariable("SIG3_WakeEnabled","1");context.audio.muted=true;',True,False),('context.audio.muted=true;',True,False),('tasker.setVariable("SIG3_VoiceResponses","0");tasker.setVariable("SIG3_VoicePrompts","1");',True,True),('tasker.setVariable("SIG3_VoiceResponses","1");tasker.setVariable("SIG3_VoicePrompts","0");',True,False),('',True,True),('tasker.setVariable("SIG3_VoiceResponses","0");',True,False),('context.audio.volume=0;',True,False),('context.audio.mode=2;',True,False),('context.notification.filter=2;',True,False),('context.keyguard.locked=true;',False,'Unlock the phone, then say Hey Sig again.'),('context.power.interactive=false;',False,'Unlock the phone, then say Hey Sig again.'),('context.permission=-1;',False,False),('tasker.setVariable("TRUN","SIG3_Worker,SIG3_VoiceCommand");',False,False)]
for setup,allowed,spoken in cases:
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/'ready.bsh';f.write_text(stub+setup+'run(){'+source+'}run();if(!tasker.getVariable("SIG3_VoiceCaptureAllowed").equals('+json.dumps('1' if allowed else '0')+'))throw new RuntimeException("capture");if(!tasker.getVariable("sig3_ready_speech").equals('+json.dumps(spoken if isinstance(spoken,str) else 'Sig here' if spoken else '')+'))throw new RuntimeException("speech");print("PASS");')
  r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True);assert r.stdout.strip()=='PASS',r.stdout+r.stderr
print(str(len(cases))+' actual readiness cases passed: preference, DND, volume, lock, permission and busy worker')
t=E.parse(root/'tasks/SIG3_VoiceSession.tsk.xml').find('Task');aa=sorted(t.findall('Action'),key=lambda a:int(a.get('sr')[3:]));capture=next(i for i,a in enumerate(aa) if a.findtext('code')=='903');speech=next(i for i,a in enumerate(aa) if a.findtext('code')=='559')
assert speech<capture and aa[speech].find("Int[@sr='arg7']").get('val')=='0'
assert aa[speech].find("Int[@sr='arg2']").get('val')=='3'
assert any(a.findtext('code')=='30' for a in aa[speech:capture])
print('Readiness speech waits, uses media and settles before microphone capture; loop repeats cue on Try again')
