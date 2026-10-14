"""Exercise scheduled routing through the worker; persistence has its own Java test."""
import xml.etree.ElementTree as E
from heysig3_runtime import Phone, TASKS, ROOT

project = E.parse(ROOT / 'projects/HeySig3.prj.xml')
for name, variable, task in [('SIG3_SleepSchedule', 'SleepTime', 'SIG3_ScheduledSleep'),
                             ('SIG3_WakeSchedule', 'WakeTime', 'SIG3_ScheduledWake')]:
    matches = [p for p in project.findall('Profile') if p.findtext('nme') == name]
    assert len(matches) == 1, 'Each schedule must have exactly one profile'
    profile = matches[0]
    assert profile.findtext('Time/fromvar') == profile.findtext('Time/tovar') == '%SIG3_' + variable
    assert profile.findtext('mid0') == TASKS[task].findtext('id')
    assert profile.find('mid1') is None, 'Instant schedules must not use exit restoration'

def phone():
    p = Phone(10)
    for i, name in enumerate(p.programs, 1):
        p.globals['SIG3_ProgramName' + str(i)] = name
    p.globals.update(SIG3_SleepProgram='2', SIG3_WakeProgram='1', SIG3_SleepEnabled='1',
                     SIG3_DeferAutomation='1', SIG3_ManualOverride='0')
    return p

for task in ('SIG3_ScheduledSleep', 'SIG3_ScheduledWake'):
    p = phone(); p.globals['SIG3_SleepEnabled'] = '0'; p.run(task)
    assert p.program == 'Universal' and 'SIG3_OperationId' not in p.globals
p = phone(); p.run('SIG3_ScheduledSleep')
assert p.program == 'Music' and p.globals['SIG3_SleepActive'] == '1' and p.globals['SIG3_CommandOK'] == '1', p.globals
p.run('SIG3_ScheduledWake')
assert p.program == 'Universal' and p.globals['SIG3_SleepActive'] == '0' and p.globals['SIG3_CommandOK'] == '1', p.globals
for block in ('override', 'foreground', 'cancelled'):
    p = phone()
    if block == 'override': p.globals['SIG3_ManualOverride'] = '1'
    if block == 'foreground': p.package = 'another.app'
    if block == 'cancelled': p.globals['SIG3_AutomationCancelled'] = '1'
    p.run('SIG3_ScheduledSleep')
    assert p.program == 'Universal' and p.globals['SIG3_CommandOK'] == '0', (block, p.globals)
p = phone(); p.globals['SIG3_SleepActive'] = '1'; p.run('SIG3_SleepDisable')
assert p.globals['SIG3_SleepEnabled'] == p.globals['SIG3_SleepActive'] == '0'
print('PASS: instant variable schedules, worker routing, disabled/override/foreground/cancel guards and disable cleanup')
