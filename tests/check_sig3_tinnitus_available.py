"""Unavailable tinnitus controls must stop before clicks, drags or progress actions."""
from heysig3_runtime import Phone

for backend in ('legacy-gesture', 'accessibility'):
    for operation in ('Current', 'Up', 'Down', 'Set', 'Max', 'Mute', 'Inspect'):
        p = Phone(0)
        p.program = p.program_capture = 'TV'
        p.tinnitus_available = False
        p.globals.update(SIG3_SliderBackend=backend, SIG3_TinnitusKnobId='volume-knob',
                         SIG3_TinnitusStepPx='87', SIG3_TinnitusDirection='1')
        p.run('SIG3_Tinnitus' + operation, '1' if operation == 'Set' else '')
        assert p.globals['SIG3_CommandOK'] == '0', (backend, operation, p.globals)
        assert 'Tinnitus unavailable for this program' in p.globals['SIG3_Error'], p.globals
        assert p.level == 0 and not p.drags and not p.taps and not p.progress_actions
        assert p.globals['SIG3_TinnitusAvailable'] == '0'
p = Phone(0)
p.tinnitus_available = False
p.globals.update(SIG3_TinnitusKnobId='volume-knob', SIG3_TinnitusStepPx='87', SIG3_TinnitusDirection='1')
p.run('SIG3_VoiceRouter', 'tinnitus one')
assert p.globals['SIG3_CommandOK'] == '0' and not p.drags and not p.taps
# Capability, rather than a program-name allowlist, decides availability.
p = Phone(0)
p.program = p.program_capture = 'TV'
p.globals.update(SIG3_TinnitusKnobId='volume-knob', SIG3_TinnitusStepPx='87', SIG3_TinnitusDirection='1')
p.run('SIG3_TinnitusSet', '1')
assert p.globals['SIG3_CommandOK'] == '1' and p.level == 1
print('Tinnitus availability: all operations and voice stop without movement when the tab is absent; visible tabs remain usable.')
