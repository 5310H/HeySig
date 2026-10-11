"""Reused action templates must retain independent consecutive action numbers."""
import sys
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
