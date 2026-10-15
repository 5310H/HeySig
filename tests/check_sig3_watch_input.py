"""Execute the actual watch input normalizer, including AutoApps envelopes."""
import json
from pathlib import Path
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'tools/sig3_watch_input.java').read_text()
source = source.replace('com.joaomgcd.taskerm.action.java.JavaCodeException', 'RuntimeException')
stub = '''class FakeTasker {String value;String getVariable(String n){return value;}
void setVariable(String n,String v){if(n.equals("sig3_input"))value=v;}} tasker=new FakeTasker();'''
cases = [('sig3=:=current program.', 'current program.'),
         ('SIG3 =:= current volume', 'current volume'),
         ('sig3 current balance', 'current balance'),
         ('current tin', 'current tin'), ('sig3=:=', None), ('%awmessage', None), ('', None)]
with tempfile.TemporaryDirectory() as folder:
    for value, expected in cases:
        path = Path(folder) / 'watch.bsh'
        check = ('if(!tasker.value.equals(' + json.dumps(expected) + '))throw new RuntimeException("Mismatch");'
                 if expected is not None else 'if(!failed)throw new RuntimeException("Expected rejection");')
        path.write_text(stub + 'tasker.value=' + json.dumps(value) + ';normalize(){' + source +
                        '} failed=false;try{normalize();}catch(Exception e){failed=true;}' +
                        ('if(failed)throw new RuntimeException("Unexpected rejection");' if expected is not None else '') +
                        check + 'print("PASS");')
        result = subprocess.run(['java', '-XX:-UsePerfData', '-cp', '/usr/share/java/bsh.jar',
                                 'bsh.Interpreter', str(path)], capture_output=True, text=True)
        assert result.returncode == 0 and 'PASS' in result.stdout, result.stdout + result.stderr
print('Seven actual Java watch-input normalization and rejection cases passed')
