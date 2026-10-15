"""Execute actual Signia page recovery against modeled accessibility trees."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'tools/sig3_program_picker.java').read_text()
source = source.replace('android.os.SystemClock.sleep(150);', '')
stub = '''
class JavaCodeException extends RuntimeException {JavaCodeException(String s){super(s);}}
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}}
class Node {
 String text="",description="",id="",pkg="com.signia.rta";java.util.List children=new java.util.ArrayList();
 boolean visible=true,enabled=true;
 String getPackageName(){return pkg;}String getText(){return text;}String getContentDescription(){return description;}String getViewIdResourceName(){return id;}
 boolean isVisibleToUser(){return visible;}boolean isEnabled(){return enabled;}int getChildCount(){return children.size();}Node getChild(int i){return (Node)children.get(i);}
}
class Service {Node root,next;int backs=0;boolean allow=true;Node getRootInActiveWindow(){return root;}boolean performGlobalAction(int action){backs++;if(allow)root=next;return allow;}}
tasker=new FakeTasker();tasker.vars.put("SIG3_ProgramName1","Universal");tasker.vars.put("SIG3_ProgramName2","Sleep");tasker.vars.put("SIG3_ProgramId","program");tasker.vars.put("SIG3_BatteryPageId","battery");
node(text,description,id){n=new Node();n.text=text;n.description=description;n.id=id;return n;}
picker(){r=new Node();r.children.add(node("Programs","",""));r.children.add(node("Sleep","Sleep Selected Button",""));return r;}
controls(name){r=new Node();r.children.add(node(name,"Hearing program "+name+" Active","program"));return r;}
require(ok,message){if(!ok)throw new RuntimeException(message);}
'''
cases = '''
s=new Service();s.root=controls("Sleep");require(prepareProgramRead(s)==s.root&&s.backs==0,"Controls must not navigate");
s=new Service();s.root=picker();s.next=controls("Sleep");require(controlsLabel(prepareProgramRead(s)).equals("Sleep")&&s.backs==1,"Picker returns to verified Controls");
s=new Service();s.root=new Node();s.root.children.add(node("Battery","","battery"));s.next=controls("Universal");require(controlsLabel(prepareProgramRead(s)).equals("Universal")&&s.backs==1,"Battery page returns to Controls");
s=new Service();s.root=new Node();require(prepareProgramRead(s)==s.root&&s.backs==0,"Unknown page must not navigate");
s=new Service();s.root=picker();s.root.children.add(node("Universal","Universal Selected Button",""));failed=false;try{prepareProgramRead(s);}catch(Exception e){failed=true;}require(failed&&s.backs==0,"Ambiguous picker must not navigate");
s=new Service();s.root=picker();s.next=controls("Universal");failed=false;try{prepareProgramRead(s);}catch(Exception e){failed=true;}require(failed,"Changed selection must fail");
s=new Service();s.root=picker();s.allow=false;failed=false;try{prepareProgramRead(s);}catch(Exception e){failed=true;}require(failed,"Rejected Back must fail");
s=new Service();s.root=picker();s.next=new Node();failed=false;try{prepareProgramRead(s);}catch(Exception e){failed=true;}require(failed,"Missing Controls must fail");
s=new Service();s.root=picker();s.root.pkg="other.app";failed=false;try{prepareProgramRead(s);}catch(Exception e){failed=true;}require(failed&&s.backs==0,"Other app must not navigate");
print("PASS: nine actual page recovery and rejection cases");
'''
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / 'pages.bsh'
    path.write_text(stub + source + cases)
    result = subprocess.run(['java', '-XX:-UsePerfData', '-cp', '/usr/share/java/bsh.jar',
                             'bsh.Interpreter', str(path)], capture_output=True, text=True)
    assert result.returncode == 0 and 'PASS:' in result.stdout, result.stdout + result.stderr
    print(result.stdout.strip())
