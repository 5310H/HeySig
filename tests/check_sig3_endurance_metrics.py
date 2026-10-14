"""Execute the test-only endurance recorder: counting, monotonic stop and fail-closed."""
import subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as folder:
    d=Path(folder);(d/'android/os').mkdir(parents=True);(d/'android/content').mkdir(parents=True)
    (d/'android/os/SystemClock.java').write_text('package android.os; public class SystemClock {public static long now=1000;public static long elapsedRealtime(){return now;}}')
    (d/'android/content/IntentFilter.java').write_text('package android.content; public class IntentFilter {public IntentFilter(String s){}}')
    subprocess.run(['javac',str(d/'android/os/SystemClock.java'),str(d/'android/content/IntentFilter.java')],check=True)
    source=(ROOT/'tools/sig3_endurance_metrics.java').read_text().replace('/sdcard/Tasker/sig3-endurance-summary.json',str(d/'summary.json'))
    stub='''
class FakeBattery {int getIntExtra(String k,int fallback){return k.equals("plugged")?0:k.equals("level")?90:100;}}
class FakeManager {int getIntProperty(int k){return 4000000;}}
class FakeLock {boolean isKeyguardLocked(){return true;}}
class FakeContext {Object getSystemService(String k){return k.equals("keyguard")?new FakeLock():new FakeManager();}FakeBattery registerReceiver(Object receiver,Object filter){return new FakeBattery();}}
class FakeTasker {java.util.Map vars=new java.util.HashMap();String getVariable(String k){return (String)vars.get(k);}void setVariable(String k,String v){vars.put(k,v);}}
tasker=new FakeTasker();context=new FakeContext();
require(ok,msg){if(!ok)throw new RuntimeException(msg);}
read(){in=new java.io.FileInputStream("TARGET");bytes=new byte[(int)in.getChannel().size()];in.read(bytes);in.close();return new org.json.JSONObject(new String(bytes,"UTF-8"));}
require(run().equals("endurance off")&&!new java.io.File("TARGET").exists(),"off creates nothing");
for(k:new String[]{"EnduranceEnabled","NoiseLogEnabled","NoiseEnabled","NoisePollSampled","CommandOK"})tasker.setVariable("SIG3_"+k,"1");
tasker.setVariable("SIG3_EnduranceRunId","trial-1");tasker.setVariable("SIG3_EnduranceDeadline","1");tasker.setVariable("SIG3_EnduranceDeadlineUptime","5000");tasker.setVariable("SIG3_NoiseLastSampleTime","1000");tasker.setVariable("SIG3_NoiseIndex","-63");tasker.setVariable("SIG3_NoiseMode","observe");
run();j=read();require(j.getLong("freshSamples")==1&&j.getString("status").equals("running")&&j.getLong("lockedTicks")==1,"first finite sample; wall time cannot stop early");
android.os.SystemClock.now=2000;tasker.setVariable("SIG3_NoiseLastSampleTime","2000");run();j=read();require(j.getLong("freshSamples")==2&&j.getLong("maxSampleGapMillis")==1000&&j.getLong("maxTickGapMillis")==1000,"count and sample gap");
android.os.SystemClock.now=3000;tasker.setVariable("SIG3_NoisePollSampled","0");run();j=read();require(j.getLong("skippedTicks")==1&&j.getLong("freshSamples")==2,"busy skips not fresh samples");
android.os.SystemClock.now=4000;tasker.setVariable("SIG3_NoisePollSampled","1");tasker.setVariable("SIG3_NoiseLastSampleTime","4000");tasker.setVariable("SIG3_CommandOK","0");tasker.setVariable("SIG3_Error","capture failed");run();require(read().getLong("failedAttempts")==1,"capture failure counted");
android.os.SystemClock.now=5000;tasker.setVariable("SIG3_NoisePollSampled","0");run();require(read().getString("status").equals("completed")&&read().getLong("stopDelayMillis")==0&&tasker.getVariable("SIG3_NoiseEnabled").equals("0")&&tasker.getVariable("SIG3_NoiseLogEnabled").equals("0"),"deadline stops sampling and logging");
tasker.setVariable("SIG3_EnduranceEnabled","1");tasker.setVariable("SIG3_EnduranceRunId","wrong");run();require(tasker.getVariable("SIG3_EnduranceStatus").startsWith("failed:")&&tasker.getVariable("SIG3_NoiseEnabled").equals("0"),"mismatched run stops safely");
new java.io.File("TARGET").delete();new java.io.File("TARGET").mkdir();tasker.setVariable("SIG3_EnduranceEnabled","1");run();require(tasker.getVariable("SIG3_EnduranceStatus").startsWith("failed:"),"I/O failure stops safely");
print("PASS: endurance counters, monotonic deadline, battery state and fail-closed boundaries");
'''.replace('TARGET',str(d/'summary.json'))
    path=d/'metrics.bsh';path.write_text('run(){'+source+'}\n'+stub)
    r=subprocess.run(['java','-XX:-UsePerfData','-cp',str(d)+':/usr/share/java/bsh.jar:/tmp/sig3-orgjson.jar','bsh.Interpreter',str(path)],capture_output=True,text=True)
    assert r.returncode==0 and 'PASS:' in r.stdout,r.stdout+r.stderr
    print(r.stdout.strip())
