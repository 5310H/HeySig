"""Execute the actual Java audio policy, including fractional volume boundaries."""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as E
ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'tools/sig3_phone_check.java').read_text()
policy = source.split('/* BEGIN AUDIO POLICY')[1].split('*/', 1)[1].split('/* END AUDIO POLICY')[0]
java = '''public class AudioPolicyTest {
static class NotificationManager { static final int INTERRUPTION_FILTER_ALL=1; }
static class AudioManager { static final int RINGER_MODE_SILENT=0, RINGER_MODE_NORMAL=2; }
static class JavaCodeException extends RuntimeException { JavaCodeException(String m) {super(m);} }
static String check(String streamName,int volume,int maximum,int filter,int ringer,int minimumPercent) {
int required=(maximum*minimumPercent+99)/100;
try { POLICY return "ready"; } catch(JavaCodeException e) {return e.getMessage();}
}
public static void main(String[] args) {
int cases=0;
for(String stream:new String[]{"media","ring"}) {
for(int filter:new int[]{0,2,3,4}) {
if(!check(stream,14,25,filter,2,50).contains("Do Not Disturb")) throw new AssertionError(); cases++;
}
if(!check(stream,12,25,1,2,50).contains("13/25")) throw new AssertionError(); cases++;
if(!check(stream,13,25,1,2,50).equals("ready")) throw new AssertionError(); cases++;
if(!check(stream,0,25,1,2,50).contains("Raise phone")) throw new AssertionError(); cases++;
if(!check(stream,14,25,1,0,50).contains("Unmute")) throw new AssertionError(); cases++;
if(!check(stream,19,25,1,2,80).contains("20/25")) throw new AssertionError(); cases++;
}
if(!check("media",14,25,1,1,50).equals("ready")) throw new AssertionError(); cases++;
if(!check("ring",14,25,1,1,50).contains("vibrate")) throw new AssertionError(); cases++;
System.out.println(cases+" actual Java audio-policy cases passed");
}
}'''.replace('POLICY',policy)
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'AudioPolicyTest.java'; p.write_text(java)
    subprocess.run(['javac',str(p)],check=True)
    subprocess.run(['java','-cp',d,'AudioPolicyTest'],check=True)
assert 'setStreamVolume' not in source and 'setInterruptionFilter' not in source
root=E.parse(ROOT/'tasks/SIG3_PhoneAudioCheck.tsk.xml')
assert not root.findall('.//App')
assert 'SIG3_InternalAppLaunch' not in E.tostring(root.getroot(),encoding='unicode')
battery=E.parse(ROOT/'tasks/SIG3_InternalBatteryCheck.tsk.xml')
actions=sorted(battery.findall('.//Action'),key=lambda a:int(a.get('sr')[3:]))
preflight=next(i for i,a in enumerate(actions) if 'Read-only preflight' in E.tostring(a,encoding='unicode'))
click=next(i for i,a in enumerate(actions) if a.findtext('code')=='107361459')
assert preflight<click
print('Read-only settings and battery preflight ordering passed')

from heysig3_runtime import Phone
for family in ('Volume','Balance','Tinnitus'):
    p=Phone(0, bounds=(-8,7) if family=='Balance' else (0,15), fail_stage='phone')
    selector='SIG3_KnobId' if family=='Volume' else 'SIG3_'+family+'KnobId'
    p.globals.update({selector:'volume-knob','SIG3_'+family+'StepPx':'40','SIG3_'+family+'Direction':'1'})
    p.run('SIG3_'+family+'Set','1')
    assert p.globals['SIG3_CommandOK']=='0' and p.level==0
    assert not p.gestures and not p.progress_actions
p=Phone(0,fail_stage='phone'); p.globals['SIG3_ProgramName2']='Music'
p.run('SIG3_ProgramSwitch','2')
assert p.globals['SIG3_CommandOK']=='0' and p.program==p.programs[0]
p=Phone(0,fail_stage='phone'); p.run('SIG3_BatteryCheck','listen')
assert p.globals['SIG3_CommandOK']=='0'
p=Phone(0,fail_stage='phone'); p.run('SIG3_BatteryCheck','open')
assert p.globals['SIG3_CommandOK']=='1'
p=Phone(0); p.globals['SIG3_MinAudioPercent']='80'; p.run('SIG3_Init')
assert p.globals['SIG3_MinAudioPercent']=='80'
print('Preflight failure blocks slider/program/listen operations; read-only battery and configured minimum preserved')
