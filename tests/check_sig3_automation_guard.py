"""Check that blocked automation preserves its reason even when Tasker aborts Java."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_automation_guard.java').read_text().replace('import com.joaomgcd.taskerm.action.java.JavaCodeException;','').replace('new JavaCodeException(', 'new Exception(')
stub='''
class Root {String name="com.signia.rta";String getPackageName(){return name;}}
class Service {Root root=new Root();Root getRootInActiveWindow(){return root;}}
class Tasker {java.util.Map vars=new java.util.HashMap();Service service=new Service();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){vars.put(k,v);}Service getAccessibilityService(){return service;}}
tasker=new Tasker();
require(ok,message){if(!ok)throw new Exception(message);}
require(operation().equals("allowed"),"foreground allowed");
for(key:new String[]{"SIG3_ManualOverride","SIG3_AutomationCancelled"}){tasker.setVariable(key,"1");blocked=false;try{operation();}catch(Exception e){blocked=true;}require(blocked&&tasker.getVariable("SIG3_Error").length()>0,"blocked reason preserved "+key);tasker.setVariable(key,"0");}
tasker.service.root.name="another.app";blocked=false;try{operation();}catch(Exception e){blocked=true;}
require(blocked&&tasker.getVariable("SIG3_Error").equals("Automatic change deferred until Signia is foreground"),"foreground reason preserved");
tasker.setVariable("SIG3_DeferAutomation","0");require(operation().equals("allowed"),"explicit foreground deferral off");
tasker.setVariable("SIG3_DeferAutomation","1");tasker.service=null;blocked=false;try{operation();}catch(Exception e){blocked=true;}require(blocked,"missing service blocked");
print("PASS: automation foreground/override/cancel guards retain failure reasons before abort");
'''
with tempfile.TemporaryDirectory() as folder:
 p=Path(folder)/'guard.bsh';p.write_text('operation(){'+source+'}\n'+stub)
 r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(p)],capture_output=True,text=True,check=True)
 assert 'PASS:' in r.stdout,r.stdout+r.stderr
 print(r.stdout.strip())
