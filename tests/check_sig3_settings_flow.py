"""Generated Save/Restore control flow, serialization and voice routing."""
from heysig3_runtime import Phone
import copy

def phone():
 p=Phone(4)
 for i,n in enumerate(p.programs,1):p.globals['SIG3_ProgramName'+str(i)]=n
 for f in ['Volume','Balance','Tinnitus']:
  p.globals['SIG3_'+f+'KnobId']='volume-knob';p.globals['SIG3_'+f+'StepPx']='40';p.globals['SIG3_'+f+'Direction']='1'
 p.globals['SIG3_KnobId']='volume-knob'
 return p
p=phone();p.run('SIG3_SaveSettings');assert p.globals['SIG3_CommandOK']=='1',p.globals
saved=copy.deepcopy(p.settings_snapshot);assert not p.drags and not p.progress_actions
p.program=p.program_capture='TV';p.level=3;p.run('SIG3_RestoreSettings')
assert p.globals['SIG3_CommandOK']=='1' and p.program=='Universal' and p.level==4,p.globals
assert p.settings_snapshot==saved and p.globals['SIG3_Family']=='Settings'
assert p.globals['SIG3_SettingsExpectedProgram']==''
p.run('SIG3_RestoreSettings');assert p.globals['SIG3_CommandOK']=='1'
assert len(p.drags)==1,'Repeated restore should be a numeric no-op'
for phrase in ['save settings','restore settings']:
 p=phone();p.run('SIG3_SaveSettings');p.run('SIG3_VoiceRouter',phrase)
 assert p.globals['SIG3_VoiceMatched']=='1' and p.globals['SIG3_CommandOK']=='1',p.globals
p=phone();p.run('SIG3_RestoreSettings');assert p.globals['SIG3_CommandOK']=='0' and not p.drags and 'snapshot retained' in p.globals['SIG3_Error']
p=phone();p.tinnitus_available=False;p.run('SIG3_SaveSettings');assert p.globals['SIG3_CommandOK']=='1' and p.settings_snapshot['controls']['Tinnitus'] is None
p.level=3;p.run('SIG3_RestoreSettings');assert p.globals['SIG3_CommandOK']=='1' and p.level==4
p=phone();p.run('SIG3_SaveSettings');saved=copy.deepcopy(p.settings_snapshot);p.tinnitus_available=False;p.level=3;p.run('SIG3_RestoreSettings')
assert p.globals['SIG3_CommandOK']=='0' and p.level==4 and 'Partial restore' in p.globals['SIG3_Error'] and p.settings_snapshot==saved
p=phone();p.run('SIG3_SaveSettings');p.globals['SIG3_ProgramName1']='Renamed';p.level=3;p.run('SIG3_RestoreSettings');assert p.globals['SIG3_CommandOK']=='0' and not p.drags
p=phone();p.run('SIG3_SaveSettings');saved=copy.deepcopy(p.settings_snapshot);p.settings_fail_mode='verify-program';p.level=3;p.run('SIG3_RestoreSettings')
assert p.globals['SIG3_CommandOK']=='0' and not p.drags and p.settings_snapshot==saved
p=phone();p.active=['SIG3_Worker'];p.run('SIG3_SaveSettings');assert not hasattr(p,'settings_snapshot')
print('Settings control flow passed: save/readback, serialized restore, voice phrases, no-ops, missing tinnitus, mapping changes and retained snapshots after failure')

p=phone();p.run('SIG3_VolumeSet','5');assert p.settings_snapshot['controls']=={'Volume':5,'Balance':5,'Tinnitus':5},p.globals
p.run('SIG3_VolumeSet','6');assert p.settings_snapshot['controls']=={'Volume':6,'Balance':5,'Tinnitus':5}
assert p.globals['SIG3_Family']=='Volume' and p.globals['SIG3_Observed']=='6' and p.globals['SIG3_CommandOK']=='1'
saved=copy.deepcopy(p.settings_snapshot);p.run('SIG3_VolumeSet','6');p.run('SIG3_VolumeCurrent');assert p.settings_snapshot==saved
p.settings_fail_mode='commit';p.run('SIG3_VolumeSet','7');assert p.globals['SIG3_CommandOK']=='1' and p.globals['SIG3_Observed']=='7' and p.globals['SIG3_SettingsAutoError'] and p.settings_snapshot==saved
print('Automatic save passed: complete initial baseline, incremental latest value, result preservation, no-op/read exclusion and retained snapshot on save failure')

for family in ('Balance','Tinnitus'):
 p=phone();p.run('SIG3_SaveSettings');p.run('SIG3_'+family+'Set','5')
 expected={'Volume':4,'Balance':4,'Tinnitus':4};expected[family]=5
 assert p.settings_snapshot['controls']==expected,(family,p.settings_snapshot)
print('Balance and tinnitus changes update only their own saved value')
