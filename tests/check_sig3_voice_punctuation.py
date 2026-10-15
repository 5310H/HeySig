"""Sentence punctuation routes supported commands without broadening targets."""
import json
from pathlib import Path
import subprocess
import tempfile
from heysig3_runtime import Phone

ROOT = Path(__file__).resolve().parents[1]
for suffix in ('.', '!', '?'):
    for command, family, target in [('volume ten', 'Volume', 10),
                                     ('balance minus three', 'Balance', -3),
                                     ('tinnitus one', 'Tinnitus', 1)]:
        p = Phone(2, bounds=(-8, 7) if family == 'Balance' else (0, 15))
        p.run('SIG3_Init')
        p.globals.update(SIG3_KnobId='volume-knob', SIG3_BalanceKnobId='volume-knob',
                         SIG3_TinnitusKnobId='volume-knob')
        p.globals['SIG3_' + family + 'StepPx'] = '40'
        p.globals['SIG3_' + family + 'Direction'] = '1'
        p.run('SIG3_VoiceRouter', command + suffix)
        assert p.level == target and p.globals['SIG3_Family'] == family
        assert p.globals['SIG3_CommandOK'] == '1'
    p = Phone(2)
    p.globals['SIG3_KnobId'] = 'volume-knob'
    p.run('SIG3_VoiceRouter', 'current volume' + suffix)
    assert p.level == 2 and not p.gestures and p.globals['SIG3_CommandOK'] == '1'
for command in ('volume 1.5', 'volume ten!!', 'volume ten extra', 'volume sixteen.'):
    p = Phone(2)
    p.run('SIG3_VoiceRouter', command)
    assert p.level == 2 and not p.gestures and p.globals['SIG3_VoiceMatched'] == '0'

# Execute the Java normalizer itself, including punctuation-bearing program names.
source = (ROOT / 'tools/sig3_command_normalize.java').read_text()
source = source.replace('import com.joaomgcd.taskerm.action.java.JavaCodeException;', '')
stub = '''class JavaCodeException extends RuntimeException {JavaCodeException(String s){super(s);}}
class FakeTasker {java.util.Map values=new java.util.HashMap();
String getVariable(String n){return (String)values.get(n);}
void setVariable(String n,String v){values.put(n,v);}} tasker=new FakeTasker();'''
with tempfile.TemporaryDirectory() as folder:
    for text, expected in [('current tin.', 'current tinnitus.'),
                           ('normal!', 'program 1'), ('program noisy?', 'program 3'),
                           ('awake.', 'wake'), ('program Music!', 'program Music!')]:
        path = Path(folder) / 'normalize.bsh'
        path.write_text(stub + 'tasker.setVariable("SIG3_ModeConversationProgram","1");'
                        'tasker.setVariable("SIG3_ModeNoisyProgram","3");'
                        'tasker.setVariable("sig3_command",' + json.dumps(text) + ');'
                        'normalize(){' + source + '} normalize();'
                        'if(!tasker.getVariable("sig3_command").equals(' + json.dumps(expected) +
                        '))throw new RuntimeException("Wrong normalization");print("PASS");')
        result = subprocess.run(['java', '-XX:-UsePerfData', '-cp', '/usr/share/java/bsh.jar',
                                 'bsh.Interpreter', str(path)], capture_output=True, text=True)
        assert result.returncode == 0 and 'PASS' in result.stdout, result.stdout + result.stderr
print('Voice punctuation: routing, invalid targets and actual Java normalization passed')
