"""Control flow checks; model action/commit separately, not actual Android execution."""
from heysig3_runtime import Phone

def phone(family):
    p = Phone(0 if family == 'Balance' else 7, bounds=(-8,7) if family == 'Balance' else (0,15))
    p.globals['SIG3_SliderBackend'] = 'accessibility'
    p.globals['SIG3_KnobId' if family == 'Volume' else 'SIG3_' + family + 'KnobId'] = 'volume-knob'
    return p

for family,target in [('Volume',10),('Balance',-3),('Tinnitus',5)]:
    p = phone(family); p.run('SIG3_' + family + 'Inspect')
    assert p.globals['SIG3_CommandOK'] == '1' and not p.progress_actions and not p.drags
    p.run('SIG3_' + family + 'Set',str(target))
    assert p.globals['SIG3_CommandOK'] == '0' and not p.progress_actions
    p.globals['SIG3_' + family + 'RangeConfirmed'] = '1'
    p.run('SIG3_' + family + 'Set',str(target))
    assert p.globals['SIG3_CommandOK'] == '0' and not p.progress_actions
    p.touch_exploration = True
    p.progress_commits = False
    p.run('SIG3_' + family + 'Set',str(target))
    assert p.globals['SIG3_CommandOK'] == '0' and p.progress_actions == [target]
    p.progress_commits = True
    p.run('SIG3_' + family + 'Set',str(target))
    assert p.globals['SIG3_CommandOK'] == '1' and p.level == target and not p.drags
    count = len(p.progress_actions)
    p.run('SIG3_' + family + 'Set',str(target))
    assert len(p.progress_actions) == count
    p.run('SIG3_' + family + 'Set','100')
    assert p.globals['SIG3_CommandOK'] == '0' and len(p.progress_actions) == count
p = phone('Volume'); p.touch_exploration = True
p.globals['SIG3_VolumeRangeConfirmed'] = '1'; p.progress_supported = False
p.run('SIG3_VolumeSet','10'); assert not p.progress_actions and p.globals['SIG3_CommandOK'] == '0'
print('Shared numeric action flow: inspection, prerequisites, accepted-without-change, targets, no-op and invalid inputs passed.')
