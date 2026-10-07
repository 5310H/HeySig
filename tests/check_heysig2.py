"""Execute actual Phase 1 action lists with aligned mock accessibility arrays."""
import json
import xml.etree.ElementTree as E
from heysig2_runtime import Phone, ROOT, TASKS


def phone(level, mode='region', **kwargs):
    p = Phone(level, **kwargs)
    if mode == 'id': p.globals['SIG2_KnobId'] = 'volume-knob'
    else:
        p.globals.update(SIG2_KnobXMin='450', SIG2_KnobXMax='550',
                         SIG2_KnobYMin='350', SIG2_KnobYMax='1050')
    return p


for mode in ('region', 'id'):
    for level in range(16):
        p = phone(level, mode); p.run('SIG2_VolumeCurrent')
        assert p.globals['SIG2_Level'] == str(level), (mode, level, p.globals)
        assert p.globals['SIG2_VolumeOK'] == '1' and not p.drags
        assert p.globals['SIG2_VolumeX'] == '500'
        assert p.globals['SIG2_VolumeY'] == str(1000-level*40)
        for name, delta in [('SIG2_VolumeUp', 1), ('SIG2_VolumeDown', -1)]:
            p = phone(level, mode); p.run(name)
            assert p.level == max(0, min(15, level + delta)), (name, mode, level, p.globals)
            assert p.globals['SIG2_VolumeOK'] == '1', p.globals
            if level == (15 if delta == 1 else 0): assert not p.drags and not p.taps
            else: assert p.taps

# Accessibility ordering is immaterial; positions remain aligned.
for level in (0, 7, 15):
    for mode in ('region', 'id'):
        p = phone(level, mode, texts=f'0,Volume Tab,{level},15',
                  coordinates=['650,1000', '100,200', f'500,{1000-level*40}', '650,400'],
                  ids=['minimum-label', 'tab', 'volume-knob', 'maximum-label'])
        p.run('SIG2_VolumeCurrent'); assert p.globals['SIG2_Level'] == str(level)

for opts in [dict(coordinates=[]), dict(coordinates=['100,200']),
             dict(coordinates=['100,200', '650,400', 'broken', '650,1000']),
             dict(coordinates=['100,200', '500,400', '500,720', '650,1000']),
             dict(texts='Volume Tab,15,0', coordinates=['100,200','650,400','650,1000']),
             dict(package='another.app'), dict(readable=False)]:
    p = phone(7, **opts); p.globals.update(SIG2_Level='7', SIG2_VolumeX='500')
    p.run('SIG2_VolumeUp')
    assert p.globals['SIG2_VolumeOK'] == '0' and not p.drags, (opts, p.globals)
    assert p.globals['SIG2_Level'] == '-1' and p.globals['SIG2_VolumeX'] == '-1'

for mode in ('region', 'id'):
    for stage in ('launch', 'query', 'tab', 'number', 'gesture'):
        p = phone(7, mode, fail_stage=stage); p.run('SIG2_VolumeUp')
        assert p.globals['SIG2_VolumeOK'] == '0' and not p.drags, (mode,stage)
    for opts in (dict(threshold=1000), dict(jump=2)):
        p = phone(7, mode, **opts); p.run('SIG2_VolumeUp')
        assert p.globals['SIG2_VolumeOK'] == '0' and len(p.drags) <= 20

for cfg in ({}, {'SIG2_KnobId':'missing'}, {'SIG2_KnobXMin':'bad'},
            {'SIG2_KnobXMin':'550','SIG2_KnobXMax':'450','SIG2_KnobYMin':'350','SIG2_KnobYMax':'1050'}):
    p = Phone(7); p.globals.update(cfg); p.run('SIG2_VolumeUp')
    assert not p.drags and p.globals['SIG2_VolumeOK'] == '0'

p = phone(7, 'id', ids=['tab','volume-knob','volume-knob','minimum-label'])
p.run('SIG2_VolumeCurrent'); assert p.globals['SIG2_VolumeOK'] == '0'

# Import-sensitive structure and all dependency names, rather than just parsing.
project = E.parse(ROOT/'projects/HeySig2.prj.xml').getroot()
assert project.get('tv') == '6.6.20'
assert project.findtext('Project/name') == 'HeySig2'
assert {t.findtext('id') for t in project.findall('Task')} == set(project.findtext('Project/tids').split(','))
assert len(TASKS) == 4 and all(n.startswith('SIG2_') for n in TASKS)
for name,t in TASKS.items():
    standalone=E.parse(ROOT/'tasks'/f'{name}.tsk.xml').getroot().find('Task')
    standalone.tail=t.tail=None
    assert E.tostring(standalone)==E.tostring(t), name
    stack=[]
    for i,a in enumerate(t.findall('Action')):
        assert a.attrib == {'sr':f'act{i}', 've':'7'}
        tags=[c.tag for c in a]; code=a.findtext('code')
        assert tags[0]=='code'
        if a.find('se') is not None: assert tags[1]=='se'
        if code=='37':
            assert tags==['code','coll','ConditionList']
            assert [c.tag for c in a.find('ConditionList/Condition')]==['lhs','op','rhs']
            stack.append('if')
        elif code=='39':
            assert tags==['code','Str','Str','Int']; stack.append('for')
        elif code=='43': assert stack[-1]=='if'
        elif code in ('38','40'):
            assert tags==['code']; assert stack.pop()==('if' if code=='38' else 'for')
        elif code=='130': assert a.findtext("Str[@sr='arg0']") in TASKS
        if int(code)>=1000:
            vals=a.find('Bundle/Vals'); assert vals is not None
            params=vals.findtext('parameters')
            if params: json.loads(params)
    assert not stack
print('Passed: four isolated exports, import structure, project parity, all 16 values in both selector modes, endpoint duplicates, array ordering, failure paths and verified one-step moves.')
