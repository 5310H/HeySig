"""Build the isolated numeric-target project using native Tasker control flow.

Only low-level App/plugin argument envelopes are reused from reference exports;
all task control flow is new. Run from any directory with python3.
"""
from pathlib import Path
from copy import deepcopy
import json
import uuid
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
reference = E.parse(ROOT / 'tools/sig3-reference.tsk.xml').getroot()
templates = {code: next(a for a in reference.findall('.//Action') if a.findtext('code') == code)
             for code in ('20', '15355', '107361459', '778682267')}
STAMP = '1791396000000'


def action(code):
    a = E.Element('Action', sr='act0', ve='7')
    E.SubElement(a, 'code').text = str(code)
    return a


def string(a, i, text=''):
    E.SubElement(a, 'Str', sr=f'arg{i}', ve='3').text = text


def integer(a, i, val=0):
    E.SubElement(a, 'Int', sr=f'arg{i}', val=str(val))


def setvar(name, value, maths=False):
    a = action(547)
    string(a, 0, name); string(a, 1, str(value))
    for i, v in enumerate((0, int(maths), 0, 3, 1), 2): integer(a, i, v)
    return a


def condition(lhs, op, rhs=''):
    a = action(37)
    E.SubElement(a, 'coll').text = 'false'
    c = E.SubElement(E.SubElement(a, 'ConditionList', sr='if'), 'Condition', sr='c0', ve='3')
    for tag, text in [('lhs', lhs), ('op', str(op)), ('rhs', str(rhs))]: E.SubElement(c, tag).text = text
    return a


def call(name, param='', param2=''):
    a = action(130)
    string(a, 0, name)
    E.SubElement(E.SubElement(a, 'Int', sr='arg1'), 'var').text = '%priority+1'
    integer(a, 10, 1)
    for i in (2, 3, 4): string(a, i, param if i == 2 else param2 if i == 3 else '')
    for i in (5, 6): integer(a, i)
    string(a, 7)
    for i in (8, 9): integer(a, i)
    e = E.Element('se'); e.text = 'true'; a.insert(1, e)
    return a


def stop():
    a = action(137); integer(a, 0); string(a, 1); return a


def fail(message):
    return [setvar('%SIG3_VolumeOK', 0), setvar('%SIG3_Error', message), stop()]


def guard(lhs, op, rhs, message):
    return [condition(lhs, op, rhs), *fail(message), action(38)]


def wait(ms=300):
    a = action(30)
    for i, v in enumerate((ms, 0, 0, 0, 0)): integer(a, i, v)
    return a


def plugin(code, command=None):
    a = deepcopy(templates[str(code)])
    a.attrib = {'sr': 'act0', 've': '7'}
    # Stable instance identifiers make regeneration reproducible.
    vals = a.find('Bundle/Vals')
    if vals is not None:
        vals.find('plugininstanceid').text = str(uuid.uuid5(uuid.NAMESPACE_URL, 'HeySig3:' + str(code) + ':' + str(command)))
        if command is not None:
            params = json.loads(vals.findtext('parameters'))
            if str(code) == '107361459':
                params['_action'] = command
                vals.find('com.twofortyfouram.locale.intent.extra.BLURB').text = 'Actions To Perform: ' + command
            else:
                params.update(initialPoint='Start X: %sig3_x\nStart Y: %sig3_y',
                              endPoint='End X: %sig3_x\nEnd Y: %sig3_end_y', duration='300')
                if command == 'swipe_up':
                    # Installed AutoInput Point(String) splits two numbers on ','.
                    params.update(initialPoint='%sig3_x,%sig3_y', endPoint='%sig3_x,%sig3_end_y')
                    params = {k: params[k] for k in ('initialPoint', 'endPoint', 'duration')}
                    params['duration'] = '600'
                    for key in ('EnableDisableAccessibilityService', 'Password'):
                        for tag in (key, key + '-type'):
                            child = vals.find(tag)
                            if child is not None: vals.remove(child)
                vals.find('com.twofortyfouram.locale.intent.extra.BLURB').text = 'Swipe from %sig3_x,%sig3_y to %sig3_x,%sig3_end_y (600 ms)' if command == 'swipe_up' else 'Swipe from %sig3_x,%sig3_y to %sig3_x,%sig3_end_y (300 ms)'
            vals.find('parameters').text = json.dumps(params, separators=(',', ':'))
    se = a.find('se')
    if se is None: se = E.Element('se')
    else: a.remove(se)
    se.text = 'true'; a.insert(1, se)
    return a


def checked_plugin(code, command=None):
    return [plugin(code, command), *guard('%err', 12, '', 'AutoInput/launch failed: %errmsg')]


def loop(var, items):
    a = action(39); string(a, 0, var); string(a, 1, items); integer(a, 2, 1); return a


def split(var):
    a = action(590); string(a, 0, var); string(a, 1, ','); integer(a, 2); return a


def task(name, number, aa):
    t = E.Element('Task', sr=f'task{number}')
    for tag, value in [('cdate', STAMP), ('edate', STAMP), ('id', str(number)), ('nme', name), ('pri', '100')]:
        E.SubElement(t, tag).text = value
    for i, a in enumerate(aa): a.set('sr', f'act{i}'); t.append(a)
    return t


launch = [setvar('%SIG3_AppOK', 0), setvar('%SIG3_Error', ''), plugin(20),
          condition('%err', 12), setvar('%SIG3_Error', 'Signia launch failed: %errmsg'), stop(), action(38),
          wait(1000), *checked_plugin(15355),
          condition('%aipackage', 3, 'com.signia.rta'), setvar('%SIG3_Error', 'Signia is not foreground'), stop(), action(38),
          setvar('%SIG3_AppOK', 1)]

current = [setvar('%SIG3_VolumeOK', 0), setvar('%SIG3_Level', -1),
           setvar('%SIG3_VolumeX', -1), setvar('%SIG3_VolumeY', -1),
           condition('%par1', 3, 'query_only'), setvar('%SIG3_Error', ''), action(38),
           condition('%par1', 3, 'query_only'), call('SIG3_InternalAppLaunch'),
           *guard('%SIG3_AppOK', 3, 1, 'Signia launch did not complete'),
           *checked_plugin(107361459, 'click(text,Volume Tab)'), wait(), action(38),
           *checked_plugin(15355), *guard('%aipackage', 3, 'com.signia.rta', 'Signia is not foreground'),
           *guard('%aitext(#)', 6, 1, 'Empty UI Query text array'),
           setvar('%SIG3_QueryData', ''), loop('%sig3_dump_i', '1:%aitext(#)'),
           setvar('%SIG3_QueryData', '%SIG3_QueryData%sig3_dump_i | %aitext(%sig3_dump_i) | %aiid(%sig3_dump_i) | %aicoordinates(%sig3_dump_i)\n'),
           action(40),
           # Stable knob resource ID wins. Otherwise require a calibrated region.
           setvar('%sig3_mode', 'id'), condition('%SIG3_KnobId', 13), setvar('%sig3_mode', 'region')]
for name in ('XMin', 'XMax', 'YMin', 'YMax'):
    current += guard('%SIG3_Knob' + name, 5, r'^[0-9]+$', 'Configure SIG3_KnobId or all four knob region bounds first')
current += guard('%SIG3_KnobXMin', 7, '%SIG3_KnobXMax', 'Invalid knob X region')
current += guard('%SIG3_KnobYMin', 7, '%SIG3_KnobYMax', 'Invalid knob Y region')
current += [action(38), setvar('%sig3_count', 0),
            *guard('%aitext(#)', 6, 1, 'Empty UI Query text array'),
            *guard('%aitext(#)', 9, '%aicoordinates(#)', 'UI Query text/coordinate arrays are not aligned'),
            condition('%sig3_mode', 2, 'id'),
            *guard('%aitext(#)', 9, '%aiid(#)', 'UI Query text/id arrays are not aligned'), action(38),
            loop('%sig3_i', '1:%aitext(#)'), setvar('%sig3_text', '%aitext(%sig3_i)'),
            condition('%sig3_text', 4, r'^(?:[0-9]|1[0-5])$'),
            setvar('%sig3_point', '%aicoordinates(%sig3_i)'),
            condition('%sig3_point', 4, r'^[0-9]+,[0-9]+$'), split('%sig3_point'),
            setvar('%sig3_selected', 0),
            condition('%sig3_mode', 2, 'id'), condition('%aiid(%sig3_i)', 4, r'^\Q%SIG3_KnobId\E$'),
            setvar('%sig3_selected', 1), action(38), action(43), setvar('%sig3_selected', 1)]
for lhs, op, rhs in [('%sig3_point1', 6, '%SIG3_KnobXMin'), ('%sig3_point1', 7, '%SIG3_KnobXMax'),
                     ('%sig3_point2', 6, '%SIG3_KnobYMin'), ('%sig3_point2', 7, '%SIG3_KnobYMax')]:
    current += [condition(lhs, op, rhs), setvar('%sig3_selected', 0), action(38)]
current += [action(38), condition('%sig3_selected', 8, 1),
            setvar('%sig3_count', '%sig3_count + 1', True), setvar('%sig3_level', '%sig3_text'),
            setvar('%sig3_x', '%sig3_point1'), setvar('%sig3_y', '%sig3_point2'),
            action(38), action(38), action(38), action(40),
            *guard('%sig3_count', 9, 1, 'Knob selector matched zero or multiple numeric elements; inspect aligned UI Query data'),
            setvar('%SIG3_Level', '%sig3_level'), setvar('%SIG3_VolumeX', '%sig3_x'),
            setvar('%SIG3_VolumeY', '%sig3_y'), setvar('%SIG3_VolumeOK', 1)]


def hold_drag():
    # Schema captured from an actual Tasker 6.6.20 Java Code export.
    a = action(474)
    E.SubElement(a, 'se').text = 'true'
    string(a, 0, (ROOT / 'tools/sig3_hold_drag.java').read_text())
    string(a, 1)
    integer(a, 2, 1)
    return a


def family_current(family):
    aa = deepcopy(current)
    for a in aa:
        for node in a.iter():
            if node.text:
                node.text = node.text.replace('SIG3_Volume', 'SIG3_' + family).replace('Volume Tab', family + ' Tab').replace('SIG3_Knob', 'SIG3_' + family + 'Knob').replace('SIG3_Level', 'SIG3_' + family + 'Level')
                if family == 'Balance' and node.text == r'^(?:[0-9]|1[0-5])$':
                    node.text = r'^(?:-[1-8]|[0-7])$'
    return aa


def family_fail(family, message):
    return [setvar('%SIG3_' + family + 'OK', 0), setvar('%SIG3_Error', message), stop()]


def family_guard(family, lhs, op, rhs, message):
    return [condition(lhs, op, rhs), *family_fail(family, message), action(38)]


def target_set(family):
    lo, hi = (-8, 7) if family == 'Balance' else (0, 15)
    level = '%SIG3_Level' if family == 'Volume' else '%SIG3_' + family + 'Level'
    ok = '%SIG3_' + family + 'OK'
    step = '%SIG3_' + family + 'StepPx'
    direction = '%SIG3_' + family + 'Direction'
    g = lambda lhs, op, rhs, msg: family_guard(family, lhs, op, rhs, msg)
    aa = [setvar(ok, 0), setvar('%SIG3_Error', ''), setvar('%sig3_target', '%par1'),
          *g('%sig3_target', 5, r'^-?[0-9]+$', family + ' target must be an integer'),
          *g('%sig3_target', 6, lo, family + ' target below minimum'),
          *g('%sig3_target', 7, hi, family + ' target above maximum'),
          setvar('%SIG3_' + family + 'Target', '%sig3_target'), setvar('%SIG3_Target', '%sig3_target')]
    if family == 'Volume':
        aa += [condition(step, 13), setvar(step, 40), action(38), condition(direction, 13), setvar(direction, 1), action(38)]
    aa += [*g(direction, 5, r'^(?:1|-1)$', 'Configure calibrated direction: 1=up increases, -1=down increases'), *g(step, 5, r'^[0-9]+$', 'Measure and configure ' + step),
           *g(step, 6, 1, 'Invalid step distance'), *g(step, 7, 200, 'Invalid step distance'),
           call('SIG3_Internal' + family + 'Current'), *g(ok, 3, 1, family + ' initial query failed: %SIG3_Error'),
           loop('%sig3_iteration', '1:16'),
           condition(level, 8, '%sig3_target'), setvar(ok, 1), setvar('%SIG3_MoveStage', 'complete'), stop(), action(38),
           setvar('%sig3_start', level), setvar('%SIG3_Previous', level), setvar('%sig3_delta', 1),
           condition(level, 7, '%sig3_target'), setvar('%sig3_delta', -1), action(38),
           setvar('%sig3_expected', '%sig3_start + %sig3_delta', True), setvar('%SIG3_Expected', '%sig3_expected'),
           setvar('%sig3_x', '%SIG3_' + family + 'X'), setvar('%sig3_y', '%SIG3_' + family + 'Y'),
           setvar('%sig3_end_y', '%sig3_y - %sig3_delta * ' + step + ' * ' + direction, True),
           setvar(ok, 0), setvar('%SIG3_MoveStage', 'gesture'),
           setvar('%SIG3_Error', family + ' gesture did not complete'),
           setvar('%SIG3_Gesture', family + ' target=%sig3_target expected=%sig3_expected; DOWN-HOLD-MOVE-UP: same pointer; HOLD 200 ms; MOVE 300 ms; dispatchGesture + continueStroke; %sig3_x,%sig3_y -> %sig3_x,%sig3_end_y; UP only at end')]
    a = hold_drag()
    a.find("Str[@sr='arg0']").text = (ROOT / 'tools/sig3_target_drag.java').read_text()
    aa += [java_file('sig3_phone_check.java'), *g('%err', 12, '', family + ' audio preflight failed: %errmsg'), java_file('sig3_ui_check.java'), *g('%err', 12, '', family + ' control/program check failed: %errmsg'), a, *g('%err', 12, '', family + ' continuous gesture failed: %errmsg'), wait(500),
           setvar('%SIG3_MoveStage', 'readback'), call('SIG3_Internal' + family + 'Current', 'query_only'), setvar('%SIG3_Observed', level),
           *g(ok, 3, 1, family + ' post-gesture query failed: %SIG3_Error'),
           *g(level, 9, '%sig3_expected', family + ' unexpected readback=' + level + ' expected=%sig3_expected; stopped'),
           action(40), *family_fail(family, family + ' target not reached within bounded steps')]
    return aa


def target_wrapper(family, operation):
    lo, hi = (-8, 7) if family == 'Balance' else (0, 15)
    if operation in ('Max', 'Mute', 'Sharp', 'Soft'):
        value = hi if operation in ('Max', 'Sharp') else lo
        return [call('SIG3_Internal' + family + 'Set', str(value))]
    level = '%SIG3_Level' if family == 'Volume' else '%SIG3_' + family + 'Level'
    ok = '%SIG3_' + family + 'OK'
    boundary = hi if operation == 'Up' else lo
    return [call('SIG3_Internal' + family + 'Current'),
            *family_guard(family, ok, 3, 1, 'Current query failed: %SIG3_Error'),
            condition(level, 8, boundary), stop(), action(38),
            setvar('%sig3_requested', level + (' + 1' if operation == 'Up' else ' - 1'), True),
            call('SIG3_Internal' + family + 'Set', '%sig3_requested')]


def numeric_voice():
    aa = [setvar('%sig3_command', '%avcomm'),
          condition('%par1', 12), setvar('%sig3_command', '%par1'), action(38)]
    words = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen']
    for family in ('Volume', 'Balance', 'Tinnitus'):
        for value in range(-8 if family == 'Balance' else 0, 8 if family == 'Balance' else 16):
            word = (r'(?:minus|negative)\s+' if value < 0 else '') + words[abs(value)]
            pattern = r'(?i)^\s*(?:(?:set|change)\s+)?' + family.lower() + r'\s+(?:to\s+)?(?:' + str(value) + '|' + word + r')\s*$'
            aa += [condition('%sig3_command', 4, pattern), request(family, 'Set', str(value)), stop(), action(38)]
    for family, operation, pattern in [('Volume', 'Max', r'(?i)^\s*(?:maximum volume|volume max|volume maximum)\s*$'), ('Volume', 'Mute', r'(?i)^\s*(?:mute|volume mute|mute volume)\s*$'), ('Balance', 'Sharp', r'(?i)^\s*(?:balance sharp|sharp balance)\s*$'), ('Balance', 'Soft', r'(?i)^\s*(?:balance soft|soft balance)\s*$'), ('Tinnitus', 'Max', r'(?i)^\s*(?:maximum tinnitus|tinnitus max)\s*$'), ('Tinnitus', 'Mute', r'(?i)^\s*(?:tinnitus mute|mute tinnitus)\s*$')]:
        aa += [condition('%sig3_command', 4, pattern), request(family, operation), stop(), action(38)]
    for slot in range(1, 7):
        word = words[slot]
        pattern = r'(?i)^\s*(?:(?:set|change)\s+)?(?:program|mode)\s+(?:to\s+)?(?:' + str(slot) + '|' + word + r'|\Q%SIG3_ProgramName' + str(slot) + r'\E)\s*$'
        aa += [condition('%sig3_command', 4, pattern), request('Program', 'Switch', str(slot)), stop(), action(38)]
    for family, operation, target, pattern in [
            ('Battery','Check','open',r'(?i)^\s*(?:battery|battery check|check battery)\s*$'),
            ('Battery','Check','listen',r'(?i)^\s*(?:battery listen|listen to battery)\s*$'),
            ('Noise','Sample','',r'(?i)^\s*(?:noise sample|check noise)\s*$'),
            ('Setup','Override','1',r'(?i)^\s*(?:override on|manual mode)\s*$'),
            ('Setup','Override','0',r'(?i)^\s*(?:override off|automatic mode)\s*$')]:
        aa += [condition('%sig3_command', 4, pattern), request(family, operation, target), stop(), action(38)]
    return aa + [java_code('tasker.showToast("Use volume 0–15, balance minus 8–7, tinnitus 0–15, program 1–6, or battery check"); return "unrecognized";')]


def java_code(code):
    a = action(474); E.SubElement(a, 'se').text = 'true'
    string(a, 0, code); string(a, 1); integer(a, 2, 1)
    return a


def java_file(name):
    return java_code((ROOT / 'tools' / name).read_text())


def request(family, operation, target=''):
    return call('SIG3_Worker', family + ',' + operation + ',' + target)


def defaults():
    aa = []
    # Static APK IDs, adjustable; do not pretend these are phone-confirmed.
    for name, value in [('ProgramId', 'com.signia.rta:id/TA-ProgramName'),
                        ('VolumeControlId', 'com.signia.rta:id/VolumeSlider'),
                        ('BalanceControlId', 'com.signia.rta:id/TA-SoundBalanceSlider'),
                        ('TinnitusControlId', 'com.signia.rta:id/TA-TinnitusSlider'),
                        ('ProgramOpenId', 'com.signia.rta:id/TA_HomePage_ProgramSwitch_Icon'),
                        ('BatteryOpenId', 'com.signia.rta:id/TA-BatteryIcon'),
                        ('BatteryPageId', 'com.signia.rta:id/TA-BluetoothAndBatteryPageCloseIcon')]:
        aa += [condition('%SIG3_' + name, 13), setvar('%SIG3_' + name, value), action(38)]
    return aa


def protect_internal(aa):
    # TRUN is Tasker's live running-task list; it is not a sticky lock variable.
    return [condition('%TRUN', 5, r'(^|,)SIG3_Worker(,|$)'), stop(), action(38), *aa]


def worker():
    aa = [setvar('%SIG3_CommandOK', 0), setvar('%SIG3_Error', ''),
          setvar('%SIG3_Result', 'pending: operation did not finish'),
          setvar('%SIG3_MoveStage', 'start'), setvar('%SIG3_TouchStage', 'not run'), setvar('%SIG3_Gesture', ''), setvar('%SIG3_QueryData', ''), setvar('%SIG3_Program', ''),
          setvar('%SIG3_Previous', ''), setvar('%SIG3_Expected', ''), setvar('%SIG3_Observed', ''),
          setvar('%SIG3_AudioDiagnostics', ''), setvar('%SIG3_Target', ''),
          setvar('%SIG3_OperationId', '%TIMEMS'), setvar('%sig3_request', '%par1')]
    a = split('%sig3_request'); a.find("Str[@sr='arg1']").text = ','
    aa += [a, setvar('%SIG3_Family', '%sig3_request1'), setvar('%SIG3_Target', '%sig3_request3'), setvar('%SIG3_Error', 'Operation incomplete or unsupported request'), *defaults()]
    for family in ('Volume', 'Balance', 'Tinnitus'):
        aa += [condition('%sig3_request1', 2, family), setvar('%SIG3_' + family + 'OK', 0)]
        for op in ('Current','Set','Up','Down','Max','Mute','Sharp','Soft','Calibrate'):
            if (family == 'Balance' and op in ('Max','Mute')) or (family != 'Balance' and op in ('Sharp','Soft')): continue
            aa += [condition('%sig3_request2', 2, op), call('SIG3_Internal' + family + op, '%sig3_request3', '%sig3_request4'),
                   condition('%err', 12), setvar('%SIG3_Error', 'Internal task failed: %errmsg'), setvar('%SIG3_' + family + 'OK', 0), action(38),
                   setvar('%SIG3_CommandOK', '%SIG3_' + family + 'OK'), action(38)]
        aa += [action(38)]
    for family, operations in [('Program', ('Switch',)), ('Battery', ('Check',)), ('Noise', ('Sample','Process')), ('Sleep', ('Set',)), ('Setup', ('Init','Override'))]:
        aa += [condition('%sig3_request1', 2, family), setvar('%SIG3_' + family + 'OK', 0)]
        for operation in operations:
            aa += [condition('%sig3_request2', 2, operation), call('SIG3_Internal' + family + operation, '%sig3_request3'),
                   condition('%err', 12), setvar('%SIG3_Error', 'Internal task failed: %errmsg'), setvar('%SIG3_' + family + 'OK', 0), action(38),
                   setvar('%SIG3_CommandOK', '%SIG3_' + family + 'OK'), action(38)]
        aa += [action(38)]
    aa += [condition('%SIG3_CommandOK', 8, 1), setvar('%SIG3_MoveStage', 'complete'), setvar('%SIG3_Error', ''),
           setvar('%SIG3_Result', '%SIG3_Family: %SIG3_Observed; program=%SIG3_Program; target=%SIG3_Target (app state; aid receipt unverified)'),
           action(43), setvar('%SIG3_Result', 'Failed: %SIG3_Error; family=%SIG3_Family target=%SIG3_Target previous=%SIG3_Previous expected=%SIG3_Expected observed=%SIG3_Observed; program=%SIG3_Program; stage=%SIG3_MoveStage'), action(38),
           java_code('tasker.log(tasker.getVariable("SIG3_Result") + "; " + tasker.getVariable("SIG3_AudioDiagnostics")); tasker.showToast(tasker.getVariable("SIG3_Result")); return "reported";')]
    return aa


def extra_tasks():
    tasks = []
    def add(name, number, aa, internal=False):
        tasks.append(task(name, number, protect_internal(aa) if internal else aa))
    def g(family, lhs, op, rhs, message):
        return family_guard(family, lhs, op, rhs, message)
    def init_defaults():
        aa = defaults()
        for key, value in [('NoiseEnabled','0'),('SleepEnabled','0'),('ManualOverride','0'),
                           ('NoiseInvert','0'),('NoiseScaleConfirmed','0'),('NoiseStrikeLimit','3'),
                           ('NoiseStrikes','0'),('SleepActive','0')]:
            aa += [condition('%SIG3_' + key, 13), setvar('%SIG3_' + key, value), action(38)]
        return aa + [setvar('%SIG3_Observed','Defaults initialized; existing configuration preserved; automatic features default off'),setvar('%SIG3_SetupOK',1)]
    add('SIG3_InternalSetupInit',470,init_defaults(),True)
    add('SIG3_Init',360,[request('Setup','Init')])
    add('SIG3_InternalSetupOverride',471,[*g('Setup','%par1',5,r'^[01]$','Override must be 0 or 1'),setvar('%SIG3_ManualOverride','%par1'),setvar('%SIG3_NoiseStrikes',0),setvar('%SIG3_NoiseCandidate',''),setvar('%SIG3_Observed','Manual override=%par1'),setvar('%SIG3_SetupOK',1)],True)
    add('SIG3_Override',361,[request('Setup','Override','%par1')])
    program = [setvar('%SIG3_ProgramOK',0),call('SIG3_InternalAppLaunch'),*g('Program','%SIG3_AppOK',3,1,'Program launch failed: %SIG3_Error'),
               java_file('sig3_phone_check.java'),*g('Program','%err',12,'','Program audio preflight failed: %errmsg'),
               java_file('sig3_program.java'),*g('Program','%err',12,'','Program switch failed: %errmsg'),setvar('%SIG3_ProgramOK',1)]
    add('SIG3_InternalProgramSwitch',472,program,True)
    add('SIG3_ProgramSwitch',362,[request('Program','Switch','%par1')])
    battery = [setvar('%SIG3_BatteryOK',0),setvar('%SIG3_BatteryText',''),call('SIG3_InternalAppLaunch'),*g('Battery','%SIG3_AppOK',3,1,'Battery launch failed: %SIG3_Error'),
               condition('%par1',2,'listen'),java_file('sig3_phone_check.java'),*g('Battery','%err',12,'','Battery audio preflight failed: %errmsg'),action(38),
               java_file('sig3_battery.java'),*g('Battery','%err',12,'','Battery check failed: %errmsg'),setvar('%SIG3_BatteryOK',1)]
    add('SIG3_InternalBatteryCheck',473,battery,True)
    add('SIG3_BatteryCheck',363,[condition('%par1',13),setvar('%sig3_mode','open'),action(43),setvar('%sig3_mode','%par1'),action(38),request('Battery','Check','%sig3_mode')])
    # Reuse the exported AutoVoice capture envelope; no invented microphone implementation.
    noise_reference = E.parse(ROOT / 'tasks/SIG_Current_dB.tsk.xml').getroot()
    sample_action = deepcopy(next(a for a in noise_reference.findall('.//Action') if a.findtext('code') == '1218739680'))
    e = sample_action.find('se')
    if e is not None: sample_action.remove(e)
    e = E.Element('se'); e.text = 'true'; sample_action.insert(1,e)
    noise_process = [setvar('%SIG3_NoiseOK',0),setvar('%sig3_noise_raw','%par1'),java_file('sig3_noise.java'),*g('Noise','%err',12,'','Noise processing failed: %errmsg'),
                     condition('%SIG3_AutoProgramSlot',12),call('SIG3_InternalProgramSwitch','%SIG3_AutoProgramSlot'),*g('Noise','%SIG3_ProgramOK',3,1,'Automatic program switch failed: %SIG3_Error'),action(38),setvar('%SIG3_NoiseOK',1)]
    add('SIG3_InternalNoiseProcess',474,noise_process,True)
    noise_sample = [setvar('%SIG3_NoiseOK',0),sample_action,*g('Noise','%err',12,'','Noise plugin failed: %errmsg'),call('SIG3_InternalNoiseProcess','%avnoiselevel')]
    add('SIG3_InternalNoiseSample',475,noise_sample,True)
    add('SIG3_CurrentNoise',364,[request('Noise','Sample')])
    add('SIG3_NoiseMonitor',365,[request('Noise','Process','%par1')])
    sleep = [setvar('%SIG3_SleepOK',0),*g('Sleep','%SIG3_SleepEnabled',3,1,'Sleep automation is disabled'),
             *g('Sleep','%SIG3_ManualOverride',8,1,'Manual override blocks sleep automation'),
             *g('Sleep','%par1',5,r'^(?:asleep|awake)$','Sleep input must be asleep or awake'),
             condition('%par1',2,'asleep'),setvar('%sig3_sleep_slot','%SIG3_SleepProgram'),action(43),setvar('%sig3_sleep_slot','%SIG3_WakeProgram'),action(38),
             call('SIG3_InternalProgramSwitch','%sig3_sleep_slot'),*g('Sleep','%SIG3_ProgramOK',3,1,'Sleep program switch failed: %SIG3_Error'),
             condition('%par1',2,'asleep'),setvar('%SIG3_SleepActive',1),action(43),setvar('%SIG3_SleepActive',0),action(38),setvar('%SIG3_SleepOK',1)]
    add('SIG3_InternalSleepSet',476,sleep,True)
    add('SIG3_SleepState',366,[request('Sleep','Set','%par1')])
    # Capture event-local input explicitly. All control execution still goes through the worker.
    for name, number, preferred, fallback in [('SIG3_AutoVoiceCommand',367,'%avcommnofilter','%avcomm'),('SIG3_WatchCommand',368,'%awcomm','%awmessage')]:
        aa = [setvar('%sig3_input',preferred),condition(preferred,13),setvar('%sig3_input',fallback),action(38),
              condition('%par1',12),setvar('%sig3_input','%par1'),action(38),
              java_code('input = tasker.getVariable("sig3_input"); if (input == null) throw new com.joaomgcd.taskerm.action.java.JavaCodeException("No command text supplied by event"); input = input.trim().replaceAll("(?i)^sig3\\\\s+", ""); tasker.setVariable("sig3_input", input); return "normalized";'),
              condition('%err',13),call('SIG3_VoiceRouter','%sig3_input'),action(38)]
        add(name,number,aa)
    return tasks

def write(path, root):
    E.indent(root, space='\t')
    path.write_text(E.tostring(root, encoding='unicode') + '\n')


def build():
    specs = [('SIG3_AppLaunch', 301, launch), ('SIG3_VolumeCurrent', 302, current)]
    specs += [('SIG3_VolumeUp', 303, target_wrapper('Volume', 'Up')), ('SIG3_VolumeDown', 304, target_wrapper('Volume', 'Down'))]
    number = 305
    for family in ('Volume', 'Balance', 'Tinnitus'):
        if family != 'Volume':
            specs.append(('SIG3_' + family + 'Current', number, family_current(family))); number += 1
        specs.append(('SIG3_' + family + 'Set', number, target_set(family))); number += 1
        for operation in (('Max', 'Mute') if family == 'Volume' else ('Up', 'Down', 'Sharp', 'Soft') if family == 'Balance' else ('Up', 'Down', 'Max', 'Mute')):
            specs.append(('SIG3_' + family + operation, number, target_wrapper(family, operation))); number += 1
    specs.append(('SIG3_VoiceRouter', number, numeric_voice()))
    tasks = []
    for name, number, aa in specs:
        if name == 'SIG3_VoiceRouter':
            tasks.append(task(name, number, aa)); continue
        internal = name.replace('SIG3_', 'SIG3_Internal', 1)
        if name.endswith('Current'):
            family = name[len('SIG3_'):-len('Current')]
            # Fail closed if the common control or program cannot be confirmed.
            ok = '%SIG3_' + family + 'OK'
            level = '%SIG3_Level' if family == 'Volume' else '%SIG3_' + family + 'Level'
            aa = aa[:-1] + [java_file('sig3_ui_check.java'),
                            *family_guard(family, '%err', 12, '', family + ' UI guard failed: %errmsg'),
                            setvar('%SIG3_Observed', level), setvar(ok, 1)]
        if name == 'SIG3_AppLaunch':
            aa = [java_code('pm = context.getSystemService("power"); km = context.getSystemService("keyguard"); if (!pm.isInteractive() || km.isKeyguardLocked()) throw new com.joaomgcd.taskerm.action.java.JavaCodeException("Turn on and unlock the phone"); return "screen-ready";'), *guard('%err', 12, '', 'Screen prerequisite failed: %errmsg'), *aa]
        tasks.append(task(internal, number + 100, protect_internal(aa)))
        if name == 'SIG3_AppLaunch':
            # App launch is internal only; all public reads/writes go through worker.
            tasks.append(task(name, number, [request('Volume', 'Current')]))
            continue
        family = next(f for f in ('Volume','Balance','Tinnitus') if name.startswith('SIG3_' + f))
        operation = name[len('SIG3_' + family):]
        tasks.append(task(name, number, [request(family, operation, '%par1'), condition('%err', 12), java_code('tasker.showToast("Signia command was not accepted: busy or unavailable. Try again after completion."); return "rejected";'), action(38)]))
    for index, family in enumerate(('Volume', 'Balance', 'Tinnitus')):
        step = '%SIG3_' + family + 'StepPx'
        aa = [*family_guard(family, '%par1', 5, r'^[0-9]+$', 'Calibration requires measured pixel spacing'),
              *family_guard(family, '%par1', 6, 1, 'Step must be 1–200 pixels'),
              *family_guard(family, '%par1', 7, 200, 'Step must be 1–200 pixels'),
              call('SIG3_Internal' + family + 'Current'),
              *family_guard(family, '%SIG3_' + family + 'OK', 3, 1, 'Calibration query failed: %SIG3_Error'),
              *family_guard(family, '%par2', 5, r'^(?:1|-1)$', 'Calibration direction must be 1 or -1'), setvar(step, '%par1'), setvar('%SIG3_' + family + 'Direction', '%par2')]
        tasks.append(task('SIG3_Internal' + family + 'Calibrate', 460 + index, protect_internal(aa)))
    tasks.append(task('SIG3_Calibrate', 351, [call('SIG3_Worker', '%par1,Calibrate,%par2')]))
    tasks.extend(extra_tasks())
    tasks.append(task('SIG3_Worker', 350, worker()))
    for t in tasks:
        r = E.Element('TaskerData', sr='', dvi='1', tv='6.6.20'); r.append(deepcopy(t))
        write(ROOT / 'tasks' / (t.findtext('nme') + '.tsk.xml'), r)
    r = E.Element('TaskerData', sr='', dvi='1', tv='6.6.20')
    p = E.SubElement(r, 'Project', sr='proj0', ve='2')
    for tag, value in [('cdate', STAMP), ('name', 'HeySig3'), ('tids', ','.join(t.findtext('id') for t in tasks))]: E.SubElement(p, tag).text = value
    r.extend(tasks); write(ROOT / 'projects/HeySig3.prj.xml', r)


if __name__ == '__main__': build()
