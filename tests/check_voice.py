"""Voice targets come from the command, independently of AutoVoice groups."""
from check_volume import Phone

for family, bounds, targets in [
    ('volume', (0, 15), [0, 1, 10, 15]),
    ('balance', (-8, 7), [-8, -1, 0, 7]),
    ('tinnitus', (0, 15), [0, 10, 15]),
]:
    for target in targets:
        p = Phone(0, bounds=bounds)
        p.globals.update(SIG_ModeChanged='0')
        # avcomm is local in Tasker; provide it as the AutoVoice output in the mock.
        p.run('SIG_VoiceRouter', f'SET {family} TO {target}')
        assert p.level == target, (family, target, p.level)
for command in ['volume 16', 'balance -9', 'tinnitus 20', 'mute tinnitus please volume up']:
    p = Phone(3)
    p.run('SIG_VoiceRouter', command)
    assert p.level == 3 and not p.drags and not p.closed
p = Phone(3)
p.globals.update(SIG_ModeChanged='0')
p.run('SIG_VoiceRouter', 'tinnitus down')
assert p.level == 2
print('Passed: voice numeric extraction, negative balance, multi-digit targets, range rejection and tinnitus routing.')
