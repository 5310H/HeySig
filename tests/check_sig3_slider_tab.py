"""Execute tab coordinate, selection and availability bodies against accessibility stubs."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'tools/sig3_slider_tab.java').read_text()
source = source[source.index('try {'):]
source = source.replace('JavaCodeException', 'Exception').replace('android.graphics.Rect', 'FakeRect')
source = source.replace('GestureDescription.StrokeDescription', 'FakeStroke').replace('Build.VERSION.SDK_INT', 'tasker.sdk').replace('java.lang.Thread.sleep(3000)', 'java.lang.Thread.sleep(1)')

stub = '''
class FakeRect {
 int left=698, top=2130, right=1012, bottom=2298;
 int centerX(){return (left+right)/2;} int centerY(){return (top+bottom)/2;}
 boolean isEmpty(){return right<=left || bottom<=top;}
}
class Path {void moveTo(int x,int y){}}
class FakeStroke {FakeStroke(Path p,int start,int duration){}}
class Metrics {int widthPixels=1080, heightPixels=2400;}
class Resources {Metrics getDisplayMetrics(){return new Metrics();}}
class AccessibilityNodeInfo {
 String desc="", pkg="com.signia.rta", text="";
 boolean visible=true, enabled=true;
 int left=698, top=2130, right=1012, bottom=2298;
 java.util.List children=new java.util.ArrayList();
 String getText(){return text;}
 String getPackageName(){return pkg;}
 boolean forbidDescription=false; String getContentDescription(){if(forbidDescription)throw new RuntimeException("Unexpected tab search");return desc;}
 boolean isVisibleToUser(){return visible;}
 boolean isEnabled(){return enabled;}
 int getChildCount(){return children.size();}
 AccessibilityNodeInfo getChild(int i){return (AccessibilityNodeInfo)children.get(i);}
 void getBoundsInScreen(FakeRect r){r.left=left;r.top=top;r.right=right;r.bottom=bottom;}
}
class FakeService {
 AccessibilityNodeInfo root; int taps=0,calls=0;boolean accepted=true,moveOnSecond=false,selectOnSecond=false,hideOnSecond=false;
 AccessibilityNodeInfo getRootInActiveWindow(){calls++;if(calls==2 && root.children.size()>0){n=(AccessibilityNodeInfo)root.children.get(0);if(moveOnSecond)n.left=540;if(selectOnSecond)n.desc="Selected "+n.desc;if(hideOnSecond)n.visible=false;}return root;}
 Resources getResources(){return new Resources();}
}
class FakeTasker {
 FakeService service=new FakeService(); String error="", family="Volume";
 int sdk=26;java.util.Map vars=new java.util.HashMap();
 String getVariable(String k){return family;}
 FakeService getAccessibilityService(){return service;}
 void setVariable(String k,String v){vars.put(k,v);if(k.equals("SIG3_Error"))error=v;}
}
performTabDoubleTap(service,first,second,phase){service.taps++;if(!service.accepted)throw new Exception("rejected");tabNode.desc="Selected "+tabNode.desc;}
tasker=new FakeTasker();
rootNode=new AccessibilityNodeInfo(); tabNode=new AccessibilityNodeInfo();
tabNode.desc="Volume Tab";
rootNode.children.add(tabNode); tasker.service.root=rootNode;
'''
cases = [
    ('three tab volume', 'tabNode.left=42;tabNode.right=357;', True, '199,2214'),
    ('two tab volume', 'tabNode.left=42;tabNode.right=514;', True, '278,2214'),
    ('three tab balance', 'tasker.family="Balance";tabNode.desc="Sound Sharpness Tab";', True, '855,2214'),
    ('two tab balance', 'tasker.family="Balance";tabNode.desc="Sound Sharpness Tab";tabNode.left=540;', True, '776,2214'),
    ('tinnitus', 'tasker.family="Tinnitus";tabNode.desc="Tinnitus Signal Tab";tabNode.left=370;tabNode.right=685;', True, '527,2214'),
    ('live label target', 'labelNode=new AccessibilityNodeInfo();labelNode.text="Volume";labelNode.left=216;labelNode.top=2231;labelNode.right=340;labelNode.bottom=2280;tabNode.left=42;tabNode.right=514;tabNode.children.add(labelNode);', True, '278,2255'),
    ('selected', 'tabNode.desc="Selected Volume Tab";', True, 'null,null'),
    ('missing', 'rootNode.children.clear();', False, 'null,null'),
    ('ambiguous', 'rootNode.children.add(tabNode);', False, 'null,null'),
    ('hidden', 'tabNode.visible=false;', False, 'null,null'),
    ('disabled', 'tabNode.enabled=false;', False, 'null,null'),
    ('wrong app', 'rootNode.pkg="other.app";', False, 'null,null'),
    ('unknown family', 'tasker.family="Other";', False, 'null,null'),
    ('layout changes while settling', 'tasker.family="Balance";tabNode.desc="Sound Sharpness Tab";tasker.service.moveOnSecond=true;', True, '776,2214'),
    ('selected while settling', 'tasker.service.selectOnSecond=true;', True, 'null,null'),
    ('hidden while settling', 'tasker.service.hideOnSecond=true;', False, 'null,null'),
    ('old Android', 'tasker.sdk=23;', False, 'null,null'),
    ('rejected activation', 'tasker.service.accepted=false;', False, '855,2214'),
    ('outside display', 'tabNode.right=1100;', False, 'null,null'),
]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'tab.bsh'
    for name, setup, success, coordinates in cases:
        script = stub + setup + '\nselectTab(){\n' + source + '\n}\n'
        script += 'ok=true;try {selectTab();}catch(Exception failure){ok=false;}\n'
        script += 'print(ok+":"+tasker.vars.get("sig3_tab_x")+","+tasker.vars.get("sig3_tab_y"));\n'
        path.write_text(script)
        result = subprocess.run(['java', '-cp', '/usr/share/java/bsh.jar', 'bsh.Interpreter', str(path)], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == f'{str(success).lower()}:{coordinates}', (name, result.stdout, result.stderr)
print(f'{len(cases)} actual BeanShell tab coordinate cases passed, including two and three tabs')

verify = (root / 'tools/sig3_slider_tab_verify.java').read_text()
verify = verify[verify.index('try {'):].replace('JavaCodeException', 'Exception')
cases = [('selected', 'tabNode.desc="Selected Volume Tab";', True),
         ('not selected', '', False),
         ('hidden selection', 'tabNode.desc="Selected Volume Tab";tabNode.visible=false;', False),
         ('ambiguous selection', 'tabNode.desc="Selected Volume Tab";rootNode.children.add(tabNode);', False),
         ('foreground lost', 'rootNode.pkg="other.app";', False)]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'verify.bsh'
    for name, setup, success in cases:
        path.write_text(stub + setup + '\nverifyTab(){\n' + verify + '\n}\nok=true;try{verifyTab();}catch(Exception failure){ok=false;}print(ok);\n')
        result = subprocess.run(['java', '-cp', '/usr/share/java/bsh.jar', 'bsh.Interpreter', str(path)], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == str(success).lower(), (name, result.stdout, result.stderr)
print('5 actual BeanShell selected-tab verification cases passed')

availability = (root / 'tools/sig3_tinnitus_available.java').read_text()
availability = availability[availability.index('tasker.setVariable'):].replace('JavaCodeException', 'Exception')
cases = [('Universal', '\\uE912', True, True, '1'),
         ('TV', '\\uE909', False, True, '0'),
         ('Universal missing tab', '\\uE912', False, True, '1'),
         ('TV conflicting tab', '\\uE909', True, True, '0'),
         ('unknown with tab', '?', True, True, '1'),
         ('unknown without tab', '?', False, True, '0')]
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'available.bsh'
    for name, glyph, has_tab, success, available in cases:
        setup = 'rootNode.desc="Hearing program Test Active";iconNode=new AccessibilityNodeInfo();iconNode.text="'+glyph+'";rootNode.children.add(iconNode);'
        if glyph in ('\\uE912', '\\uE909'): setup += 'tabNode.forbidDescription=true;'
        setup += 'tabNode.desc="Tinnitus Signal Tab";' if has_tab else 'tabNode.desc="Volume Tab";'
        path.write_text(stub + setup + '\navailable(){\n' + availability + '\n}\nok=true;try{available();}catch(Exception failure){ok=false;}print(ok+":"+tasker.vars.get("SIG3_TinnitusAvailable"));\n')
        result = subprocess.run(['java', '-cp', '/usr/share/java/bsh.jar', 'bsh.Interpreter', str(path)], capture_output=True, text=True, check=True)
        assert result.stdout.strip() == str(success).lower()+':'+available, (name, result.stdout, result.stderr)
print('6 actual BeanShell program icon and tinnitus availability cases passed')
