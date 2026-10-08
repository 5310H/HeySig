"""Validate Tasker control flow using simulated AutoInput and Signia UI."""
from pathlib import Path
import re
import json
import xml.etree.ElementTree as E
ROOT = Path(__file__).resolve().parents[1]
TASKS = {t.findtext('nme'): t for t in E.parse(ROOT / 'projects/HeySig3.prj.xml').getroot().findall('Task')}
class Phone:
    def __init__(self, level, threshold=24, jump=1, readable=True, bounds=(0, 15),
                 package='com.signia.rta', texts=None, fail_stage=None, coordinates=None, ids=None):
        self.level, self.threshold, self.jump, self.readable = level, threshold, jump, readable
        self.bounds, self.closed = bounds, False
        self.package, self.texts, self.fail_stage = package, texts, fail_stage
        self.coordinates, self.ids = coordinates, ids
        self.programs = ['Universal', 'Music', 'Outdoor', 'TV', 'Car', 'Speech']
        self.program = self.programs[0]
        self.globals, self.drags, self.taps = {}, [], []
        self.knob_x, self.knob_y0, self.gestures = 500, 1000, []
        self.active = []
        self.program_capture = 'Universal'
        self.wrong_control = False
        self.ui_checks = 0
        self.hook = None
    def run(self, name, param='', param2=''):
        if name in self.active:
            return False  # Tasker's default Abort New Task policy.
        self.active.append(name)
        self.globals['TRUN'] = ',' + ','.join(self.active) + ','
        self.globals['TIMEMS'] = '1791460800000'
        try:
            self._run(name, param, param2)
            return True
        finally:
            self.active.remove(name)
            self.globals['TRUN'] = ',' + ','.join(self.active) + ',' if self.active else ''

    def _run(self, name, param='', param2=''):
        local = {'par1': param, 'par2': param2, 'priority': '10'}
        if name in ('SIG_VoiceRouter', 'SIG3_VoiceRouter', 'SIG3_AutoVoiceCommand'): local['avcomm'] = getattr(self, 'voice_event', param)
        if name == 'SIG3_WatchCommand': local['awcomm'] = getattr(self, 'watch_event', param)
        if name == 'SIG_WatchCommand' and hasattr(self, 'watch_event'):
            local['awcomm'] = self.watch_event
        actions = sorted(TASKS[name].findall('Action'), key=lambda a: int(a.get('sr')[3:]))
        def get(key): return self.globals.get(key, '%' + key) if any(c.isupper() for c in key) else local.get(key, '%' + key)
        def put(key, value): (self.globals if any(c.isupper() for c in key) else local).__setitem__(key, str(value))
        def expand(text):
            text = text or ''
            for array in ('aitext', 'aicoordinates', 'aiid'):
                values = local.get(array + '_array', [])
                text = text.replace('%' + array + '(#)', str(len(values)))
                text = re.sub(r'%' + array + r'\((%[A-Za-z_][A-Za-z_0-9]*|[0-9]+)\)',
                              lambda m: values[int(expand(m[1])) - 1] if 0 < int(expand(m[1])) <= len(values) else m[0], text)
            text = text.replace('%aitext()', local.get('aitext', '%aitext()'))
            return re.sub(r'%([A-Za-z_][A-Za-z_0-9]*)', lambda m: str(get(m[1])), text)
        def arg(a, n): return a.findtext(f"Str[@sr='arg{n}']", '')
        def test(a):
            c = a.find('./ConditionList/Condition'); lhs, rhs = expand(c.findtext('lhs')), expand(c.findtext('rhs'))
            op = int(c.findtext('op'))
            if op in (2, 3):
                # Tasker's simple Matches treats slash as OR, not a literal.
                negate = rhs.startswith('!')
                pattern = rhs[1:] if negate else rhs
                flags = 0 if any(c.isupper() for c in pattern) else re.I
                matched = not pattern or any(re.fullmatch(re.escape(part).replace(r'\*', '.*').replace(r'\+', '.+'), lhs, flags) for part in pattern.split('/'))
                matched = not matched if negate else matched
                return matched if op == 2 else not matched
            if op in (12, 13):
                is_set = bool(lhs) and lhs != c.findtext('lhs')
                return is_set if op == 12 else not is_set
            if op in (4, 5):
                # Translate Java Pattern.quote sections for Python's regex engine.
                rhs = re.sub(r'\\Q(.*?)\\E', lambda m: re.escape(m[1]), rhs)
                return bool(re.search(rhs, lhs)) == (op == 4)
            if op == 6: return float(lhs) < float(rhs)
            if op == 7: return float(lhs) > float(rhs)
            if op == 8: return float(lhs) == float(rhs)
            if op == 9: return float(lhs) != float(rhs)
            raise AssertionError(op)
        if_stack, loops, pc, budget = [], [], 0, 10000
        while pc < len(actions):
            budget -= 1
            assert budget > 0, 'Unbounded task'
            a = actions[pc]; code = int(a.findtext('code'))
            if code == 37:
                if_stack.append(all(if_stack) and test(a)); pc += 1; continue
            if code == 43:
                if_stack[-1] = all(if_stack[:-1]) and not if_stack[-1]; pc += 1; continue
            if code == 38:
                if_stack.pop(); pc += 1; continue
            if not all(if_stack): pc += 1; continue
            if code in (20, 15355, 107361459, 778682267, 474):
                local.pop('err', None)
                stage = {20: 'launch', 15355: 'query', 778682267: 'gesture', 474: 'gesture'}.get(code)
                if code == 474 and 'dispatchGesture' not in arg(a, 0): stage = 'ui' if 'Read-only live UI guard' in arg(a, 0) else 'phone' if 'Read-only preflight' in arg(a, 0) else 'report'
                if code == 107361459:
                    params = a.findtext('./Bundle/Vals/parameters', '')
                    stage = 'tab' if 'Tab)' in params else 'number'
                if self.fail_stage == 'halt_' + str(stage):
                    return  # Emulate a plugin/Tasker halt before its error guard.
                if code == 474 and 'dispatchGesture' in arg(a, 0) and self.fail_stage in ('missing_service', 'hold_rejected', 'hold_cancelled', 'hold_timeout', 'move_rejected', 'move_cancelled', 'move_timeout'):
                    phase = 'down-hold' if self.fail_stage.startswith('hold_') else 'move-up'
                    reasons = {'missing_service': 'Enable Tasker in Android Settings > Accessibility > Installed apps',
                               'rejected': 'dispatchGesture rejected', 'cancelled': 'Android cancelled gesture',
                               'timeout': 'completion timed out after 3000 ms'}
                    reason = reasons['missing_service'] if self.fail_stage == 'missing_service' else phase + ': ' + reasons[self.fail_stage.split('_')[1]]
                    local['err'], local['errmsg'] = '1', reason
                    pc += 1; continue
                if stage == self.fail_stage:
                    assert a.findtext('se') == 'true'
                    local['err'], local['errmsg'] = '1', 'Injected plugin failure'
                    pc += 1; continue
            if code == 137: return
            if code == 547:
                value = expand(arg(a, 1))
                if a.find("Int[@sr='arg3']").get('val') == '1': value = str(int(eval(value, {'__builtins__': {}}, {})))
                put(arg(a, 0)[1:], value)
            elif code == 590:
                key = arg(a, 0)[1:]
                for n, value in enumerate(str(get(key)).split(arg(a, 1)), 1): put(key + str(n), value)
            elif code == 130:
                local.pop('err', None)
                if not self.run(expand(arg(a, 0)), expand(arg(a, 2)), expand(arg(a, 3))):
                    local['err'], local['errmsg'] = '1', 'Task already running'

            elif code == 39:
                items = expand(arg(a, 1)); values = list(map(str, range(int(items.split(':')[0]), int(items.split(':')[1]) + 1))) if ':' in items else items.split(',')
                assert values
                loops.append([pc, arg(a, 0)[1:], values, 0]); put(loops[-1][1], values[0])
            elif code == 40:
                start, key, values, idx = loops[-1]
                if idx + 1 < len(values):
                    loops[-1][3] += 1; put(key, values[idx + 1]); pc = start + 1; continue
                loops.pop()
            elif code == 15355:
                local['aipackage'] = self.package
                default_text = f'Volume Tab,15,{self.level},0' if self.readable else 'Volume Tab'
                local['aitext'] = self.texts if self.texts is not None else default_text
                local['aitext_array'] = local['aitext'].split(',')
                local['aicoordinates_array'] = list(self.coordinates if self.coordinates is not None else (['100,200', '650,400', f'{self.knob_x},{self.knob_y0-self.level*40}', '650,1000'] if self.readable else ['100,200']))
                local['aiid_array'] = list(self.ids if self.ids is not None else (['tab', 'maximum-label', 'volume-knob', 'minimum-label'] if self.readable else ['tab']))
            elif code == 107361459:
                local['ailastcoordinates'] = '500,800'
                action = expand(json.loads(a.findtext('./Bundle/Vals/parameters'))['_action'])
                if action.startswith('click(point,'):
                    point = action[len('click(point,'):-1].replace('\\', '')
                    assert point == f'{self.knob_x},{self.knob_y0-self.level*40}', ('Tapped endpoint instead of knob', point, self.level)
                    self.taps.append(point)
                if action.startswith('click(text,'):
                    value = action[len('click(text,'):-1]
                    if value in self.programs: self.program = value
                    elif '%requested_program' in a.findtext('./Bundle/Vals/parameters'):
                        local['err'], local['errmsg'] = '1', 'Program not found'
            elif code == 474:
                # Model the touch result; Android/BeanShell execution is a separate check.
                script = arg(a, 0)
                if 'dispatchGesture' not in script:
                    if 'Program selection through visible' in script:
                        slot = get('par1')
                        target = self.globals.get('SIG3_ProgramName' + slot)
                        if not target or target not in self.programs:
                            local['err'], local['errmsg'] = '1', 'Program not configured or unavailable'
                        else:
                            self.globals['SIG3_Previous'] = self.program
                            self.program = self.program_capture = target
                            self.globals['SIG3_Observed'] = target
                            self.globals['SIG3_Program'] = target
                    elif 'Opens battery UI' in script:
                        if get('par1') == 'listen' and not self.globals.get('SIG3_BatteryRequestId'):
                            local['err'], local['errmsg'] = '1', 'Configure battery request ID'
                        else:
                            self.globals['SIG3_BatteryText'] = 'Acoustic battery indication'
                            self.globals['SIG3_Observed'] = 'Battery page opened; no percentage inferred'
                    elif 'Sample indices are not calibrated' in script:
                        try:
                            raw = float(get('sig3_noise_raw'))
                            value = -raw if self.globals.get('SIG3_NoiseInvert') == '1' else raw
                            self.globals.update(SIG3_NoiseRaw=str(raw), SIG3_NoiseIndex=str(value), SIG3_AutoProgramSlot='', SIG3_Observed='Uncalibrated noise index ' + str(value))
                            if self.globals.get('SIG3_NoiseEnabled') == '1':
                                if self.globals.get('SIG3_NoiseScaleConfirmed') != '1': raise ValueError('Confirm noise scale')
                                if self.globals.get('SIG3_ManualOverride') == '1':
                                    self.globals.update(SIG3_NoiseStrikes='0', SIG3_NoiseCandidate='')
                                elif self.globals.get('SIG3_SleepActive') != '1':
                                    low, high = float(self.globals['SIG3_NoiseLow']), float(self.globals['SIG3_NoiseHigh'])
                                    limit = int(self.globals.get('SIG3_NoiseStrikeLimit','3'))
                                    if low >= high or limit < 1 or limit > 20: raise ValueError('Invalid thresholds')
                                    tier = 'loud' if value >= high else 'quiet' if value <= low else 'middle'
                                    if tier == 'middle': self.globals.update(SIG3_NoiseStrikes='0',SIG3_NoiseCandidate='')
                                    else:
                                        strikes = min(limit, int(self.globals.get('SIG3_NoiseStrikes','0')) + 1) if self.globals.get('SIG3_NoiseCandidate') == tier else 1
                                        self.globals.update(SIG3_NoiseStrikes=str(strikes),SIG3_NoiseCandidate=tier)
                                        if strikes == limit:
                                            slot = self.globals.get('SIG3_NoiseLoudProgram' if tier == 'loud' else 'SIG3_NoiseQuietProgram')
                                            if slot not in ('1','2','3','4','5','6'): raise ValueError('Configure noise program')
                                            self.globals['SIG3_AutoProgramSlot'] = slot
                        except (ValueError, KeyError): local['err'], local['errmsg'] = '1', 'Noise configuration/sample invalid'
                    elif 'No command text supplied by event' in script:
                        value = get('sig3_input')
                        if value.startswith('%'): local['err'], local['errmsg'] = '1', 'No input'
                        else: put('sig3_input', re.sub(r'(?i)^sig3\s+', '', value.strip()))
                    elif 'Read-only live UI guard' in script:
                        self.ui_checks += 1
                        baseline = self.globals.get('SIG3_Program', '')
                        if self.wrong_control or (baseline and baseline != self.program_capture):
                            local['err'], local['errmsg'] = '1', 'Wrong control or program changed'
                        else:
                            self.globals['SIG3_Program'] = self.program_capture
                    elif 'Read-only preflight' in script:
                        self.globals['SIG3_AudioDiagnostics'] = 'stream=media volume=10/15; outputs=speaker'
                    pc += 1; continue
                if self.hook:
                    hook, self.hook = self.hook, None
                    hook(self)
                assert 'holdStroke.continueStroke(movePath, 0, 300, false)' in script
                self.gestures.append((f"{get('sig3_x')},{get('sig3_y')}", f"{get('sig3_x')},{get('sig3_end_y')}", '200+300'))
                distance = float(get('sig3_y')) - float(get('sig3_end_y'))
                assert 1 <= abs(distance) <= 200
                self.drags.append(distance)
                put('SIG3_TouchStage', 'released')
                if abs(distance) >= self.threshold: self.level = max(self.bounds[0], min(self.bounds[1], self.level + (self.jump if distance > 0 else -self.jump)))
            elif code == 778682267:
                params = json.loads(a.findtext('Bundle/Vals/parameters'))
                self.gestures.append((expand(params['initialPoint']), expand(params['endPoint']), expand(params['duration'])))
                if name == 'SIG3_VolumeUp':
                    if any(not re.fullmatch(r'[0-9]+,[0-9]+', point) for point in self.gestures[-1][:2]):
                        local['err'], local['errmsg'] = '1', 'Points are invalid'
                        pc += 1; continue
                    assert self.gestures[-1] == (f"{get('sig3_x')},{get('sig3_y')}", f"{get('sig3_x')},{get('sig3_end_y')}", '600')
                    # Mirror installed Point(String): exactly two comma-separated integers.
                    for point in self.gestures[-1][:2]:
                        assert len(point.split(',')) == 2
                        tuple(int(part) for part in point.split(','))
                else:
                    assert self.gestures[-1] == (f"Start X: {get('sig3_x')}\nStart Y: {get('sig3_y')}", f"End X: {get('sig3_x')}\nEnd Y: {get('sig3_end_y')}", '300')
                distance = float(get('sig3_y')) - float(get('sig3_end_y'))
                self.drags.append(distance)
                if abs(distance) >= self.threshold: self.level = max(self.bounds[0], min(self.bounds[1], self.level + (self.jump if distance > 0 else -self.jump)))
            elif code == 18: self.closed = True
            elif code == 25: self.closed = True
            elif code == 1218739680:
                local['avnoiselevel'] = str(getattr(self, 'noise_sample', -45))
            else: assert code in (20, 18, 25, 30, 548), code
            pc += 1
        assert not if_stack and not loops
