"""Static Tasker XML checks; not a substitute for Tasker's Android parser."""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'tests/fixtures/tasker-action-codes.json').read_text())
codes = catalog['codes']
issues = []
files = [ROOT / 'projects/HeySig3.prj.xml', *sorted((ROOT / 'tasks').glob('SIG3_*.tsk.xml'))]
actions_count = 0

def issue(path, where, message):
    issues.append(f'{path.relative_to(ROOT)} — {where}: {message}')

required = {
    18: {'arg0': 'App', 'arg1': 'Int'},
    20: {'arg0': 'App', 'arg1': 'Str', 'arg2': 'Int', 'arg3': 'Int'},
    25: {'arg0': 'Int'},
    30: {f'arg{i}': 'Int' for i in range(5)},
    39: {'arg0': 'Str', 'arg1': 'Str', 'arg2': 'Int'},
    130: {'arg0': 'Str', 'arg1': 'Int', 'arg2': 'Str', 'arg3': 'Str'},
    137: {'arg0': 'Int', 'arg1': 'Str'},
    474: {'arg0': 'Str', 'arg1': 'Str', 'arg2': 'Int'},
    547: {'arg0': 'Str', 'arg1': 'Str', **{f'arg{i}': 'Int' for i in range(2, 7)}},
    548: {'arg0': 'Str', 'arg1': 'Int'},
    590: {'arg0': 'Str', 'arg1': 'Str'},
}
for path in files:
    try: root = E.parse(path).getroot()
    except E.ParseError as ex:
        issue(path, 'document', str(ex)); continue
    if root.tag != 'TaskerData':
        issue(path, 'document', 'root is not TaskerData'); continue
    tasks = root.findall('Task')
    ids = [t.findtext('id') for t in tasks]
    if len(ids) != len(set(ids)): issue(path, 'document', 'duplicate task IDs')
    for t in tasks:
        name = t.findtext('nme', t.get('sr', 'unnamed'))
        if not (t.findtext('id') or '').isdigit():
            issue(path, name, 'task id is not numeric')
        if t.get('sr') != 'task' + (t.findtext('id') or ''):
            issue(path, name, 'Task sr does not match id')
        aa = t.findall('Action')
        try: aa.sort(key=lambda a: int(a.get('sr', '')[3:]))
        except ValueError:
            issue(path, name, 'invalid Action sr'); continue
        indices = [int(a.get('sr')[3:]) for a in aa]
        if indices != list(range(len(aa))): issue(path, name, 'action numbers are not unique and contiguous')
        stack = []
        for condition in t.findall('.//Condition'):
            fields = [c.tag for c in condition]
            allowed = [['lhs', 'op', 'rhs']]
            if condition.findtext('op') in ('12', '13'):
                allowed.append(['lhs', 'op'])  # Original exports omit unary RHS.
            if fields not in allowed:
                issue(path, name, 'Condition has an incompatible field layout')
        for a in aa:
            actions_count += 1
            where = name + '/' + a.get('sr')
            try: code = int(a.findtext('code'))
            except (TypeError, ValueError):
                issue(path, where, 'invalid action code'); continue
            if code < 1000 and str(code) not in codes:
                issue(path, where, f'action code {code} absent from official definitions')
            args = [x for x in a if re.fullmatch(r'arg\d+', x.get('sr', ''))]
            slots = [x.get('sr') for x in args]
            if len(slots) != len(set(slots)): issue(path, where, 'duplicate argument slots')
            for slot, tag in required.get(code, {}).items():
                if a.find(f"{tag}[@sr='{slot}']") is None:
                    issue(path, where, f'missing {tag} {slot} in checked argument layout')
            if code == 547 and not re.fullmatch(r'%[A-Za-z][A-Za-z_0-9]*', a.findtext("Str[@sr='arg0']", '')):
                issue(path, where, 'Variable Set name is not a variable reference')
            if code == 37:
                stack.append('if')
                if a.find('ConditionList/Condition') is None: issue(path, where, 'If has no condition')
            elif code == 39: stack.append('for')
            elif code == 43:
                if not stack or stack[-1] != 'if': issue(path, where, 'Else outside If')
            elif code in (38, 40):
                expected = 'if' if code == 38 else 'for'
                if not stack or stack.pop() != expected: issue(path, where, 'mismatched control-flow end')
            if code >= 1000:
                vals = a.find("Bundle[@sr='arg0']/Vals")
                if vals is None:
                    issue(path, where, 'plugin action has no Bundle/Vals'); continue
                for slot in ('arg1', 'arg2'):
                    if not a.findtext(f"Str[@sr='{slot}']"):
                        issue(path, where, f'plugin {slot} missing package/config activity')
                param = vals.findtext('parameters')
                if param:
                    try: json.loads(param)
                    except json.JSONDecodeError as ex: issue(path, where, f'plugin parameters JSON: {ex}')
        if stack: issue(path, name, 'unclosed control-flow blocks')

report = '# Tasker XML static validation — 2026-10-08\n\n'
report += f'Checked {len(files)} XML files and {actions_count} task actions. Found {len(issues)} failures.\n\n'
report += 'Action numbers were compared with [Tasker’s official definitions](' + catalog['source'] + '). Checks include XML parsing, task IDs, action numbering, nested control flow, explicit condition fields, selected built-in argument layouts, plugin bundle presence, and JSON syntax.\n\n'
report += 'This is not full schema certification. Tasker has not parsed or executed these files here. The selected argument layouts are repository-derived checks, not an official XSD. Plugin settings, Android components, scene/profile layouts, unresolved external task references, and all remaining action arguments need runtime or authoritative format verification.\n\n'
report += '\n'.join('- ' + x for x in issues) + '\n'
(ROOT / 'docs/HeySig3-validation.md').write_text(report.rstrip() + '\n')
print(f'Checked {len(files)} XML files, {actions_count} task actions; {len(issues)} static failures.')
for x in issues: print(x)
sys.exit(bool(issues))
