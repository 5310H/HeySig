"""Reused action templates must retain independent consecutive action numbers."""
import sys
import xml.etree.ElementTree as E
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_heysig3 as b
record=b.java_code('return "recorded";')
a=b.task('Acceptance',1000,[b.setvar('%SIG3_Test','start'),record,b.wait(),record])
assert [n.get('sr') for n in a.findall('Action')]==['act0','act1','act2','act3']
assert record.get('sr')=='act0'
a.findall('Action')[1].find("Str[@sr='arg0']").text='return "changed";'
assert a.findall('Action')[3].findtext("Str[@sr='arg0']")=='return "recorded";'
print('Shared templates generate independent, consecutive actions')

# A plugin timeout shorter than its capture window fails on the real phone.
noise=E.parse(b.ROOT / 'tasks/SIG3_InternalNoiseSample.tsk.xml')
capture=next(a for a in noise.findall('.//Action') if a.findtext('code')=='1218739680')
listen=float(capture.findtext('Bundle/Vals/TimeToListent'))
timeout=int(capture.find("Int[@sr='arg3']").get('val'))
assert timeout >= listen + 5, 'Allow capture time plus plugin response overhead'
assert capture.findtext('se')=='true', 'Preserve plugin error reporting'
print('Phone noise capture timeout includes listening and response time')
