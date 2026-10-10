"""Remaining parity flow checks against exported Tasker actions."""
from check_sig3_migration import phone
p=phone()
p.globals.update(SIG3_ModeConversationProgram='1',SIG3_ModeNoisyProgram='2',SIG3_ModeVeryNoisyProgram='3')
for phrase,expected in [('sig conversation','Universal'),('mode noisy','Music'),('sig vnoisy','Outdoor')]:
    p.run('SIG3_VoiceRouter',phrase); assert p.program==expected and p.globals['SIG3_CommandOK']=='1'
p.run('SIG3_OverrideToggle'); assert p.globals['SIG3_ManualOverride']=='1'
p.run('SIG3_VoiceRouter','override toggle'); assert p.globals['SIG3_ManualOverride']=='0'
p.prompt_response='Music'; p.run('SIG3_VoiceMode'); assert p.program=='Music'
p.prompt_response='battery check'; p.run('SIG3_VoiceBattery'); assert 'battery checks requested' in p.globals['SIG3_Observed']
p.prompt_response=''; previous=p.program; p.run('SIG3_VoiceMode'); assert p.program==previous
p.globals.update(SIG3_NoiseEnabled='1',SIG3_NoiseScaleConfirmed='1',SIG3_NoiseLow='40',SIG3_NoiseHigh='60',SIG3_NoiseStrikeLimit='2',SIG3_NoiseQuietProgram='1',SIG3_NoiseMiddleProgram='2',SIG3_NoiseLoudProgram='3')
p.run('SIG3_ProgramSwitch','1')
p.run('SIG3_NoiseMonitor','50'); assert p.program=='Universal'
p.run('SIG3_NoiseMonitor','50'); assert p.program=='Music'
p.run('SIG3_CancelAutomation')
for i in range(3): p.run('SIG3_NoiseMonitor','70')
assert p.program=='Music' and p.globals['SIG3_CommandOK']=='0'
p.run('SIG3_ResumeAutomation'); p.run('SIG3_NoiseMonitor','70'); assert p.program=='Outdoor'
p.globals['SIG3_NoiseSource']='watch'; p.run('SIG3_WatchNoise','20'); p.run('SIG3_WatchNoise','20'); assert p.program=='Universal'
p.run('SIG3_LegacyCommand','SIG_ProgramSwitch','2'); assert p.program=='Music'
p.run('SIG3_LegacyCommand','SIG_VolumeSet','10'); assert p.level==10
p.run('SIG3_LegacyCommand','SIG_VolumeUp'); assert p.level==10
print('Prompted workflows, aliases, toggle, three tiers, cancellation/resume and watch samples passed.')
