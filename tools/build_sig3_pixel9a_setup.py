"""Build explicit Pixel 9a gesture calibration for Balance and Tinnitus only."""
import xml.etree.ElementTree as E
import build_heysig3 as b


def build():
    settings = []
    for family in ('Balance', 'Tinnitus'):
        settings.extend([(f'SIG3_{family}Backend', 'legacy-gesture'),
                         (f'SIG3_{family}KnobId', 'com.signia.rta:id/TA-SliderValue'),
                         (f'SIG3_{family}StepPx', '87'),
                         (f'SIG3_{family}Direction', '1'),
                         (f'SIG3_{family}TrackTopY', '695'),
                         (f'SIG3_{family}TrackBottomY', '2000'),
                         (f'SIG3_{family}TrackBounds', '501,652,580,2047')])
    root = E.Element('TaskerData', sr='', dvi='1', tv='6.6.20')
    root.append(b.task('SIG3_Pixel9aGestureSetup', 990,
                      [b.condition('%SIG3_AudioStream', 13), b.setvar('%SIG3_AudioStream', 'media'), b.action(38)] +
                      [b.setvar('%' + name, value) for name, value in settings]))
    b.write(b.ROOT / 'tasks/SIG3_Pixel9aGestureSetup.tsk.xml', root)


if __name__ == '__main__':
    build()
