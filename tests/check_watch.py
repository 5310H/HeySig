"""AutoWear payloads reuse validated phone routing and report actual results."""
from check_volume import Phone, ROOT, TASKS
import xml.etree.ElementTree as E

for command, expected in [('heysig=:=volume up', 4), ('volume down', 2),
                          ('heysig=:=set volume to 10', 10)]:
    p = Phone(3)
    p.globals.update(SIG_ModeChanged='0')
    p.run('SIG_WatchCommand', command)
    assert p.level == expected and p.globals['SIG_WatchOK'] == '1'
    assert p.globals['SIG_WatchMessage'].startswith('Completed:')
p = Phone(3)
p.watch_event = 'heysig=:=volume down'
p.globals['SIG_ModeChanged'] = '0'
p.run('SIG_WatchCommand')
assert p.level == 2 and p.globals['SIG_WatchOK'] == '1'
for command in ['other=:=volume up', 'heysig=:=', 'heysig=:=volume up=:=volume down',
                'heysig=:=volume up=:=', 'volume 99']:
    p = Phone(3)
    p.globals['SIG_WatchOK'] = '1'
    p.run('SIG_WatchCommand', command)
    assert p.level == 3 and not p.drags and p.globals['SIG_WatchOK'] == '0'
p = Phone(3, fail_stage='tab')
p.globals['SIG_ModeChanged'] = '0'
p.run('SIG_WatchCommand', 'volume up')
assert p.globals['SIG_WatchOK'] == '0' and not p.drags
p = Phone(3)
p.voice_event = 'volume up'
p.globals['SIG_ModeChanged'] = '0'
p.run('SIG_VoiceRouter')
assert p.level == 4 and p.globals['SIG_CommandOK'] == '1'
for name in ['VoiceRouter', 'WatchCommand']:
    task = E.parse(ROOT / 'tasks' / f'SIG_{name}.tsk.xml').getroot().find('Task')
    other = TASKS['SIG_' + name]
    task.tail = other.tail = None
    assert E.tostring(task) == E.tostring(other)
print('Passed: prefixed/payload watch commands, AutoWear event input, invalid input, plugin failures and AutoVoice fallback.')
