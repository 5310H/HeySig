"""Execute actual Phase 1 action lists with aligned mock accessibility arrays."""
import json
from copy import deepcopy
from itertools import permutations
import xml.etree.ElementTree as E
from heysig3_runtime import Phone, ROOT, TASKS


def phone(level, mode='region', **kwargs):
    p = Phone(level, **kwargs)
    if mode == 'id': p.globals['SIG3_KnobId'] = 'volume-knob'
    else:
        p.globals.update(SIG3_KnobXMin='450', SIG3_KnobXMax='550',
                         SIG3_KnobYMin='350', SIG3_KnobYMax='1050')
    return p


# Real-device 7 capture plus synthetic endpoint values using its verified ID.
CAPTURE_ID = 'com.signia.rta:id/TA-SliderValue'

def capture(level=7, order=(0, 1, 2), knob_id=CAPTURE_ID):
    rows = [('15', 'com.signia.rta:id/maximum', '700,1000'),
            (str(level), knob_id, '541,1701'),
            ('0', 'com.signia.rta:id/minimum', '700,2000')]
    rows = [rows[i] for i in order]
    p = Phone(level, texts=','.join(r[0] for r in rows),
              ids=[r[1] for r in rows], coordinates=[r[2] for r in rows])
    p.globals['SIG3_KnobId'] = CAPTURE_ID
    return p

# Regression: the original simple Matches operator interprets '/' as OR.
original = TASKS['SIG3_InternalVolumeCurrent']
broken = deepcopy(original)
id_condition = next(c for c in broken.findall('.//Condition')
                    if c.findtext('lhs') == '%aiid(%sig3_i)')
id_condition.find('op').text = '2'
id_condition.find('rhs').text = '%SIG3_KnobId'
try:
    TASKS['SIG3_InternalVolumeCurrent'] = broken
    p = capture(); p.run('SIG3_VolumeCurrent')
    assert p.globals['SIG3_Level'] == '-1' and p.globals['SIG3_VolumeOK'] == '0'
    assert 'Knob selector matched' in p.globals['SIG3_Error']
finally:
    TASKS['SIG3_InternalVolumeCurrent'] = original

for level in range(16):
    for order in permutations(range(3)):
        p = capture(level, order); p.run('SIG3_VolumeCurrent')
        assert (p.globals['SIG3_Level'], p.globals['SIG3_VolumeX'],
                p.globals['SIG3_VolumeY'], p.globals['SIG3_VolumeOK']) == (str(level), '541', '1701', '1'), p.globals

# Regex metacharacters in a resource ID are literal, and partial IDs fail.
for bad_id in ('comXsigniaXrta:id/TA-SliderValue', 'TA-SliderValue',
               'com.signia.rta:id', CAPTURE_ID + '-other'):
    p = capture(knob_id=bad_id); p.run('SIG3_VolumeCurrent')
    assert p.globals['SIG3_VolumeOK'] == '0'

# Numeric Set supersedes the former escalating swipe movement checks.
import check_sig3_numeric
print('HeySig3 selector regressions and numeric target checks passed')
