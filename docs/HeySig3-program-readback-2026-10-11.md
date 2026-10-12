# Remaining-program readback acceptance — October 11, 2026

Checklist item 6 passed in a guarded 28-request phone run. Exact program names and switch slots came from configured mappings and were checked against the active app header. Each of the four remaining programs passed ProgramSwitch, repeated-current ProgramSwitch with no gesture, and fresh VolumeCurrent, BalanceCurrent and TinnitusCurrent readback.

| Program | Header icon | Volume | Balance | Tinnitus |
| --- | --- | ---: | ---: | ---: |
| Off just Tinnitus | U+E912 | 8 | 0 | 7 |
| Noisy | U+E912 | 8 | 0 | 7 |
| Outdoor | U+E912 | 8 | 0 | 7 |
| Very Noisy | U+E912 | 12 | 0 | 2 |

All four programs provide tinnitus on this phone. These observations do not form a program-name allowlist: production availability reads the live icon, with tab fallback only for unknown icons.

All 28 operation IDs were distinct. Every request returned CommandOK=1, empty Error and complete stage. Each numeric result matched the independently captured selected tab and displayed value. Repeated program selection left Gesture empty and TouchStage `not run`. No slider values were written. The final ProgramSwitch and three Current reads restored the captured starting Universal values: Volume 9, Balance 0 and Tinnitus 0.

Evidence: `/tmp/sig3-modes-final.json`, validated by `/tmp/sig3_validate_modes.py`. All six installed Current/Inspect helpers now use the live label target with selected-tab verification.
