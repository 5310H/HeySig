"""Build temporary, opt-in phone reliability tasks outside release exports.

The polling task retains every production action; only its optional numeric logger
adds a bounded summary and monotonic stop deadline. Reimport the release polling
export after collecting the run. No startup profile or program changes are added.
"""
from pathlib import Path
import sys,xml.etree.ElementTree as E
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_heysig3 as b

init='''import java.io.*;
secondsText=tasker.getVariable("sig3_trial_seconds");seconds=secondsText==null||secondsText.startsWith("%")||secondsText.length()==0?28800:Integer.parseInt(secondsText);
if(seconds<60||seconds>28800)throw new Exception("Trial duration must be 60–28800 seconds");
if("1".equals(tasker.getVariable("SIG3_WakeEnabled"))||"1".equals(tasker.getVariable("SIG3_VoiceBusy"))||"1".equals(tasker.getVariable("SIG3_NoiseEnabled")))throw new Exception("Stop existing listening, voice capture and polling before the trial");
f=new File("/sdcard/Tasker/sig3-endurance-summary.json");if(f.isFile()){previous=new File(f.getPath()+".previous");if(previous.isFile()&&!previous.delete())throw new Exception("Could not archive the previous summary");if(!f.renameTo(previous))throw new Exception("Could not archive the previous summary");}
now=System.currentTimeMillis();uptime=android.os.SystemClock.elapsedRealtime();
tasker.setVariable("SIG3_EnduranceRunId",""+now);tasker.setVariable("SIG3_EnduranceDeadline",""+(now+seconds*1000L));tasker.setVariable("SIG3_EnduranceDeadlineUptime",""+(uptime+seconds*1000L));
tasker.setVariable("SIG3_EnduranceEnabled","1");tasker.setVariable("SIG3_EnduranceStatus","starting");tasker.setVariable("SIG3_NoiseLogEnabled","1");tasker.setVariable("SIG3_NoiseCalibrationStage","");return "observation endurance initialized";'''

def build(output=Path('/tmp')):
    output.mkdir(parents=True,exist_ok=True)
    poll=E.parse(b.ROOT/'tasks/SIG3_NoisePoll.tsk.xml').getroot()
    log=(b.ROOT/'tools/sig3_noise_log.java').read_text()
    metrics=(b.ROOT/'tools/sig3_endurance_metrics.java').read_text()
    found=False
    for node in poll.findall('.//Action/Str'):
        if node.text==log:
            node.text='numericLog(){'+log+'}\nenduranceSummary(){'+metrics+'}\nnumericLog();return enduranceSummary();'
            found=True
    assert found,'Production numeric logger not found'
    E.ElementTree(poll).write(output/'00_SIG3_NoisePoll_endurance.tsk.xml',encoding='utf-8',xml_declaration=True)
    aa=[b.condition('%TRUN',4,r'(^|,)SIG3_NoisePoll(,|$)'),b.stop(),b.action(38),b.setvar('%sig3_noise_pref_mode','load'),b.java_file('sig3_noise_preferences.java'),b.condition('%err',12),b.stop(),b.action(38),b.condition('%SIG3_NoiseSettingsReady',3,1),b.stop(),b.action(38),b.condition('%SIG3_NoiseScaleConfirmed',3,1),b.stop(),b.action(38),b.setvar('%sig3_trial_seconds','%par1'),b.java_code(init),b.call('SIG3_NoiseObserve')]
    r=E.Element('TaskerData',sr='',dvi='1',tv='6.6.20');r.append(b.task('00_SIG3_EnduranceStart',9931,aa));E.ElementTree(r).write(output/'00_SIG3_EnduranceStart.tsk.xml',encoding='utf-8',xml_declaration=True)
    stop=[b.call('SIG3_NoiseStop'),b.setvar('%SIG3_NoiseLogEnabled',0),b.setvar('%SIG3_EnduranceEnabled',0),b.setvar('%SIG3_EnduranceStatus','stopped early')]
    r=E.Element('TaskerData',sr='',dvi='1',tv='6.6.20');r.append(b.task('00_SIG3_EnduranceStop',9932,stop));E.ElementTree(r).write(output/'00_SIG3_EnduranceStop.tsk.xml',encoding='utf-8',xml_declaration=True)
    r=E.Element('TaskerData',sr='',dvi='1',tv='6.6.20');r.append(b.task('00_SIG3_EnduranceSmoke',9933,[b.call('00_SIG3_EnduranceStart','60')]));E.ElementTree(r).write(output/'00_SIG3_EnduranceSmoke.tsk.xml',encoding='utf-8',xml_declaration=True)
    print('Built four temporary tasks in '+str(output))

if __name__=='__main__':build()
