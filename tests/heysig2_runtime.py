"""Validate Tasker control flow using simulated AutoInput and Signia UI."""
from pathlib import Path
import re
import json
import xml.etree.ElementTree as E
ROOT = Path(__file__).resolve().parents[1]
TASKS = {t.findtext('nme'): t for t in E.parse(ROOT / 'projects/HeySig2.prj.xml').getroot().findall('Task')}
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
    def run(self, name, param='', param2=''):
        local = {'par1': param, 'par2': param2, 'priority': '10'}
        if name == 'SIG_VoiceRouter': local['avcomm'] = getattr(self, 'voice_event', param)
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
            if code in (20, 15355, 107361459, 778682267):
                local.pop('err', None)
                stage = {20: 'launch', 15355: 'query', 778682267: 'gesture'}.get(code)
                if code == 107361459:
                    params = a.findtext('./Bundle/Vals/parameters', '')
                    stage = 'tab' if 'Tab)' in params else 'number'
                if self.fail_stage == 'halt_' + str(stage):
                    return  # Emulate a plugin/Tasker halt before its error guard.
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
            elif code == 130: self.run(expand(arg(a, 0)), expand(arg(a, 2)), expand(arg(a, 3)))
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
            elif code == 778682267:
                params = json.loads(a.findtext('Bundle/Vals/parameters'))
                self.gestures.append((expand(params['initialPoint']), expand(params['endPoint']), expand(params['duration'])))
                if name == 'SIG2_VolumeUp':
                    if any(not re.fullmatch(r'[0-9]+,[0-9]+', point) for point in self.gestures[-1][:2]):
                        local['err'], local['errmsg'] = '1', 'Points are invalid'
                        pc += 1; continue
                    assert self.gestures[-1] == (f"{get('sig2_x')},{get('sig2_y')}", f"{get('sig2_x')},{get('sig2_end_y')}", '300')
                    # Mirror installed Point(String): exactly two comma-separated integers.
                    for point in self.gestures[-1][:2]:
                        assert len(point.split(',')) == 2
                        tuple(int(part) for part in point.split(','))
                else:
                    assert self.gestures[-1] == (f"Start X: {get('sig2_x')}\nStart Y: {get('sig2_y')}", f"End X: {get('sig2_x')}\nEnd Y: {get('sig2_end_y')}", '300')
                distance = float(get('sig2_y')) - float(get('sig2_end_y'))
                self.drags.append(distance)
                if abs(distance) >= self.threshold: self.level = max(self.bounds[0], min(self.bounds[1], self.level + (self.jump if distance > 0 else -self.jump)))
            elif code == 18: self.closed = True
            elif code == 25: self.closed = True
            elif code == 1218739680:
                local['avnoiselevel'] = str(self.noise_sample)
            else: assert code in (20, 18, 25, 30, 548), code
            pc += 1
        assert not if_stack and not loops
