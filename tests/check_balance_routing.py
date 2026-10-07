"""Check that BalanceSet cannot route a request through volume tasks."""
from pathlib import Path
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
task = E.parse(ROOT / 'tasks/SIG_BalanceSet.tsk.xml').getroot().find('Task')
project_task = next(
    t for t in E.parse(ROOT / 'projects/HeySig.prj.xml').getroot().findall('Task')
    if t.findtext('nme') == 'SIG_BalanceSet'
)
calls = [
    a.findtext("Str[@sr='arg0']") for a in sorted(
        task.findall('Action'), key=lambda a: int(a.get('sr')[3:])
    )
    if a.findtext('code') == '130'
    and a.findtext("Str[@sr='arg0']") not in ['SIG_AppClose', 'SIG_AppError']
]
assert calls == ['SIG_BalanceCurrent', '%balance_task', 'SIG_BalanceCurrent'], calls
helpers = [a.findtext("Str[@sr='arg1']") for a in task.findall('Action')
           if a.findtext('code') == '547'
           and a.findtext("Str[@sr='arg0']") == '%balance_task']
assert set(helpers) == {'SIG_BalanceDown', 'SIG_BalanceUp'}, helpers
assert 'SIG_TargetVolume' not in E.tostring(task, encoding='unicode')
for name in ['SIG_BalanceCurrent'] + helpers:
    assert (ROOT / 'tasks' / (name + '.tsk.xml')).is_file(), name
task.tail = project_task.tail = None
assert E.tostring(task) == E.tostring(project_task)
print('Passed: BalanceSet uses only balance helpers and targets; project export matches.')
