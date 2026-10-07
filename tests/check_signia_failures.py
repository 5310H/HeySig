"""Verify navigation errors cannot become slider success or unwanted gestures."""
from check_volume import Phone, ROOT, TASKS
import xml.etree.ElementTree as E

for family, bounds, level_key in [
    ('Volume', (0, 15), 'SIG_Level'),
    ('Balance', (-8, 7), 'SIG_BalanceLevel'),
    ('Tinnitus', (0, 15), 'SIG_TinnitusLevel'),
]:
    for stage in ['launch', 'query', 'tab', 'number', 'gesture']:
        p = Phone(3, bounds=bounds, fail_stage=stage)
        p.globals[f'SIG_Target{family}'] = '5'
        p.globals[f'SIG_{family}OK'] = '1'
        p.run(f'SIG_{family}Set')
        assert p.globals[f'SIG_{family}OK'] == '0', (family, stage)
        assert not p.drags and p.level == 3, (family, stage)
    for options in [{'package': 'another.app'}, {'texts': 'Tab,3,4'}, {'texts': 'Tab'}]:
        p = Phone(3, bounds=bounds, **options)
        p.globals[f'SIG_Target{family}'] = '5'
        p.run(f'SIG_{family}Set', 'keep_open')
        assert p.globals[f'SIG_{family}OK'] == '0'
        assert not p.drags and not p.closed
    for target in ['3', '5', 'bad']:
        p = Phone(3, bounds=bounds)
        p.globals[f'SIG_Target{family}'] = target
        p.run(f'SIG_{family}Set', 'keep_open')
        assert not p.closed
        assert p.globals[f'SIG_{family}OK'] == ('0' if target == 'bad' else '1')
    p = Phone(3, bounds=bounds)
    p.globals.update(SIG_Action=f'{family.lower()}_down', SIG_ModeChanged='0')
    p.run('SIG_Dispatcher')
    assert p.level == 2 and p.globals['SIG_Action'] == '0'
    assert p.globals[f'SIG_{family}OK'] == '1'
    class ChangedRequest(Phone):
        def run(self, name, param='', param2=''):
            super().run(name, param, param2)
            if name == f'SIG_{family}Up':
                self.globals[f'SIG_Target{family}'] = '999'
    p = ChangedRequest(3, bounds=bounds)
    p.globals[f'SIG_Target{family}'] = '5'
    p.run(f'SIG_{family}Set', 'keep_open')
    assert p.level == 5 and p.globals[f'SIG_{family}OK'] == '1'
    class DriftAfterMove(Phone):
        def run(self, name, param='', param2=''):
            super().run(name, param, param2)
            if name == f'SIG_{family}Up' and self.level == 5:
                self.level = 6
    p = DriftAfterMove(3, bounds=bounds)
    p.globals[f'SIG_Target{family}'] = '5'
    p.run(f'SIG_{family}Set', 'keep_open')
    assert p.level == 6 and p.globals[f'SIG_{family}OK'] == '0'
    for path in (ROOT / 'tasks').glob(f'SIG_{family}*.tsk.xml'):
        t = E.parse(path).getroot().find('Task')
        other = TASKS[t.findtext('nme')]
        t.tail = other.tail = None
        assert E.tostring(t) == E.tostring(other), path
        aa = sorted(t.findall('Action'), key=lambda a: int(a.get('sr')[3:]))
        assert [a.get('sr') for a in aa] == [f'act{i}' for i in range(len(aa))]
print('Passed: plugin failure stages, wrong app, ambiguous/missing readings, stale status, keep_open, dispatcher and export equality.')
