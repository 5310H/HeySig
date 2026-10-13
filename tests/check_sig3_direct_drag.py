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
for name,value in [('SIG3_Family','Balance'),('sig3_target','16'),('SIG3_VolumeTrackTopY','NaN'),('SIG3_VolumeTrackBottomY','600'),('SIG3_VolumeY','600'),('SIG3_VolumeTrackTopY','bad'),('SIG3_VolumeX','NaN')]:
 stub+='setup();tasker.setVariable("'+name+'","'+value+'");rejected=false;try{check();}catch(Exception e){rejected=true;}if(!rejected)throw new RuntimeException("guard '+name+'");\n'
stub+='setup();tasker.setVariable("sig3_drag_direct","0");rejected=false;try{check();}catch(Exception e){rejected=true;}if(!rejected)throw new RuntimeException("incremental distance limit");print("PASS");'
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'geometry.bsh';p.write_text(stub)
 r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar','bsh.Interpreter',str(p)],capture_output=True,text=True,check=True)
 assert r.stdout.strip()=='PASS',r.stdout+r.stderr
print('Actual direct geometry: 16 target endpoints and 8 rejection guards passed')
