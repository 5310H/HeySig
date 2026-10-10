# HeySig3 completed work and test checklist

Updated October 10, 2026. Checked phone items below were actually observed on the Pixel 9a; repository checks are listed separately. Unchecked items remain to be tested. See the [user manual](HeySig3.md) and [recorded phone evidence](HeySig3-verified-usb-drags.md).

## Completed implementation

- [x] Repair slider inspection when direct ID lookup returns no nodes; traverse the actual accessibility tree using exact IDs.
- [x] Use the actual Balance and Tinnitus tab descriptions.
- [x] Locate calibrated gesture starts from native progress rather than the numeric label's oversized bounds.
- [x] Send one continuous 650 ms Tasker gesture and verify fresh displayed readback.
- [x] Select backends per family, preserving the Volume backend when configuring balance/tinnitus.
- [x] Avoid a second app launch when Up/Down has already read the current level.
- [x] Preserve Java errors and avoid self-referential `%SIG3_Error` failure messages.
- [x] Check for a visible enabled tinnitus tab before selecting it; stop cleanly if unavailable, including inspection and endpoint requests.
- [x] Read the active program header when a configured program label ID is absent; keep ambiguity and program-change guards.
- [x] Save the Pixel 9a setup task, generated exports, verified ADB volume replay code, and phone verification notes.
- [x] Publish the implementation to GitHub on `HeySid3` ([cc3fc3f](https://github.com/5310H/HeySig/commit/cc3fc3f)).

## Passed on the phone

- [x] VolumeInspect: success, empty Error, exact visible enabled VolumeSlider, native range and actions captured; no movement.
- [x] BalanceInspect: success and native center captured at displayed 0.
- [x] Balance bottom label: observed −8, then restored 0. Displayed range is −8–7; native step 8 is center 0.
- [x] ADB volume 7 → 8, 8 → 9, and 9 → 0; user confirmed these moves worked. These are separate from Tasker's Volume backend.
- [x] Tasker balance 0 → 1 → 0 in Universal, with expected app labels and successful result.
- [x] Tasker tinnitus 0 → 1 → 0 in Universal, with expected app labels and successful result.
- [x] Signia audio setting read as Media sound; Tasker configured to match, with an unmuted speaker stream.
- [x] TV inspected: Volume/Balance tabs present, tinnitus tab absent.
- [x] TinnitusUp in TV: `Tinnitus unavailable for this program`, empty gesture diagnostic, no slider gesture.
- [x] Updated TinnitusCurrent in Universal: displayed 0, program Universal, empty Error.
- [x] Updated BalanceCurrent in TV: displayed 0, program TV, empty Error despite the configured label ID being Universal.
- [x] Restore Universal after TV testing; balance and tinnitus finished at 0.

Successful app labels do not independently acknowledge acoustic receipt by the aids. The volume ADB moves have user confirmation; separate aid-response checks for balance/tinnitus remain below.

## Passed in repository checks

- [x] Static validation: 79 XML files, 4,921 task actions, zero failures.
- [x] Numeric simulation: 768 source/target transitions, invalid targets, repeated targets, endpoints and readback failures.
- [x] Backend simulation: native prerequisites, accepted-but-unchanged progress, and per-family backend isolation.
- [x] Missing tinnitus simulation: Current, Up, Down, Set, Max, Mute, Inspect, and voice request stop without movement.
- [x] Worker coordination, wrong control/program, calibration, generated-project parity, migration and restored workflows.

These checks do not execute Android/BeanShell or phone plugin events. Run the repository checks with:

```bash
python3 tests/check_sig3_numeric.py
python3 tests/check_sig3_progress.py
python3 tests/check_sig3_tinnitus_available.py
python3 tests/check_sig3_coordination.py
python3 tests/check_sig3_parity.py
python3 tests/check_sig3_migration.py
python3 tests/validate_heysig3_xml.py
```

## Next phone tests, in order

Use an unlocked phone on Signia Controls. Keep competing legacy profiles disabled. Record starting program/value and restore them after each test. Stop on an error or unexpected readback; do not resend blindly.

1. [ ] Run public BalanceSet with Parameter 1 `1`, then `0`; repeat `0` and confirm no additional gesture. The successful Up/Down wrappers exercised Set internally, but direct numbered entry and repeated-target behavior still need explicit phone checks.
2. [ ] Run public TinnitusSet with Parameter 1 `1`, then `0` in Universal; repeat `0` and confirm no additional gesture.
3. [ ] Test balance 0 → −1 → 0, followed by other small targets before endpoint/long-jump tests.
4. [ ] Confirm the expected audible aid response for balance and tinnitus separately from app readback.
5. [ ] In TV, test TinnitusCurrent, Set, Mute/Max and Inspect. Confirm the same unavailable message, no gesture/progress action, and no program switch. Up already passed; the other entry points have simulated coverage only.
6. [ ] Check availability/readback in the remaining actual programs: Off just Tinnitus, Noisy, Outdoor and Very Noisy. Do not assume which ones provide a tinnitus tab.
7. [ ] Test balance/tinnitus movement in another program where its control is present; only Universal movement has passed so far.
8. [ ] Test public numeric voice routing with explicit command text, then actual AutoVoice recognition. Confirm correct target, cancellation and no command on unrecognized speech.
9. [ ] Test the configured AutoWear command event and its actual input variable.
10. [ ] Test a second command while the worker runs, a manual Stop, and successful recovery afterward. Confirm no stale success or stuck lock.
11. [ ] Test locked screen, app left on settings, missing control/overlay, program change, muted selected stream and active call failures as appropriate. Opening Controls recovered the observed settings-page launch failure; automatic recovery is not implemented.

## Volume and native accessibility acceptance still pending

- [ ] Verify Tasker's Volume Set path separately. Existing ADB volume success does not establish it.
- [ ] Confirm native/display mapping at enough levels for each family before setting its RangeConfirmed flag.
- [ ] If intentionally testing native accessibility, verify touch exploration is enabled by the user. It was off in the captured inspection, and the code must stop before sending progress when off.
- [ ] Verify one native adjacent target, repeated target, reverse move and actual aid response. Do not infer acoustic commit from Android acceptance or a changed label.
- [ ] Test mute/max and full-range targets only after ordinary adjacent moves work for the chosen backend.

See the [acceptance guide](HeySig3-slider-acceptance.md); no automatic backend fallback is used.

## Other workflows: implemented, phone verification pending

- [ ] SIG3 ProgramCurrent and ProgramSwitch, exact configured program names/slots, repeated-current no-op and failure cases. Manual program selection and the slider guard's TV read do not certify these tasks.
- [ ] SIG3 battery listen sequence and prompted battery recognition. The original HeySig sequence was user-confirmed; the migrated SIG3 version remains unverified.
- [ ] Prompted mode recognition, aliases, empty/cancelled input and override toggle.
- [ ] Phone/watch noise capture, measured units/sign, thresholds, strike count and optional three-tier program selection.
- [ ] Sleep/wake events, foreground deferral, manual override, cancellation/resume and optional Home completion.
- [ ] Fresh project import and Pixel setup after export, plus configuration persistence after Tasker/phone restart.

Leave noise/sleep automation disabled until its configuration and event tests pass. See [event wiring](HeySig3-completion.md).
