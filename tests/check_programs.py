"""Test configured program names rather than screen coordinate guesses."""
from check_volume import Phone, ROOT, TASKS
import xml.etree.ElementTree as E

for target in range(1, 7):
    p = Phone(8)
    p.globals.update(SIG_Action='program_switch', SIG_ModeChanged='0', SIG_ProgramTarget=str(target))
    p.globals.update({f'SIG_Program{i}': value for i, value in enumerate(p.programs, 1)})
    p.run('SIG_Dispatcher')
    assert p.program == p.programs[target - 1]
    assert p.globals['SIG_CurrentProgram'] == p.program
    assert p.globals['SIG_ProgramOK'] == '1'
    assert not p.drags
for options in [{'package': 'other.app'}, {'fail_stage': 'query'}, {'fail_stage': 'number'}, {'texts': 'Wrong program'}]:
    p = Phone(8, **options)
    p.globals.update(SIG_Mode='Music', SIG_CurrentProgram='Universal')
    p.run('SIG_ProgramSwitch', 'keep_open')
    assert p.globals['SIG_ProgramOK'] == '0'
    assert p.globals['SIG_CurrentProgram'] == 'Universal'
    assert not p.closed
for target in ['0', '7', 'bad', '2']:
    p = Phone(8)
    p.globals.update(SIG_Action='program_switch', SIG_ModeChanged='0', SIG_ProgramTarget=target)
    p.run('SIG_Dispatcher')
    assert p.globals['SIG_ProgramOK'] == '0'
    assert p.program == 'Universal'
for name in ['ProgramSwitch', 'Dispatcher']:
    t = E.parse(ROOT / 'tasks' / f'SIG_{name}.tsk.xml').getroot().find('Task')
    other = TASKS['SIG_' + name]
    t.tail = other.tail = None
    assert E.tostring(t) == E.tostring(other)
assert 'click point(540,' not in (ROOT / 'tasks/SIG_ProgramSwitch.tsk.xml').read_text()
assert '<code>25</code>' not in (ROOT / 'tasks/SIG_ProgramSwitch.tsk.xml').read_text()
print('Passed: six configured program slots, missing/invalid slots, failed clicks/queries, wrong app and displayed-program verification.')
