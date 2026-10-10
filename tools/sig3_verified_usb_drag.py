#!/usr/bin/env python3
"""Replay the three Signia volume drags verified on the Pixel 9a, 2026-10-10."""
import argparse
import re
import subprocess
import xml.etree.ElementTree as ET

# from_level, to_level: start_x, start_y, end_x, end_y, duration_ms
VERIFIED_DRAGS = {
    (7, 8): (540, 1393, 540, 1306, 650),
    (8, 9): (540, 1306, 540, 1219, 650),
    (9, 0): (540, 1219, 540, 2000, 1000),
}
PACKAGE = 'com.signia.rta'
VALUE_ID = PACKAGE + ':id/TA-SliderValue'
SLIDER_ID = PACKAGE + ':id/VolumeSlider'


def read_volume(adb):
    subprocess.run(adb + ['shell', 'uiautomator', 'dump', '/sdcard/heysig-window.xml'],
                   check=True, capture_output=True, timeout=30)
    xml = subprocess.check_output(adb + ['shell', 'cat', '/sdcard/heysig-window.xml'], timeout=15)
    root = ET.fromstring(xml)
    if root.get('rotation') != '0':
        raise RuntimeError('Expected the verified portrait orientation')
    nodes = list(root.iter('node'))
    labels = [n for n in nodes if n.get('resource-id') == VALUE_ID]
    sliders = [n for n in nodes if n.get('resource-id') == SLIDER_ID]
    if len(labels) != 1 or len(sliders) != 1:
        raise RuntimeError('Open the Signia Volume tab; expected one slider and one value label')
    slider = sliders[0]
    if slider.get('bounds') != '[501,652][580,2047]':
        raise RuntimeError('Slider layout differs from the verified layout; no gesture sent')
    if slider.get('enabled') != 'true':
        raise RuntimeError('Slider is disabled')
    size = subprocess.check_output(adb + ['shell', 'wm', 'size'], text=True, timeout=15)
    sizes = re.findall(r'(?:Physical|Override) size: (\d+x\d+)', size)
    if not sizes or sizes[-1] != '1080x2424':
        raise RuntimeError('Expected the verified 1080x2424 screen size')
    return int(labels[0].get('text'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True, help='Authorized ADB device serial')
    parser.add_argument('previous', type=int, help='Expected displayed starting level')
    parser.add_argument('target', type=int, help='Requested displayed level')
    args = parser.parse_args()
    drag = VERIFIED_DRAGS.get((args.previous, args.target))
    if drag is None:
        parser.error('Only verified transitions 7->8, 8->9 and 9->0 are available')
    adb = ['adb', '-s', args.serial]
    previous = read_volume(adb)
    print(f'Before: {previous}', flush=True)
    if previous != args.previous:
        raise RuntimeError(f'Expected {args.previous}; no gesture sent')
    # Exactly one ordinary pointer drag. No retry or fallback on mismatched readback.
    subprocess.run(adb + ['shell', 'input', 'swipe', *map(str, drag)], check=True, timeout=15)
    observed = read_volume(adb)
    print(f'After: {observed}', flush=True)
    if observed != args.target:
        raise RuntimeError(f'Expected {args.target}, observed {observed}; no retry sent')


if __name__ == '__main__':
    main()
