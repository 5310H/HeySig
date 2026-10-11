"""Result formatting for missing optional values and concrete failures."""
from pathlib import Path
from heysig3_runtime import Phone
for task in ('SIG3_ProgramCurrent','SIG3_VolumeCurrent','SIG3_BalanceCurrent','SIG3_TinnitusCurrent'):
    p=Phone(0);p.globals['SIG3_KnobId']='volume-knob'
    p.globals['SIG3_BalanceKnobId']='volume-knob';p.globals['SIG3_TinnitusKnobId']='volume-knob'
    p.run(task)
    assert p.globals['SIG3_CommandOK']=='1',(task,p.globals)
    assert '%' not in p.globals['SIG3_Result'],p.globals['SIG3_Result']
p=Phone(0);p.run('SIG3_Worker','Wrong,Set,')
assert p.globals['SIG3_CommandOK']=='0' and '%' not in p.globals['SIG3_Result']
assert p.globals['SIG3_Result'].startswith('Failed:')
print('Read-only results omit unresolved optional values; failures remain concrete')

# Execute the actual BeanShell helper, not just the control-flow model.
import subprocess, tempfile
source=(Path(__file__).resolve().parents[1]/'tools/sig3_report.java').read_text()
with tempfile.TemporaryDirectory() as d:
    f=Path(d)/'report.bsh'
    stub='class FakeTasker { java.util.Map values=new java.util.HashMap(); String getVariable(String n) {return (String)values.get(n);} void setVariable(String n,String v){values.put(n,v);} void log(String s){} void showToast(String s){} } tasker=new FakeTasker();'
    cases=[('1','%par1','',False),('0','%sig3_request3','',True),('0','1','Low volume',True)]
    for ok,target,error,failed in cases:
        setup='tasker.setVariable("SIG3_CommandOK","'+ok+'");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("SIG3_Observed","0");tasker.setVariable("SIG3_Target","'+target+'");tasker.setVariable("SIG3_Error","'+error+'");'
        # Top-level return is scoped inside a function so assertions execute.
        tail='result=tasker.getVariable("SIG3_Result"); if(result.indexOf("%")>=0 || result.startsWith("Failed:")!='+str(failed).lower()+') throw new RuntimeException(result); print("Actual BeanShell result passed: "+result);'
        f.write_text(stub+setup+'report(){'+source+'} report();'+tail)
        out=subprocess.run(['java','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(f)],capture_output=True,text=True,check=True)
        assert 'Actual BeanShell result passed:' in out.stdout,out.stdout+out.stderr
        print(out.stdout.strip())
