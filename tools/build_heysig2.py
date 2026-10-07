"""Build the isolated Phase 1 project using native Tasker control flow.

Only low-level App/plugin argument envelopes are reused from reference exports;
all task control flow is new. Run from any directory with python3.
"""
from pathlib import Path
from copy import deepcopy
import json
import uuid
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
reference = E.parse(ROOT / 'tasks/SIG_VolumeUp.tsk.xml').getroot()
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


def call(name, param=''):
    a = action(130)
    string(a, 0, name)
    E.SubElement(E.SubElement(a, 'Int', sr='arg1'), 'var').text = '%priority'
    integer(a, 10, 1)
    for i in (2, 3, 4): string(a, i, param if i == 2 else '')
    for i in (5, 6): integer(a, i)
    string(a, 7)
    for i in (8, 9): integer(a, i)
    return a


def stop():
    a = action(137); integer(a, 0); string(a, 1); return a


def fail(message):
    return [setvar('%SIG2_VolumeOK', 0), setvar('%SIG2_Error', message), stop()]


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
        vals.find('plugininstanceid').text = str(uuid.uuid5(uuid.NAMESPACE_URL, 'HeySig2:' + str(code) + ':' + str(command)))
        if command is not None:
            params = json.loads(vals.findtext('parameters'))
            if str(code) == '107361459':
                params['_action'] = command
                vals.find('com.twofortyfouram.locale.intent.extra.BLURB').text = 'Actions To Perform: ' + command
            else:
                params.update(initialPoint='Start X: %sig2_x\nStart Y: %sig2_y',
                              endPoint='End X: %sig2_x\nEnd Y: %sig2_end_y', duration='300')
                if command == 'swipe_up':
                    # Installed AutoInput Point(String) splits two numbers on ','.
                    params.update(initialPoint='%sig2_x,%sig2_y', endPoint='%sig2_x,%sig2_end_y')
                vals.find('com.twofortyfouram.locale.intent.extra.BLURB').text = 'Swipe from %sig2_x,%sig2_y to %sig2_x,%sig2_end_y (300 ms)'
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


launch = [setvar('%SIG2_AppOK', 0), setvar('%SIG2_Error', ''), plugin(20),
          condition('%err', 12), setvar('%SIG2_Error', 'Signia launch failed: %errmsg'), stop(), action(38),
          wait(1000), *checked_plugin(15355),
          condition('%aipackage', 3, 'com.signia.rta'), setvar('%SIG2_Error', 'Signia is not foreground'), stop(), action(38),
          setvar('%SIG2_AppOK', 1)]

current = [setvar('%SIG2_VolumeOK', 0), setvar('%SIG2_Level', -1),
           setvar('%SIG2_VolumeX', -1), setvar('%SIG2_VolumeY', -1),
           condition('%par1', 3, 'query_only'), setvar('%SIG2_Error', ''), action(38),
           condition('%par1', 3, 'query_only'), call('SIG2_AppLaunch'),
           *guard('%SIG2_AppOK', 3, 1, 'Signia launch did not complete'),
           *checked_plugin(107361459, 'click(text,Volume Tab)'), wait(), action(38),
           *checked_plugin(15355), *guard('%aipackage', 3, 'com.signia.rta', 'Signia is not foreground'),
           *guard('%aitext(#)', 6, 1, 'Empty UI Query text array'),
           setvar('%SIG2_QueryData', ''), loop('%sig2_dump_i', '1:%aitext(#)'),
           setvar('%SIG2_QueryData', '%SIG2_QueryData%sig2_dump_i | %aitext(%sig2_dump_i) | %aiid(%sig2_dump_i) | %aicoordinates(%sig2_dump_i)\n'),
           action(40),
           # Stable knob resource ID wins. Otherwise require a calibrated region.
           setvar('%sig2_mode', 'id'), condition('%SIG2_KnobId', 13), setvar('%sig2_mode', 'region')]
for name in ('XMin', 'XMax', 'YMin', 'YMax'):
    current += guard('%SIG2_Knob' + name, 5, r'^[0-9]+$', 'Configure SIG2_KnobId or all four knob region bounds first')
current += guard('%SIG2_KnobXMin', 7, '%SIG2_KnobXMax', 'Invalid knob X region')
current += guard('%SIG2_KnobYMin', 7, '%SIG2_KnobYMax', 'Invalid knob Y region')
current += [action(38), setvar('%sig2_count', 0),
            *guard('%aitext(#)', 6, 1, 'Empty UI Query text array'),
            *guard('%aitext(#)', 9, '%aicoordinates(#)', 'UI Query text/coordinate arrays are not aligned'),
            condition('%sig2_mode', 2, 'id'),
            *guard('%aitext(#)', 9, '%aiid(#)', 'UI Query text/id arrays are not aligned'), action(38),
            loop('%sig2_i', '1:%aitext(#)'), setvar('%sig2_text', '%aitext(%sig2_i)'),
            condition('%sig2_text', 4, r'^(?:[0-9]|1[0-5])$'),
            setvar('%sig2_point', '%aicoordinates(%sig2_i)'),
            condition('%sig2_point', 4, r'^[0-9]+,[0-9]+$'), split('%sig2_point'),
            setvar('%sig2_selected', 0),
            condition('%sig2_mode', 2, 'id'), condition('%aiid(%sig2_i)', 4, r'^\Q%SIG2_KnobId\E$'),
            setvar('%sig2_selected', 1), action(38), action(43), setvar('%sig2_selected', 1)]
for lhs, op, rhs in [('%sig2_point1', 6, '%SIG2_KnobXMin'), ('%sig2_point1', 7, '%SIG2_KnobXMax'),
                     ('%sig2_point2', 6, '%SIG2_KnobYMin'), ('%sig2_point2', 7, '%SIG2_KnobYMax')]:
    current += [condition(lhs, op, rhs), setvar('%sig2_selected', 0), action(38)]
current += [action(38), condition('%sig2_selected', 8, 1),
            setvar('%sig2_count', '%sig2_count + 1', True), setvar('%sig2_level', '%sig2_text'),
            setvar('%sig2_x', '%sig2_point1'), setvar('%sig2_y', '%sig2_point2'),
            action(38), action(38), action(38), action(40),
            *guard('%sig2_count', 9, 1, 'Knob selector matched zero or multiple numeric elements; inspect aligned UI Query data'),
            setvar('%SIG2_Level', '%sig2_level'), setvar('%SIG2_VolumeX', '%sig2_x'),
            setvar('%SIG2_VolumeY', '%sig2_y'), setvar('%SIG2_Error', ''), setvar('%SIG2_VolumeOK', 1)]


def move_up():
    # One measured step: current 8 at y=1661 -> desired 9 near y=1621.
    # Keep a pending diagnostic before operations which can halt Tasker.
    def pending(stage, message):
        return [setvar('%SIG2_VolumeOK', 0), setvar('%SIG2_MoveStage', stage),
                setvar('%SIG2_Error', message)]
    aa = [setvar('%SIG2_TapErr', 'not run'), setvar('%SIG2_TapErrMsg', 'not run'),
          setvar('%SIG2_GestureErr', 'not run'), setvar('%SIG2_GestureErrMsg', 'not run'),
          call('SIG2_VolumeCurrent'),
          *guard('%SIG2_VolumeOK', 3, 1, 'VolumeUp initial readback failed: %SIG2_Error'),
          setvar('%sig2_start', '%SIG2_Level'),
          condition('%sig2_start', 8, 15), setvar('%SIG2_MoveStage', 'upper-boundary'), stop(), action(38),
          *pending('prepare', 'VolumeUp stopped while preparing the 40 px upward gesture'),
          setvar('%sig2_target', '%sig2_start + 1', True),
          setvar('%sig2_x', '%SIG2_VolumeX'), setvar('%sig2_y', '%SIG2_VolumeY'),
          setvar('%sig2_end_y', '%sig2_y - 40', True),
          setvar('%SIG2_Gesture', 'tap %sig2_x,%sig2_y; swipe %sig2_x,%sig2_y -> %sig2_x,%sig2_end_y; 40 px up; 300 ms'),
          *guard('%sig2_end_y', 6, 0, 'VolumeUp endpoint above screen: %SIG2_Gesture'),
          *pending('tap', 'VolumeUp AutoInput tap did not complete: %SIG2_Gesture'),
          setvar('%SIG2_TapErr', 'not returned (action halted)'), setvar('%SIG2_TapErrMsg', 'not returned (action halted)'),
          plugin(107361459, r'click(point,%SIG2_VolumeX\,%SIG2_VolumeY)'),
          setvar('%SIG2_TapErr', '%err'), setvar('%SIG2_TapErrMsg', '%errmsg'),
          *guard('%err', 12, '', 'VolumeUp AutoInput tap failed: code=%SIG2_TapErr message=%SIG2_TapErrMsg; %SIG2_Gesture'),
          wait(100),
          *pending('gesture', 'VolumeUp AutoInput gesture did not complete: %SIG2_Gesture'),
          setvar('%SIG2_GestureErr', 'not returned (action halted)'), setvar('%SIG2_GestureErrMsg', 'not returned (action halted)'),
          plugin(778682267, 'swipe_up'),
          setvar('%SIG2_GestureErr', '%err'), setvar('%SIG2_GestureErrMsg', '%errmsg'),
          *guard('%err', 12, '', 'VolumeUp AutoInput gesture failed: code=%SIG2_GestureErr message=%SIG2_GestureErrMsg; %SIG2_Gesture'),
          wait(),
          *pending('readback', 'VolumeUp post-gesture query did not complete: %SIG2_Gesture'),
          call('SIG2_VolumeCurrent', 'query_only'),
          *guard('%SIG2_VolumeOK', 3, 1, 'VolumeUp post-gesture readback failed: %SIG2_Error; %SIG2_Gesture'),
          *pending('verify', 'VolumeUp stopped while verifying readback: %SIG2_Gesture'),
          *guard('%SIG2_Level', 8, '%sig2_start', 'VolumeUp unchanged: level=%SIG2_Level expected=%sig2_target; %SIG2_Gesture'),
          *guard('%SIG2_Level', 9, '%sig2_target', 'VolumeUp unexpected level=%SIG2_Level expected=%sig2_target; %SIG2_Gesture'),
          setvar('%SIG2_MoveStage', 'complete'), setvar('%SIG2_Error', ''), setvar('%SIG2_VolumeOK', 1)]
    return aa


def move(delta):
    if delta == 1:
        return move_up()
    aa = [call('SIG2_VolumeCurrent'), *guard('%SIG2_VolumeOK', 3, 1, 'Current readback failed: %SIG2_Error'),
          setvar('%sig2_start', '%SIG2_Level'),
          condition('%sig2_start', 8, 15 if delta == 1 else 0), stop(), action(38),
          setvar('%sig2_target', f'%sig2_start + ({delta})', True), loop('%sig2_attempt', '1:20'),
          call('SIG2_VolumeCurrent', 'query_only'), *guard('%SIG2_VolumeOK', 3, 1, 'Current readback failed: %SIG2_Error'),
          *guard('%SIG2_Level', 9, '%sig2_start', 'Volume changed before gesture; stopped'),
          *checked_plugin(107361459, r'click(point,%SIG2_VolumeX\,%SIG2_VolumeY)'), wait(100),
          call('SIG2_VolumeCurrent', 'query_only'), *guard('%SIG2_VolumeOK', 3, 1, 'Current readback failed: %SIG2_Error'),
          *guard('%SIG2_Level', 9, '%sig2_start', 'Volume changed during knob tap; stopped'),
          setvar('%sig2_x', '%SIG2_VolumeX'), setvar('%sig2_y', '%SIG2_VolumeY'),
          setvar('%sig2_distance', '%sig2_attempt * 8', True),
          setvar('%sig2_end_y', f'%sig2_y - ({delta}) * %sig2_distance', True),
          *guard('%sig2_end_y', 6, 0, 'Gesture would leave screen'),
          setvar('%SIG2_VolumeOK', 0), *checked_plugin(778682267, 'swipe'), wait(),
          call('SIG2_VolumeCurrent', 'query_only'), *guard('%SIG2_VolumeOK', 3, 1, 'Post-gesture readback failed: %SIG2_Error'),
          condition('%SIG2_Level', 8, '%sig2_target'), stop(), action(38),
          *guard('%SIG2_Level', 9, '%sig2_start', 'Gesture skipped a level; stopped without retry'),
          action(40), *fail('Volume unchanged after 20 gestures')]
    return aa


def write(path, root):
    E.indent(root, space='\t')
    path.write_text(E.tostring(root, encoding='unicode') + '\n')


def build():
    tasks = [task(name, number, aa) for name, number, aa in [
        ('SIG2_AppLaunch', 201, launch), ('SIG2_VolumeCurrent', 202, current),
        ('SIG2_VolumeUp', 203, move(1)), ('SIG2_VolumeDown', 204, move(-1))]]
    for t in tasks:
        r = E.Element('TaskerData', sr='', dvi='1', tv='6.6.20'); r.append(deepcopy(t))
        write(ROOT / 'tasks' / (t.findtext('nme') + '.tsk.xml'), r)
    r = E.Element('TaskerData', sr='', dvi='1', tv='6.6.20')
    p = E.SubElement(r, 'Project', sr='proj0', ve='2')
    for tag, value in [('cdate', STAMP), ('name', 'HeySig2'), ('tids', '201,202,203,204')]: E.SubElement(p, tag).text = value
    r.extend(tasks); write(ROOT / 'projects/HeySig2.prj.xml', r)


if __name__ == '__main__': build()
