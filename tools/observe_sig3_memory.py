"""Read-only, bounded ADB memory observations; does not start phone tasks."""
import argparse
import json
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--duration', type=int, default=1800, help='Seconds (1–28800)')
    parser.add_argument('--interval', type=int, default=60, help='Seconds (10–600)')
    args = parser.parse_args()
    if not 1 <= args.duration <= 28800 or not 10 <= args.interval <= 600:
        parser.error('Duration or interval outside bounds')
    adb = ['adb', '-s', args.serial]

    def read(command):
        try:
            result = subprocess.run(adb + ['shell', command], capture_output=True,
                                    text=True, timeout=20)
            return {'code': result.returncode, 'stdout': result.stdout,
                    'stderr': result.stderr}
        except subprocess.TimeoutExpired:
            return {'error': 'ADB read timed out'}

    start = time.monotonic()
    # Exclusive creation protects evidence from previous sessions.
    with args.output.open('x') as output:
        while True:
            row = {'hostTime': time.time(), 'elapsedSeconds': time.monotonic() - start}
            row['uptime'] = read('cat /proc/uptime')
            for package in ('net.dinglisch.android.taskerm', 'com.joaomgcd.autovoice'):
                row[package] = {
                    'pid': read('pidof ' + package),
                    'memory': read('dumpsys meminfo ' + package),
                }
            row['summary'] = read('cat /sdcard/Tasker/sig3-endurance-summary.json')
            output.write(json.dumps(row) + '\n')
            output.flush()
            remaining = args.duration - (time.monotonic() - start)
            if remaining <= 0:
                break
            time.sleep(min(args.interval, remaining))


if __name__ == '__main__':
    main()
