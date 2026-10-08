"""Exercise worker collision, recovery and guard failures in exported task flow.

Android Java checks are modeled; this does not execute BeanShell or Android APIs.
"""
from copy import deepcopy
import xml.etree.ElementTree as E
from heysig3_runtime import Phone, TASKS, ROOT

def phone():
    p = Phone(7)
    p.globals.update(SIG3_KnobId='volume-knob', SIG3_BalanceKnobId='volume-knob',
                     SIG3_TinnitusKnobId='volume-knob', SIG3_BalanceStepPx='40', SIG3_TinnitusStepPx='40',
                     SIG3_BalanceDirection='1', SIG3_TinnitusDirection='1', SIG3_AudioStream='media')
    return p

# A different public family attempts to enter during a volume gesture.
p = phone()
def overlap(p):
    snapshot = {k: v for k, v in p.globals.items() if k.startswith('SIG3_')}
    p.run('SIG3_BalanceSet', '3')
    assert {k: v for k, v in p.globals.items() if k.startswith('SIG3_')} == snapshot
p.hook = overlap
p.run('SIG3_VolumeSet', '8')
assert p.level == 8 and len(p.drags) == 1 and p.globals['SIG3_CommandOK'] == '1'
assert not p.active and not p.globals['TRUN']

# A rejected/failed operation cannot leave a sticky busy flag; later command succeeds.
for failure in ('gesture','phone','ui','halt_gesture'):
    p = phone(); p.fail_stage = failure; p.run('SIG3_VolumeSet','8')
    assert p.globals['SIG3_CommandOK'] == '0' and not p.active, p.globals
    p.fail_stage = None; p.run('SIG3_VolumeSet', '8')
    assert p.level == 8 and p.globals['SIG3_CommandOK'] == '1', p.globals

# A reused numeric label on a different control cannot certify success.
p = phone(); p.wrong_control = True; p.run('SIG3_VolumeSet','8')
assert not p.drags and p.globals['SIG3_CommandOK'] == '0'
# Changing the program at gesture completion is rejected at readback.
p = phone(); p.hook = lambda p: setattr(p, 'program_capture', 'Music')
p.run('SIG3_VolumeSet','8')
assert len(p.drags) == 1 and p.globals['SIG3_CommandOK'] == '0'
assert 'UI guard' in p.globals['SIG3_Error']

# Internal helper cannot be launched outside worker ownership.
p = phone(); p.run('SIG3_InternalVolumeSet','8'); assert not p.drags
# Unknown request reports failure without movement.
p = phone(); p.run('SIG3_Worker','Wrong,Set,8'); assert not p.drags and p.globals['SIG3_CommandOK'] == '0'

# Calibration is read-only, preserves existing step if validation fails.
p = phone(); p.run('SIG3_Calibrate','Balance','40,1')
assert p.globals['SIG3_BalanceStepPx'] == '40' and not p.drags
p.run('SIG3_Calibrate','Balance','40,0')
assert p.globals['SIG3_CommandOK'] == '0' and p.globals['SIG3_BalanceDirection'] == '1'

# One supported project, all child references resolvable, public writes only call worker.
r = E.parse(ROOT / 'projects/HeySig3.prj.xml').getroot()
for t in r.findall('Task'):
    name = t.findtext('nme')
    for a in t.findall('Action'):
        if a.findtext('code') == '130':
            callee = a.findtext("Str[@sr='arg0']")
            assert callee in TASKS and callee.startswith('SIG3_')
            if not name.startswith('SIG3_Internal') and name != 'SIG3_Worker': assert callee in ('SIG3_Worker', 'SIG3_VoiceRouter')
    # Omission uses Tasker's documented default Abort New Task collision policy.
    assert t.find('rty') is None
    other = E.parse(ROOT / 'tasks' / (name + '.tsk.xml')).getroot().find('Task')
    def clean(e):
        e.tail = None
        if e.text and not e.text.strip(): e.text = None
        for c in e: clean(c)
    clean(t); clean(other); assert E.tostring(t) == E.tostring(other), name
print('Worker collision/recovery, wrong-control/program guards, calibration, project isolation/parity passed')
