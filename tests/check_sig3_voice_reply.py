"""Execute the actual spoken-result formatter in BeanShell."""
from pathlib import Path
import json
import subprocess
import tempfile
import xml.etree.ElementTree as E

root = Path(__file__).resolve().parents[1]
source = (root / 'tools/sig3_voice_reply.java').read_text()
base = dict(SIG3_OperationId='new',sig3_reply_before='old',SIG3_CommandOK='1',
            SIG3_MoveStage='complete',SIG3_Family='Program',SIG3_Program='My custom program')
cases = [
    ({}, 'Program is My custom program.'),
    ({'SIG3_Family':'Volume','SIG3_Observed':'3'}, 'Volume is 3.'),
    ({'SIG3_Family':'Balance','SIG3_Observed':'-3'}, 'Balance is minus 3.'),
    ({'SIG3_Family':'Tinnitus','SIG3_Observed':'0'}, 'Tinnitus is 0.'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'Turn off Do Not Disturb'}, 'Turn off Do Not Disturb.'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'Raise phone media volume'}, 'Raise phone media volume.'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'Raise phone media volume with the phone volume slider to at least 13/25 (50% minimum), then retry'}, 'Raise phone media volume to halfway.'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'Raise phone ring volume with the phone volume slider to at least 18/25 (70% minimum), then retry'}, 'Raise phone ring volume.'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'Tinnitus unavailable for this program'}, 'Command stopped. Tinnitus unavailable for this program'),
    ({'SIG3_CommandOK':'0','SIG3_Error':'%SIG3_Error'}, 'Command did not complete. Check the phone screen.'),
    ({'SIG3_OperationId':'old'}, 'Command was not accepted. Please try again when the current command finishes.'),
    ({'SIG3_MoveStage':'start'}, 'Command result could not be verified. Check the phone screen.'),
    ({'SIG3_Family':'Battery'}, 'Battery checks requested. Listen for the hearing aid indications.'),
    ({'sig3_reply_kind':'retry'}, 'Command not recognized. Tap Try again to speak again, or Cancel.'),
    ({'SIG3_VoiceResponses':'0'}, ''),
    ({'TRUN':',SIG3_VoiceCommand,SIG3_Worker,'}, ''),
]
stub='class FakeTasker { java.util.Map values=new java.util.HashMap(); String getVariable(String n){return (String)values.get(n);} void setVariable(String n,String v){values.put(n,v);} } tasker=new FakeTasker();'
with tempfile.TemporaryDirectory() as d:
    for changes, expected in cases:
        setup=''.join('tasker.setVariable('+json.dumps(k)+','+json.dumps(v)+');' for k,v in (base|changes).items())
        f=Path(d)/'voice.bsh'
        f.write_text(stub+setup+'format(){'+source+'} format();'+
                     'reply=tasker.getVariable("sig3_speech"); if (!reply.equals('+json.dumps(expected)+')) throw new RuntimeException(reply); print("PASS");')
        out=subprocess.run(['java','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True)
        assert 'PASS' in out.stdout,out.stdout+out.stderr

task=E.parse(root/'tasks/SIG3_VoiceCommand.tsk.xml').getroot().find('Task')
actions=task.findall('Action')
for i,a in enumerate(actions):
    if a.findtext('code')=='559':
        assert a.find("Int[@sr='arg2']").get('val')=='3'  # Media stream, no volume change.
        assert a.find("Int[@sr='arg7']").get('val')=='0'  # Wait until speech ends.
        assert a.find("Int[@sr='arg6']").get('val')=='0'  # Offline/default engine.
        assert any(x.findtext('code')=='30' for x in actions[max(0,i-3):i])
print(f'{len(cases)} actual BeanShell spoken-result cases passed; Say waits, uses media and follows a settling delay.')
