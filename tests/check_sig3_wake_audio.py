"""Execute media preservation against actual helper source and audio changes."""
import subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_wake_audio.java').read_text().replace('import android.media.AudioManager;','').replace('com.joaomgcd.taskerm.action.java.JavaCodeException','RuntimeException')
stub='''class AudioManager {static int STREAM_MUSIC=3;static int ADJUST_UNMUTE=100;}
class Audio {int level=17;int maximum=25;boolean muted=false;int writes=0;int getStreamVolume(int s){return level;}int getStreamMaxVolume(int s){return maximum;}boolean isStreamMute(int s){return muted;}void setStreamVolume(int s,int v,int f){level=v;writes++;}void adjustStreamVolume(int s,int d,int f){muted=false;}}
class Context {Audio audio=new Audio();Object getSystemService(String n){return audio;}}
class Tasker {java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}}
context=new Context();tasker=new Tasker();'''
cases=[
 ('tasker.setVariable("sig3_wake_audio_mode","capture");', 'if(!"17".equals(tasker.getVariable("SIG3_WakeMediaLevel")))throw new RuntimeException("capture");'),
 ('tasker.setVariable("sig3_wake_audio_mode","restore");tasker.setVariable("SIG3_WakeMediaLevel","17");context.audio.level=0;context.audio.muted=true;', 'if(context.audio.level!=17||context.audio.muted)throw new RuntimeException("restore");'),
 ('tasker.setVariable("sig3_wake_audio_mode","restore");tasker.setVariable("SIG3_WakeMediaLevel","0");context.audio.level=8;', 'if(context.audio.level!=0)throw new RuntimeException("saved mute");'),
 ('tasker.setVariable("sig3_wake_audio_mode","restore");', 'if(context.audio.writes!=0)throw new RuntimeException("no snapshot");'),
 ('tasker.setVariable("sig3_wake_audio_mode","restore");tasker.setVariable("SIG3_WakeMediaLevel","17");', 'if(context.audio.writes!=0)throw new RuntimeException("unchanged");'),
]
for setup,check in cases:
 with tempfile.TemporaryDirectory() as d:
  f=Path(d)/'audio.bsh';f.write_text(stub+setup+'run(){'+source+'}run();'+check+'print("PASS");')
  r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True)
  assert r.stdout.strip()=='PASS',r.stdout+r.stderr
print('5 actual wake audio cases passed: capture, suppression recovery, saved mute, missing snapshot and unchanged level')
