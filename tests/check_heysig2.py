"""Execute actual Phase 1 action lists with aligned mock accessibility arrays."""
import json
from copy import deepcopy
from itertools import permutations
import xml.etree.ElementTree as E
from heysig2_runtime import Phone, ROOT, TASKS


def phone(level, mode='region', **kwargs):
    p = Phone(level, **kwargs)
    if mode == 'id': p.globals['SIG2_KnobId'] = 'volume-knob'
    else:
        p.globals.update(SIG2_KnobXMin='450', SIG2_KnobXMax='550',
                         SIG2_KnobYMin='350', SIG2_KnobYMax='1050')
    return p


# Real-device 7 capture plus synthetic endpoint values using its verified ID.
CAPTURE_ID = 'com.signia.rta:id/TA-SliderValue'

def capture(level=7, order=(0, 1, 2), knob_id=CAPTURE_ID):
    rows = [('15', 'com.signia.rta:id/maximum', '700,1000'),
            (str(level), knob_id, '541,1701'),
            ('0', 'com.signia.rta:id/minimum', '700,2000')]
    rows = [rows[i] for i in order]
    p = Phone(level, texts=','.join(r[0] for r in rows),
              ids=[r[1] for r in rows], coordinates=[r[2] for r in rows])
    p.globals['SIG2_KnobId'] = CAPTURE_ID
    return p

# Regression: the original simple Matches operator interprets '/' as OR.
original = TASKS['SIG2_VolumeCurrent']
broken = deepcopy(original)
id_condition = next(c for c in broken.findall('.//Condition')
                    if c.findtext('lhs') == '%aiid(%sig2_i)')
id_condition.find('op').text = '2'
id_condition.find('rhs').text = '%SIG2_KnobId'
try:
    TASKS['SIG2_VolumeCurrent'] = broken
    p = capture(); p.run('SIG2_VolumeCurrent')
    assert p.globals['SIG2_Level'] == '-1' and p.globals['SIG2_VolumeOK'] == '0'
    assert 'Knob selector matched' in p.globals['SIG2_Error']
finally:
    TASKS['SIG2_VolumeCurrent'] = original

for level in range(16):
    for order in permutations(range(3)):
        p = capture(level, order); p.run('SIG2_VolumeCurrent')
        assert (p.globals['SIG2_Level'], p.globals['SIG2_VolumeX'],
                p.globals['SIG2_VolumeY'], p.globals['SIG2_VolumeOK']) == (str(level), '541', '1701', '1'), p.globals

# Regex metacharacters in a resource ID are literal, and partial IDs fail.
for bad_id in ('comXsigniaXrta:id/TA-SliderValue', 'TA-SliderValue',
               'com.signia.rta:id', CAPTURE_ID + '-other'):
    p = capture(knob_id=bad_id); p.run('SIG2_VolumeCurrent')
    assert p.globals['SIG2_VolumeOK'] == '0'

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
            elif delta == -1: assert p.taps
            else: assert not p.taps

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
    for stage in ('launch', 'query', 'tab', 'gesture'):
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
print('Passed: captured 7/541/1701, slash-ID regression, literal IDs, all 16 values in all query orders; four isolated exports, import structure, project parity, all 16 values in both selector modes, endpoint duplicates, array ordering, failure paths and verified one-step moves.')

# Runtime geometry: 7=1701, 8=1661, desired 9=1621.
p = phone(8, 'id')
p.knob_x, p.knob_y0 = 541, 1981
p.run('SIG2_VolumeUp')
assert p.level == 9 and p.globals['SIG2_VolumeOK'] == '1'
assert p.globals['SIG2_VolumeX'] == '541' and p.globals['SIG2_VolumeY'] == '1621'
assert p.drags == [40] and not p.taps
assert p.gestures == [('541,1661', '541,1621', '200+300')]
assert p.globals['SIG2_Error'] == '' and p.globals['SIG2_MoveStage'] == 'complete'
for stage in ('gesture', 'halt_gesture'):
    p = phone(8, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.globals['SIG2_VolumeOK'] == '0'
    assert ('tap' if 'number' in stage else 'gesture') in p.globals['SIG2_Error'], p.globals
for opts, fragment in [(dict(threshold=1000), 'unchanged'), (dict(jump=2), 'unexpected level')]:
    p = phone(8, 'id', **opts); p.run('SIG2_VolumeUp')
    assert p.globals['SIG2_VolumeOK'] == '0' and fragment in p.globals['SIG2_Error'], p.globals
    assert len(p.drags) == 1
print('Passed: simulated gesture payload 541,1661 -> 541,1621, 40 px up, 200 ms hold + 300 ms move; gesture failures, halted actions, unchanged and overshoot diagnostics.')

class FailedPostQuery(Phone):
    def run(self, name, param='', param2=''):
        if name == 'SIG2_VolumeCurrent' and param == 'query_only' and self.drags:
            self.fail_stage = 'halt_query'
        super().run(name, param, param2)
p = FailedPostQuery(8)
p.globals['SIG2_KnobId'] = 'volume-knob'
p.run('SIG2_VolumeUp')
assert p.globals['SIG2_VolumeOK'] == '0' and 'query did not complete' in p.globals['SIG2_Error']
for stage in ('launch', 'query', 'tab', 'gesture'):
    p = phone(8, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.globals['SIG2_VolumeOK'] == '0' and p.globals['SIG2_Error'].strip(), (stage,p.globals)
print('Passed: post-gesture query halt retains a useful error; every injected Up failure leaves a diagnostic.')

for stage, prefix in [('gesture', 'Gesture')]:
    p = phone(8, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.globals[f'SIG2_{prefix}Err'] == '1'
    assert p.globals[f'SIG2_{prefix}ErrMsg'] == 'Injected plugin failure'
    assert 'code=1 message=Injected plugin failure' in p.globals['SIG2_Error']
for stage, prefix in [('halt_gesture', 'Gesture')]:
    p = phone(8, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.globals[f'SIG2_{prefix}Err'] == 'not returned (action halted)'

# Each raw error pair is copied immediately after its plugin, ahead of guards.
aa = TASKS['SIG2_VolumeUp'].findall('Action')
for i,a in enumerate(aa):
    if a.findtext('code') == '474': prefix='Gesture'
    elif a.findtext('code') == '107361459': prefix='Tap'
    else: continue
    assert aa[i+1].findtext("Str[@sr='arg0']") == f'%SIG2_{prefix}Err'
    assert aa[i+1].findtext("Str[@sr='arg1']") == '%err'
    assert aa[i+2].findtext("Str[@sr='arg0']") == f'%SIG2_{prefix}ErrMsg'
    assert aa[i+2].findtext("Str[@sr='arg1']") == '%errmsg'

# Legacy display summaries are invalid inputs to the installed point parser.
for bad_point in ('Start X: 541\nStart Y: 1661', 'End X: 541\nEnd Y: 1621'):
    assert len(bad_point.split(',')) != 2
print('Passed: installed AutoInput comma-pair point format, display-label rejection, immediate native error snapshots and halted-action diagnostics.')

java_action = next(a for a in TASKS['SIG2_VolumeUp'].findall('Action') if a.findtext('code') == '474')
assert java_action.findtext('se') == 'true'
assert [(e.tag, e.get('sr')) for e in java_action if e.tag in ('Str', 'Int')] == [('Str', 'arg0'), ('Str', 'arg1'), ('Int', 'arg2')]
assert java_action.find("Int[@sr='arg2']").get('val') == '1'
script = java_action.findtext("Str[@sr='arg0']")
assert script == (ROOT / 'tools/sig2_hold_drag.java').read_text()
for required in ('tasker.getAccessibilityService()', 'StrokeDescription(holdPath, 0, 200, true)',
                 'holdStroke.continueStroke(movePath, 0, 300, false)', 'movePath.moveTo(x, y)',
                 'movePath.lineTo(x, endY)', 'onCompleted', 'onCancelled',
                 'signal.await(3, TimeUnit.SECONDS)', 'dispatchGesture rejected',
                 'finally', 'holdStroke.continueStroke(holdPath, 0, 1, false)'):
    assert required in script, required
assert all(a.findtext('code') != '778682267' for a in TASKS['SIG2_VolumeUp'].findall('Action'))
p = phone(8, 'id', fail_stage='gesture'); p.run('SIG2_VolumeUp')
p.fail_stage = None; p.run('SIG2_VolumeCurrent', 'query_only')
assert p.globals['SIG2_GestureErr'] == '1' and p.globals['SIG2_GestureErrMsg'] == 'Injected plugin failure'
print('Passed: actual Tasker 6.6.20 Java Code schema, same-pointer continuation, completion diagnostics, release cleanup and snapshots.')

for stage, returned in [('gesture', '1'), ('halt_gesture', '0')]:
    p = phone(8, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.globals['SIG2_GestureReturned'] == returned
p = phone(8, 'id', threshold=1000); p.run('SIG2_VolumeUp')
assert p.globals['SIG2_GestureReturned'] == '1'
assert p.globals['SIG2_GestureErr'] == 'not supplied by returned action'
assert p.globals['SIG2_GestureErrMsg'] == 'not supplied by returned action'
assert p.drags == [40] and 'unchanged' in p.globals['SIG2_Error']
print('Passed: continued-touch action, returned-versus-halted diagnostics and explicit missing-native-error values.')

assert all(a.findtext('code') != '107361459' for a in TASKS['SIG2_VolumeUp'].findall('Action'))
for level in range(15):
    p = phone(level, 'id'); p.run('SIG2_VolumeUp')
    assert not p.taps and len(p.gestures) == 1 and p.drags == [40]
print('Passed: one continuous knob drag, no separate tap, unchanged 40 px travel, 200 ms hold + 300 ms move duration and verified one-level readback.')

# Captured level 9 geometry: same contact reaches exactly level 10's stop.
p = Phone(9)
p.knob_x, p.knob_y0 = 541, 1981
p.globals['SIG2_KnobId'] = 'volume-knob'
p.run('SIG2_VolumeUp')
assert p.gestures == [('541,1621', '541,1581', '200+300')]
assert p.level == 10 and p.globals['SIG2_VolumeOK'] == '1'
assert 'DOWN-HOLD-MOVE-UP' in p.globals['SIG2_Gesture']
assert p.globals['SIG2_TouchStage'] == 'released'
print('Passed: measured 9/541/1621 -> 10/541/1581, explicit DOWN-HOLD-MOVE-UP diagnostics and verified readback.')

for stage in ('missing_service', 'hold_rejected', 'hold_cancelled', 'hold_timeout', 'move_rejected', 'move_cancelled', 'move_timeout'):
    p = phone(9, 'id', fail_stage=stage); p.run('SIG2_VolumeUp')
    assert p.level == 9 and not p.drags and p.globals['SIG2_VolumeOK'] == '0'
    assert p.globals['SIG2_GestureErr'] == '1'
    assert p.globals['SIG2_GestureErrMsg'] in p.globals['SIG2_Error']
print('Passed: simulated missing-service, hold/move rejection, cancellation and timeout diagnostics.')
