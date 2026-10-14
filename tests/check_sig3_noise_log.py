"""Run opt-in numeric telemetry, including size and diagnostic failure boundaries."""
import os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
jar=Path(os.environ.get('SIG3_JSON_JAR','/tmp/sig3-orgjson.jar'))
assert jar.is_file(), 'Set SIG3_JSON_JAR to the test-only org.json JAR'
source=(ROOT/'tools/sig3_noise_log.java').read_text()
with tempfile.TemporaryDirectory() as folder:
    target=Path(folder)/'samples.jsonl'
    source=source.replace('/sdcard/Tasker/sig3-noise-observation.jsonl',str(target))
    stub='''
class FakeRoot {String getPackageName(){return "com.signia.rta";}}
class FakeService {FakeRoot getRootInActiveWindow(){return new FakeRoot();}}
class FakeLock {boolean isKeyguardLocked(){return false;}}
class FakeContext {FakeLock getSystemService(String key){return new FakeLock();}}
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){vars.put(k,v);}FakeService getAccessibilityService(){return new FakeService();}}
tasker=new FakeTasker();context=new FakeContext();
require(ok,message){if(!ok)throw new RuntimeException(message);}
file=new java.io.File("TARGET");
require(log().equals("logging off")&&!file.exists(),"off by default");
tasker.setVariable("SIG3_NoiseLogEnabled","1");tasker.setVariable("SIG3_NoiseRaw","-65");tasker.setVariable("SIG3_NoiseIndex","-65.0");tasker.setVariable("SIG3_NoiseCalibrationStage","quiet");tasker.setVariable("SIG3_Error","%err");log();log();
reader=new java.io.BufferedReader(new java.io.FileReader(file));a=new org.json.JSONObject(reader.readLine());b=reader.readLine();require(b!=null&&reader.readLine()==null,"two lines");reader.close();
require(a.getString("stage").equals("quiet")&&a.getString("NoiseRaw").equals("-65")&&a.getString("foregroundPackage").equals("com.signia.rta")&&!a.getBoolean("locked")&&a.getString("Error").equals(""),"numeric state and unresolved tokens");
out=new java.io.FileOutputStream(file);out.write(new byte[262145]);out.close();log();require(file.length()<4096,"bounded log rolls over");
length=file.length();tasker.setVariable("SIG3_NoiseLogEnabled","0");log();require(file.length()==length,"off does not touch existing log");
file.delete();file.mkdir();tasker.setVariable("SIG3_NoiseLogEnabled","1");require(log().equals("diagnostic write failed")&&tasker.getVariable("SIG3_NoiseLogError").length()>0,"diagnostic failure does not abort polling");
print("PASS: numeric-only opt-in telemetry, state labels, bounded storage and nonfatal write failure");
'''.replace('TARGET',str(target))
    path=Path(folder)/'log.bsh';path.write_text('log(){'+source+'}\n'+stub)
    r=subprocess.run(['java','-XX:-UsePerfData','-cp','/usr/share/java/bsh.jar:'+str(jar),'bsh.Interpreter',str(path)],capture_output=True,text=True)
    assert r.returncode==0 and 'PASS:' in r.stdout,r.stdout+r.stderr
    print(r.stdout.strip())
