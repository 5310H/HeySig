"""Execute the actual direct-drag coordinate guards in BeanShell."""
import subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tools/sig3_target_drag.java').read_text()
geometry=source[source.index('x = Float.parseFloat'):source.index('metrics = service.getResources()')]
stub='''class JavaCodeException extends Exception {JavaCodeException(String s){super(s);}}
class Tasker {java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}}
tasker=new Tasker();
check(){'''+geometry+'''return endY;}
setup(){tasker.vars.clear();tasker.setVariable("sig3_x","540");tasker.setVariable("sig3_y","1130");tasker.setVariable("sig3_end_y","1391");tasker.setVariable("sig3_drag_direct","1");tasker.setVariable("SIG3_Family","Volume");tasker.setVariable("SIG3_VolumeTrackTopY","695");tasker.setVariable("SIG3_VolumeTrackBottomY","2000");tasker.setVariable("SIG3_VolumeX","540");tasker.setVariable("SIG3_VolumeY","1130");tasker.setVariable("sig3_target","7");}
for(int target=0;target<=15;target++){setup();tasker.setVariable("sig3_target",""+target);if(target==10)tasker.setVariable("SIG3_VolumeY","1217");actual=check();expected=Math.round(2000-target*87.0f);if(actual!=expected)throw new RuntimeException("endpoint "+target);}
'''
stub+='for(family:new String[]{"Balance","Tinnitus"}){for(int step=0;step<=15;step++){setup();tasker.setVariable("SIG3_Family",family);tasker.setVariable("SIG3_"+family+"TrackTopY","695");tasker.setVariable("SIG3_"+family+"TrackBottomY","2000");tasker.setVariable("SIG3_"+family+"X","540");tasker.setVariable("SIG3_"+family+"Y",step==10?"1217":"1130");tasker.setVariable("sig3_target",""+(family.equals("Balance")?step-8:step));if(check()!=Math.round(2000-step*87.0f))throw new RuntimeException("family endpoint "+family);}}'
for name,value in [('SIG3_Family','Unknown'),('sig3_target','16'),('SIG3_VolumeTrackTopY','NaN'),('SIG3_VolumeTrackBottomY','600'),('SIG3_VolumeY','600'),('SIG3_VolumeTrackTopY','bad'),('SIG3_VolumeX','NaN')]:
 stub+='setup();tasker.setVariable("'+name+'","'+value+'");rejected=false;try{check();}catch(Exception e){rejected=true;}if(!rejected)throw new RuntimeException("guard '+name+'");\n'
for family,target in [('Balance',8),('Balance',-9),('Tinnitus',16),('Tinnitus',-1)]:
 stub+='setup();tasker.setVariable("SIG3_Family","'+family+'");tasker.setVariable("SIG3_'+family+'TrackTopY","695");tasker.setVariable("SIG3_'+family+'TrackBottomY","2000");tasker.setVariable("SIG3_'+family+'X","540");tasker.setVariable("SIG3_'+family+'Y","1130");tasker.setVariable("sig3_target","'+str(target)+'");rejected=false;try{check();}catch(Exception e){rejected=true;}if(!rejected)throw new RuntimeException("family bounds");\n'

stub+='setup();tasker.setVariable("sig3_drag_direct","0");rejected=false;try{check();}catch(Exception e){rejected=true;}if(!rejected)throw new RuntimeException("incremental distance limit");print("PASS");'
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'geometry.bsh';p.write_text(stub)
 r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(p)],capture_output=True,text=True,check=True)
 assert r.stdout.strip()=='PASS',r.stdout+r.stderr
print('Actual direct geometry: 48 target endpoints and 12 rejection guards passed')

# Execute the production stroke construction with small Android stand-ins.
activation=source[source.index('minimumTap = direct'):source.index('performStroke(service, moveStroke')]
builder=source[source.index('builder = new GestureDescription.Builder()'):source.index('if (!service.dispatchGesture')]
construction=(activation+'stroke=moveStroke;phase="move";'+builder).replace('GestureDescription.StrokeDescription','MockStroke').replace('GestureDescription.Builder','MockBuilder').replace('new Path()','new MockPath()')
fixture='''class MockPath {void moveTo(float x,float y){}void lineTo(float x,float y){}}
class MockStroke {long start;long duration;MockStroke(Object path,long s,long d,boolean more){start=s;duration=d;}}
class MockBuilder {java.util.List strokes=new java.util.ArrayList();MockBuilder addStroke(Object stroke){strokes.add(stroke);return this;}Object build(){return strokes;}}
class Tasker {java.util.Map vars=new java.util.HashMap();String getVariable(String n){return (String)vars.get(n);}void setVariable(String n,String v){vars.put(n,v);}}
tasker=new Tasker();x=540f;y=2000f;endY=1739f;
checkConstruction(){'''+construction+'''return gesture;}
for(family:new String[]{"Volume","Balance","Tinnitus"}){for(start:new String[]{"0","3"}){for(direct:new boolean[]{false,true}){
tasker.setVariable("sig3_start",start);tasker.setVariable("SIG3_Gesture","");strokes=checkConstruction();needsTap=direct && family.equals("Tinnitus") && start.equals("0");
if(strokes.size()!=(needsTap?2:1))throw new RuntimeException("activation isolation");
move=(MockStroke)strokes.get(strokes.size()-1);if(move.duration!=650 || move.start!=(needsTap?200:0))throw new RuntimeException("movement timing");
if(needsTap){tap=(MockStroke)strokes.get(0);if(tap.start!=0 || tap.duration!=50)throw new RuntimeException("activation timing");}
}}}print("PASS");'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'construction.bsh';p.write_text(fixture)
 r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(p)],capture_output=True,text=True,check=True)
 assert r.stdout.strip()=='PASS',r.stdout+r.stderr
print('Actual stroke construction: 12 family/mode/start cases passed')
