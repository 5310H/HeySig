"""Exercise independent balance/tinnitus controls using a simulated slider."""
from pathlib import Path
import xml.etree.ElementTree as E
from check_volume import Phone, TASKS, ROOT

for family, low, high, endpoints in [
    ('Balance', -8, 7, [('Soft', -8), ('Sharp', 7)]),
    ('Tinnitus', 0, 15, [('Mute', 0), ('Max', 15)]),
]:
    status = f'SIG_{family}OK'
    for start in range(low, high + 1):
        for suffix, delta in [('Up', 1), ('Down', -1)]:
            p = Phone(start, bounds=(low, high))
            p.run(f'SIG_{family}{suffix}', 'keep_open')
            assert p.level == max(low, min(high, start + delta))
            assert p.globals[status] == '1' and not p.closed
        for target in range(low, high + 1):
            p = Phone(start, bounds=(low, high))
            p.globals[f'SIG_Target{family}'] = str(target)
            p.globals['SIG_Level'] = '99'
            p.run(f'SIG_{family}Set', 'keep_open')
            assert p.level == target, (family, start, target, p.level)
            assert p.globals[status] == '1' and not p.closed
            assert p.globals['SIG_Level'] == '99'
        for suffix, target in endpoints:
            p = Phone(start, bounds=(low, high))
            p.run(f'SIG_{family}{suffix}')
            assert p.level == target and p.closed
    for target in [low - 10, high + 10, 'bad']:
        p = Phone(0, bounds=(low, high))
        p.globals[f'SIG_Target{family}'] = str(target)
        p.run(f'SIG_{family}Set')
        assert p.level == (0 if target == 'bad' else max(low, min(high, target)))
        assert p.globals[status] == ('0' if target == 'bad' else '1')
    for options in [{'threshold': 1000}, {'jump': 2}, {'readable': False}]:
        p = Phone(0, bounds=(low, high), **options)
        p.globals[f'SIG_Target{family}'] = '3'
        p.run(f'SIG_{family}Set', 'keep_open')
        assert p.globals[status] == '0' and not p.closed
        assert len(p.drags) <= 20
    p = Phone(0, bounds=(low, high))
    p.run(f'SIG_{family}Current', 'keep_open')
    assert not p.drags and p.level == 0
    for path in (ROOT / 'tasks').glob(f'SIG_{family}*.tsk.xml'):
        t = E.parse(path).getroot().find('Task')
        other = TASKS[t.findtext('nme')]
        t.tail = other.tail = None
        assert E.tostring(t) == E.tostring(other), path
        assert '%SIG_Level' not in path.read_text()
print('Passed: both slider ranges, 512 Set transitions, endpoints, keep_open, isolated state, clamping and failures.')
