"""Retry recognition after an explicit choice; never repeat a routed command."""
from check_sig3_migration import phone

for first in ['', 'please do something', 'program elephant']:
    p = phone()
    p.prompt_responses = [first, 'program too']
    p.retry_choices = ['retry']
    p.run('SIG3_VoiceCommand')
    assert p.program == 'Music' and p.globals['SIG3_CommandOK'] == '1'
    assert p.retry_dialogs == 1 and not p.prompt_responses

for choice in ['cancel', 'timeout', 'back']:
    p = phone()
    p.globals['SIG3_CommandOK'] = '1'  # A previous success must not survive failure.
    p.prompt_response = 'unrecognized command'
    p.retry_choices = [choice]
    p.run('SIG3_VoiceCommand')
    assert p.program == 'Universal' and not p.gestures
    assert p.globals['SIG3_CommandOK'] == '0' and p.retry_dialogs == 1

p = phone()
p.prompt_responses = ['current program', 'program two']
p.run('SIG3_VoiceCommand')
assert p.program == 'Universal' and p.prompt_responses == ['program two']
assert getattr(p, 'retry_dialogs', 0) == 0

p = phone()
p.globals['SIG3_ProgramName2'] = 'Missing program'
p.prompt_response = 'program two'
p.run('SIG3_VoiceCommand')
assert p.globals['SIG3_CommandOK'] == '0' and getattr(p, 'retry_dialogs', 0) == 0
print('Missed/unrecognized speech retries only by choice; cancel clears stale success; routed success/failure never repeats.')

for family in ("Volume","Balance","Tinnitus"):
    p=phone(); before=(p.program,p.level,len(p.gestures))
    p.globals.update(SIG3_BalanceKnobId='volume-knob',SIG3_TinnitusKnobId='volume-knob')
    p.prompt_response="current "+family.lower(); p.run("SIG3_VoiceCommand")
    assert p.globals["SIG3_CommandOK"]=="1" and p.globals["SIG3_Family"]==family
    assert (p.program,p.level,len(p.gestures))==before and getattr(p,"retry_dialogs",0)==0
print("Current volume/balance/tinnitus voice queries read without movement or retry.")
