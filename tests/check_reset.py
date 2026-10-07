"""Simulate independent controls, program renaming, and saved-setting restore."""
from check_volume import Phone, TASKS, ROOT
import re
import xml.etree.ElementTree as E

class Controls(Phone):
    def __init__(self):
        super().__init__(8)
        self.programs = ['Normal', 'Off just tinnitus', 'Noisy', 'Outdoor', 'TV', 'Very Noisy']
        self.program = self.programs[0]
        self.levels = {'Volume': 8, 'Balance': 0, 'Tinnitus': 0}
        self.active = None
        self.no_tinnitus = False

    def run(self, name, param='', param2=''):
        match = re.match(r'SIG_(Volume|Balance|Tinnitus)(?:Current|Up|Down|Set)$', name)
        family = match[1] if match else None
        previous, old_readable = self.active, self.readable
        if family:
            self.active = family
            if previous != family: self.level = self.levels[family]
            self.bounds = (-8, 7) if family == 'Balance' else (0, 15)
            if family == 'Tinnitus' and self.no_tinnitus: self.readable = False
        try:
            super().run(name, param, param2)
        finally:
            if family: self.levels[family] = self.level
            self.active, self.readable = previous, old_readable
            if family and previous and previous != family:
                self.level = self.levels[previous]

p = Controls()
p.globals['SIG_Mode'] = 'noisy'
p.run('SIG_ProgramSwitch', 'keep_open')
assert p.program == 'Noisy' and p.globals['SIG_ProgramKey'] == 'noisy'
p.levels.update(Volume=9, Balance=-2, Tinnitus=4)
p.run('SIG_SaveSettings', 'keep_open')
assert p.globals['SIG_SaveOK'] == '1'
assert p.globals['SIG_PreferredProgram'] == 'noisy'
# Simulate charging/reset, then rename the app label and update its one mapping.
p.program = 'Normal'
p.levels.update(Volume=8, Balance=0, Tinnitus=0)
p.programs[2] = 'Busy Places'
p.globals['SIG_Program3'] = 'Busy Places'
p.run('SIG_Reset', 'keep_open')
assert p.globals['SIG_ResetOK'] == '1'
assert p.program == 'Busy Places' and not p.closed
assert p.levels == {'Volume': 9, 'Balance': -2, 'Tinnitus': 4}
p.run('SIG_ConfigurePrograms')
assert p.globals['SIG_Program3'] == 'Busy Places'
q = Controls()
q.run('SIG_Reset')
assert q.globals['SIG_ResetOK'] == '0' and not q.drags
q.globals['SIG_ProgramKey'] = 'normal'
q.no_tinnitus = True
q.run('SIG_SaveSettings', 'keep_open')
assert q.globals['SIG_SaveOK'] == '1' and q.globals['SIG_RestoreTinnitus'] == '0'
q.run('SIG_Reset', 'keep_open')
assert q.globals['SIG_ResetOK'] == '1'
p.fail_stage = 'tab'
p.run('SIG_Reset', 'keep_open')
assert p.globals['SIG_ResetOK'] == '0'
for name in ['ConfigurePrograms', 'SaveSettings', 'Reset', 'ProgramSwitch']:
    task = E.parse(ROOT / 'tasks' / f'SIG_{name}.tsk.xml').getroot().find('Task')
    project = TASKS['SIG_' + name]
    task.tail = project.tail = None
    assert E.tostring(task) == E.tostring(project)
print('Passed: stable program keys, renamed labels, saved settings, post-charge reset, missing preferences, optional tinnitus and failures.')
