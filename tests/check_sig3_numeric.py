"""Execute numeric target exports against a simulated slider, including failure cases."""
from heysig3_runtime import Phone

def phone(family, level, **kw):
    p = Phone(level, bounds=(-8,7) if family == 'Balance' else (0,15), **kw)
    selector = 'SIG3_KnobId' if family == 'Volume' else 'SIG3_' + family + 'KnobId'
    p.globals[selector] = 'volume-knob'
    p.globals['SIG3_' + family + 'StepPx'] = '40'
    p.globals['SIG3_' + family + 'Direction'] = '1'
    return p

for family in ('Volume','Balance','Tinnitus'):
    levels = range(-8,8) if family == 'Balance' else range(16)
    for start in levels:
        for target in levels:
            p = phone(family,start); p.run('SIG3_' + family + 'Set',str(target))
            assert p.level == target, (family,start,target,p.globals)
            assert p.globals['SIG3_' + family + 'OK'] == '1'
            assert not p.taps and len(p.drags) == abs(start-target)
    for value in ('bad','1.5','100','-100',''):
        p = phone(family,2); p.run('SIG3_' + family + 'Set',value)
        assert not p.drags and p.globals['SIG3_' + family + 'OK'] == '0'
    for kw in ({'threshold':100}, {'jump':2}, {'fail_stage':'gesture'}, {'readable':False}):
        p = phone(family,2,**kw); p.run('SIG3_' + family + 'Set','4')
        assert p.globals['SIG3_' + family + 'OK'] == '0', p.globals
    p = phone(family,2); p.run('SIG3_VoiceRouter',family.lower() + ' four')
    assert p.level == 4 and p.globals['SIG3_CommandOK'] == '1'
    p.run('SIG3_VoiceRouter',family.lower() + ' four')
    assert len(p.drags) == 2  # repeating a target is a no-op
p = phone('Balance',0); p.run('SIG3_BalanceSet','-9')
assert p.level == 0 and not p.drags and p.globals['SIG3_CommandOK'] == '0'
p = phone('Balance',2); p.run('SIG3_VoiceRouter','set balance to minus three')
assert p.level == -3 and p.globals['SIG3_CommandOK'] == '1'
for family in ('Balance','Tinnitus'):
    p = phone(family,2); del p.globals['SIG3_' + family + 'StepPx']
    p.run('SIG3_' + family + 'Set','3'); assert not p.drags
print('Numeric targets: 768 transitions, voice/no-op, invalid targets and gesture/readback failures passed')

for family in ('Volume','Balance','Tinnitus'):
    for op, target in [('Up',3),('Down',1)]:
        p = phone(family,2); p.run('SIG3_' + family + op)
        assert p.level == target and not p.taps
    for op, target in ([('Sharp',7),('Soft',-8)] if family == 'Balance' else [('Max',15),('Mute',0)]):
        p = phone(family,2); p.run('SIG3_' + family + op)
        assert p.level == target and p.globals['SIG3_' + family + 'OK'] == '1'
p = phone('Volume',2); p.voice_event = 'set volume to ten'; p.run('SIG3_VoiceRouter')
assert p.level == 10 and p.globals['SIG3_CommandOK'] == '1'
print('Numeric wrapper endpoints and AutoVoice event routing passed')

for command in ['tin four','set tin to four','change tin to four']:
    p=phone('Tinnitus',2);p.run('SIG3_VoiceRouter',command)
    assert p.level==4 and p.globals['SIG3_CommandOK']=='1'
p=phone('Tinnitus',2);p.run('SIG3_VoiceRouter','current tin')
assert p.level==2 and not p.drags and p.globals['SIG3_Family']=='Tinnitus'
print('Tin shorthand routes numeric changes and current query to tinnitus.')

# Direct volume requests use a single stroke and stop on an unexpected readback.
for start in range(16):
    for target in range(16):
        p=phone('Volume',start);p.globals['SIG3_VolumeDragMode']='direct'
        p.run('SIG3_VolumeSet',str(target))
        assert p.level==target and p.globals['SIG3_CommandOK']=='1', (start,target,p.globals)
        assert len(p.drags)==int(start!=target), (start,target,p.drags)
p=phone('Volume',5,jump=2);p.globals['SIG3_VolumeDragMode']='direct';p.run('SIG3_VolumeSet','9')
assert p.globals['SIG3_CommandOK']=='0' and len(p.drags)==1
print('Direct volume: 256 transitions, single stroke, no-op and failed-readback stop passed.')

for family in ('Balance','Tinnitus'):
    levels=range(-8,8) if family=='Balance' else range(16)
    for start in levels:
        for target in levels:
            p=phone(family,start);p.globals['SIG3_'+family+'DragMode']='direct'
            p.run('SIG3_'+family+'Set',str(target))
            assert p.level==target and p.globals['SIG3_CommandOK']=='1', (family,start,target,p.globals)
            assert len(p.drags)==int(start!=target)
    p=phone(family,0,jump=2);p.globals['SIG3_'+family+'DragMode']='direct';p.run('SIG3_'+family+'Set','3')
    assert p.globals['SIG3_CommandOK']=='0' and len(p.drags)==1
print('Direct balance/tinnitus: 512 transitions and failed-readback stops passed')

p=phone('Tinnitus',0);p.globals['SIG3_VolumeDragMode']='direct';p.run('SIG3_TinnitusSet','3')
assert len(p.drags)==3, 'Volume direct mode must not enable another family'
print('Per-family direct mode remains independent')
