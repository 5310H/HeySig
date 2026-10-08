"""Priority 3 exported flow checks with modeled Android/plugin effects."""
from heysig3_runtime import Phone

def phone():
    p = Phone(7)
    p.globals.update(SIG3_AudioStream='media', SIG3_KnobId='volume-knob',
                     SIG3_ProgramName1='Universal', SIG3_ProgramName2='Music',
                     SIG3_ProgramName3='Outdoor')
    p.run('SIG3_Init')
    return p

p = phone(); assert p.globals['SIG3_NoiseEnabled'] == p.globals['SIG3_SleepEnabled'] == '0'
p.globals['SIG3_NoiseStrikeLimit'] = '5'; p.run('SIG3_Init'); assert p.globals['SIG3_NoiseStrikeLimit'] == '5'
p.run('SIG3_ProgramSwitch','2'); assert p.program == 'Music' and p.globals['SIG3_CommandOK'] == '1'
p.run('SIG3_ProgramSwitch','6'); assert p.program == 'Music' and p.globals['SIG3_CommandOK'] == '0'
p.run('SIG3_VoiceRouter','program one'); assert p.program == 'Universal'
p.run('SIG3_VoiceRouter','change program to music'); assert p.program == 'Music'
p.voice_event='volume ten'; p.run('SIG3_AutoVoiceCommand'); assert p.level == 10
p.watch_event='sig3 volume nine'; p.run('SIG3_WatchCommand'); assert p.level == 9
p.run('SIG3_BatteryCheck'); assert p.globals['SIG3_CommandOK'] == '1' and '%' not in p.globals['SIG3_Observed']
p.run('SIG3_BatteryCheck','listen'); assert p.globals['SIG3_CommandOK'] == '0'
p.globals['SIG3_BatteryRequestId']='observed-button'; p.run('SIG3_BatteryCheck','listen'); assert p.globals['SIG3_CommandOK'] == '1'
p.noise_sample = -52; p.run('SIG3_CurrentNoise'); assert float(p.globals['SIG3_NoiseRaw']) == -52 and p.globals['SIG3_CommandOK'] == '1'
# Sample-only default neither changes program nor assumes a sign convention.
p.run('SIG3_NoiseMonitor','-45'); assert p.globals['SIG3_NoiseIndex'] == '-45.0' and p.program == 'Music'
p.globals.update(SIG3_NoiseEnabled='1', SIG3_NoiseInvert='1', SIG3_NoiseLow='40', SIG3_NoiseHigh='60', SIG3_NoiseStrikeLimit='3', SIG3_NoiseQuietProgram='1', SIG3_NoiseLoudProgram='3')
p.run('SIG3_NoiseMonitor','-70'); assert p.globals['SIG3_CommandOK'] == '0'  # scale unconfirmed
p.globals['SIG3_NoiseScaleConfirmed']='1'
for i in range(2): p.run('SIG3_NoiseMonitor','-70'); assert p.program == 'Music'
p.run('SIG3_NoiseMonitor','-70'); assert p.program == 'Outdoor'
p.run('SIG3_NoiseMonitor','-50'); assert p.globals['SIG3_NoiseStrikes'] == '0'
p.run('SIG3_Override','1')
for i in range(4): p.run('SIG3_NoiseMonitor','-20')
assert p.program == 'Outdoor'
p.run('SIG3_SleepState','asleep'); assert p.globals['SIG3_CommandOK'] == '0'
p.run('SIG3_Override','0'); p.globals.update(SIG3_SleepEnabled='1', SIG3_SleepProgram='2', SIG3_WakeProgram='1')
p.run('SIG3_SleepState','asleep'); assert p.program == 'Music' and p.globals['SIG3_SleepActive'] == '1'
p.run('SIG3_SleepState','awake'); assert p.program == 'Universal' and p.globals['SIG3_SleepActive'] == '0'
p.run('SIG3_NoiseMonitor','bad'); assert p.globals['SIG3_CommandOK'] == '0'
print('Initialization, program/voice/watch, battery, noise hysteresis/override and sleep flow checks passed')
