"""Compare slider action serialization with phone-confirmed working Balance XML.

This checks the importer-sensitive representation, not just XML parsing or
simulated execution. It does not implement Tasker's Android importer.
"""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]


def shape(element):
    return (element.tag, tuple(sorted(element.attrib.items())),
            tuple(shape(child) for child in element))


def check_conditions(task):
    for condition in task.findall('.//Condition'):
        assert [c.tag for c in condition] == ['lhs', 'op', 'rhs'], (
            task.findtext('nme'), E.tostring(condition))
    stack = []
    for i, action in enumerate(task.findall('Action')):
        assert action.get('sr') == f'act{i}'
        code = action.findtext('code')
        assert list(action.attrib) == ['sr', 've']
        tags = [child.tag for child in action]
        assert tags[0] == 'code'
        if action.find('se') is not None:
            assert tags[1] == 'se'
        if code == '37':
            assert tags == ['code', 'coll', 'ConditionList']
            assert action.findtext('coll') in ('false', 'true')
        if code in ('38', '40'):
            assert tags == ['code']
        if code == '39':
            assert tags == ['code', 'Str', 'Str', 'Int']
        if code in ('37', '39'):
            stack.append(code)
        elif code == '43':
            assert stack and stack[-1] == '37'
        elif code in ('38', '40'):
            assert stack and stack.pop() == {'38': '37', '40': '39'}[code]
    assert not stack


project = E.parse(ROOT / 'projects/HeySig.prj.xml').getroot()
checked = 0
for family in ('Volume', 'Tinnitus'):
    for suffix in ('Current', 'Up', 'Down', 'Set', 'Max', 'Mute'):
        name = f'SIG_{family}{suffix}'
        task = E.parse(ROOT / f'tasks/{name}.tsk.xml').getroot().find('Task')
        assert len(task.findall('Action')) == {
            'Current': 63, 'Up': 87, 'Down': 87, 'Set': 87, 'Max': 2, 'Mute': 2,
        }[suffix], name
        check_conditions(task)
        embedded = next(t for t in project.findall('Task') if t.findtext('nme') == name)
        task.tail = embedded.tail = None
        assert E.tostring(task) == E.tostring(embedded), name
        if suffix in ('Current', 'Up', 'Down', 'Set'):
            good = E.parse(ROOT / f'tasks/SIG_Balance{suffix}.tsk.xml').getroot().find('Task')
            actions, reference = task.findall('Action'), good.findall('Action')
            assert len(actions) == len(reference), name
            for action, known_good in zip(actions, reference):
                assert action.findtext('code') == known_good.findtext('code')
                def comparable(a):
                    a = deepcopy(a)
                    for metadata in ('coll', 'se'):
                        child = a.find(metadata)
                        if child is not None:
                            a.remove(child)
                    return shape(a)
                assert action.findtext('se') == known_good.findtext('se')
                assert comparable(action) == comparable(known_good), (name, action.get('sr'))
            # Reproduce the dropped action immediately after Launch App.
            if suffix == 'Current':
                broken = deepcopy(task)
                condition = broken.find("Action[@sr='act4']/ConditionList/Condition")
                condition.remove(condition.find('rhs'))
                try:
                    check_conditions(broken)
                except AssertionError:
                    pass
                else:
                    raise AssertionError('Missing RHS regression was not detected')
        checked += 1

print(f'Passed: {checked} Volume/Tinnitus files, Balance argument shapes, canonical action metadata, condition fields, nested control flow, project parity, and missing-RHS regression.')
