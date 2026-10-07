"""Regression checks for the previously malformed supplementary tasks."""
import xml.etree.ElementTree as E
from check_volume import Phone, ROOT, TASKS

legacy = E.parse(ROOT / 'tasks/sig.tasks.tsk.xml').getroot()
for t in legacy.findall('Task'):
    assert t.findtext('nme') not in TASKS, 'Supplemental task overwrites main controller'
    TASKS[t.findtext('nme')] = t
noise = E.parse(ROOT / 'tasks/SIG_NoiseMonitor.tsk.xml').getroot().find('Task')
TASKS['SIG_NoiseMonitor'] = noise
for state, mode in [('NOISE', 'VERYNOISY'), ('VOICE', None)]:
    p = Phone(8)
    p.globals.update(SIG_STATE=state, SIG_DB_ACTIVE='90', SIG_OVERRIDE='0',
                     SIG_THRESH_VNOISY='85', SIG_THRESH_NOISY='70', SIG_THRESH_CONV='60')
    p.run('SIG_StateDispatcher')
    if mode: assert p.globals['SIG_MODE'] == mode
for reading, mode in [(90, 'VERYNOISY'), (85, 'VERYNOISY'), (75, 'NOISY'), (70, 'NOISY'), (55, 'CONVERSATION')]:
    p = Phone(8)
    p.globals.update(SIG_DB_ACTIVE=str(reading), SIG_OVERRIDE='0',
                     SIG_THRESH_VNOISY='85', SIG_THRESH_NOISY='70', SIG_THRESH_CONV='60')
    p.run('SIG_NoiseEngine')
    assert p.globals['SIG_MODE'] == mode
p = Phone(8)
p.globals.update(SIG_OVERRIDE='1', SIG_MODE='SLEEP', SIG_DB_ACTIVE='90')
p.run('SIG_NoiseEngine')
assert p.globals['SIG_MODE'] == 'SLEEP'
p = Phone(8)
for expected in ['1', '0', '1']:
    p.run('SIG_OverrideToggle')
    assert p.globals['SIG_OVERRIDE'] == expected
for reading, expected in [(75, 'Music'), (60, 'Universal')]:
    p = Phone(8)
    p.noise_sample = reading
    p.globals.update(SIG_NoiseHigh='75', SIG_NoiseLow='60', SIG_StrikeLimit='3',
                     SIG_HighStrikes='0', SIG_LowStrikes='0', SIG_ProgNoisy='Music', SIG_ProgNormal='Universal')
    for _ in range(3): p.run('SIG_NoiseMonitor')
    assert p.program == expected
    assert p.globals['SIG_HighStrikes'] == p.globals['SIG_LowStrikes'] == '0'
print('Passed: supplementary dispatcher, threshold routing, override stop/toggle, and three-strike noisy/normal switching.')
