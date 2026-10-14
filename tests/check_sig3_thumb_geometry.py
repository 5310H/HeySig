"""Execute the UI guard's native-progress geometry with separate thumb endpoints."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'tools/sig3_ui_check.java').read_text()
geometry = source[source.index('topText = tasker.getVariable'):source.index('return "verified"')]
stub = '''
class JavaCodeException extends Exception {JavaCodeException(String s){super(s);}}
class Rect {int left=501;int top=652;int right=580;int bottom=2047;int centerX(){return 540;}}
class Range {float current;float getMin(){return 0;}float getMax(){return 15;}float getCurrent(){return current;}}
class Control {Range range=new Range();void getBoundsInScreen(Rect r){}Range getRangeInfo(){return range;}}
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){vars.put(k,v);}}
tasker=new FakeTasker();control=new Control();family="Volume";
setup(){tasker.vars.clear();tasker.setVariable("SIG3_VolumeTrackTopY","695");tasker.setVariable("SIG3_VolumeTrackBottomY","2000");tasker.setVariable("SIG3_VolumeTrackBounds","501,652,580,2047");}
require(ok,message){if(!ok)throw new RuntimeException(message);}
for(level=0;level<=15;level++){
 setup();control.range.current=level;check();require(Integer.parseInt(tasker.getVariable("SIG3_VolumeY"))==Math.round(2000-level*87f),"existing calibration "+level);
 tasker.setVariable("SIG3_VolumeThumbTopY","748");tasker.setVariable("SIG3_VolumeThumbBottomY","1959");check();
 require(Integer.parseInt(tasker.getVariable("SIG3_VolumeY"))==Math.round(1959-level*(1211f/15)),"thumb calibration "+level);
 require(tasker.getVariable("SIG3_VolumeTrackTopY").equals("695")&&tasker.getVariable("SIG3_VolumeTrackBottomY").equals("2000"),"target endpoints retained");
}
for(bad:new String[]{"NaN","Infinity","600","2100","1959"}){setup();tasker.setVariable("SIG3_VolumeThumbTopY",bad);tasker.setVariable("SIG3_VolumeThumbBottomY","1959");rejected=false;try{check();}catch(Exception e){rejected=true;}require(rejected,"invalid thumb endpoint "+bad);}
setup();tasker.setVariable("SIG3_VolumeThumbTopY","748");rejected=false;try{check();}catch(Exception e){rejected=true;}require(rejected,"partial calibration");
setup();tasker.setVariable("SIG3_VolumeThumbTopY","%unset");tasker.setVariable("SIG3_VolumeThumbBottomY","%unset");control.range.current=0;check();require(tasker.getVariable("SIG3_VolumeY").equals("2000"),"unset-variable compatibility");
print("PASS: 32 actual native-progress positions, 6 rejection guards and unset-variable compatibility");
'''
with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / 'thumb.bsh'
    path.write_text('check(){' + geometry + '}\n' + stub)
    result = subprocess.run(['java', '-XX:-UsePerfData', '-cp', '/usr/share/java/bsh.jar', 'bsh.Interpreter', str(path)],
                            capture_output=True, text=True, check=True)
    assert 'PASS:' in result.stdout, result.stdout + result.stderr
    print(result.stdout.strip())
