# HeySig3 remaining work

Updated October 10, 2026. This is the prioritized completion list, based on the [current test checklist](HeySig3-test-checklist.md), [phone evidence](HeySig3-verified-usb-drags.md), and [event wiring](HeySig3-completion.md). Unchecked items are pending, not necessarily missing implementations. Historical gaps in the main-parity review may already be implemented.

Program names must come from actual Signia readback or configured slots, never hardcoded into controls or test guards. Named programs in historical evidence describe what was tested. New tests should capture their starting program and verify that it remains unchanged.

## 1. Finish core slider acceptance

- [ ] Establish a working **Tasker VolumeSet** backend on the phone. Record its configuration, test an adjacent move and reverse, repeat the target to prove no additional movement, and confirm the audible aid response. Successful ADB volume drags do not complete this item.
- [x] Run **BalanceSet** directly with Parameter 1: 1 → 0, then repeat 0 and verify no gesture (app readback only).
- [ ] Test balance 0 → −1 → 0 and confirm hearing-aid receipt.
- [ ] Run **TinnitusSet** directly in Universal: 1 → 0, then repeat 0 and verify no gesture.
- [ ] Confirm audible aid response for balance and tinnitus independently of the app labels.
- [ ] After small moves pass, test other numbered targets, long jumps and endpoints: volume/tinnitus 0–15, balance −8–7. Restore starting values after testing.
- [ ] Verify availability and current readback in Off just Tinnitus, Noisy, Outdoor and Very Noisy; record actual tab availability rather than infer it from program names.
- [ ] Verify balance/tinnitus movement in another program where each control exists.
- [ ] In TV, run TinnitusCurrent, Set, Mute, Max and Inspect; verify the unavailable error, no movement and no program switch. TinnitusUp already passed.
- [x] Run TinnitusInspect in a program with tinnitus available; record its diagnostics. Passed in Universal during the [verification run](HeySig3-verification-2026-10-10.md).

Completion evidence: chosen per-family backend, starting/target/observed values, command result/error, repeated-target behavior, and user-confirmed aid response. Use the [slider acceptance guide](HeySig3-slider-acceptance.md).

## 2. Verify program, battery and prompted commands

- [x] Read six exact program names from the live picker and fill unset slots; confirm the program opener and battery page selectors on the phone.
- [ ] Configure desired Conversation/Noisy/VeryNoisy aliases when selected.
- [ ] Test SIG3_ProgramCurrent and ProgramSwitch across actual programs, including repeated-current no-op, missing/ambiguous names and failed selection. The slider guard's program read does not certify these separate tasks.
- [x] Investigate and correct the live ProgramCurrent failure, compare active imported tasks with repository exports, and retest in Universal. The repaired read path passed; see the [verification run](HeySig3-verification-2026-10-10.md).
- [x] Investigate the live VolumeCurrent failure and restore a fresh successful read. Importing the repaired tree guard passed in Universal with value 0.
- [ ] Clean up unresolved optional fields in result messages and verify concrete reporting for failed requests.
- [x] Import/run SIG3_BatteryCheck listen: repaired current top-right opener, left request, acknowledge, right request, acknowledge, close; app screen and Tasker result passed, user confirmed.
- [ ] Confirm audible battery indications when the aids are worn.
- [ ] Test prompted mode and battery recognition, configured aliases, empty/cancelled input and override toggle.

## 3. Connect and verify actual phone events

The project supplies tasks but imports **no event profiles**.

- [ ] Connect AutoVoice Recognized to SIG3_AutoVoiceCommand using the actual recognition text. First test explicit text through VoiceRouter, then live recognition for volume, balance, tinnitus, program and battery requests.
- [ ] Connect the actual AutoWear command event to SIG3_WatchCommand and verify its input variable and target routing.
- [ ] Confirm unrecognized speech and cancelled recognition send no command.
- [ ] Audit phone shortcuts, profiles, intermediate tasks and variable readers. Replace old SIG_ calls/readers with public SIG3 tasks and globals, or explicitly use SIG3_LegacyCommand where supported.
- [ ] Disable competing legacy control profiles and remove any active SoundWear profiles.
- [ ] Export the verified phone event profiles so their actual plugin settings and wrappers are preserved.

## 4. Verify reliability and installation

- [ ] Test a second command while SIG3_Worker runs: verify rejection, accurate results and subsequent recovery.
- [ ] Test manual Stop and the next command; verify no stale success or stuck lock.
- [ ] Test locked screen, Signia left on settings, missing controls/overlays, program changes during an operation, DND/bedtime mode, low nonzero selected-stream volume, muted stream and active-call failures as appropriate. Record the current manual recovery from settings: open Controls.
- [ ] Check a fresh project import and the separate Pixel 9a setup task; verify SIG3_Init preserves existing settings and configuration survives Tasker/phone restart.
- [ ] Confirm normal phone operation without an ongoing ADB connection.

## 5. Complete optional automation if it will be used

Keep noise/sleep automation disabled until the relevant items pass. These tasks are implemented; real source configuration and live tests remain.

- [ ] Choose phone or watch noise source and wire the actual polling/sample event. Measure sample sign, units, inversion, low/high thresholds and strike count; do not describe uncalibrated indices as sound-pressure dB.
- [ ] Configure actual quiet/loud program slots and, if wanted, a middle slot; verify consecutive samples, two-tier dead band or three-tier selection, and source isolation.
- [ ] Wire actual sleep/time-provider events to SleepState with explicit asleep/awake input; configure and verify sleep/wake program behavior.
- [ ] Verify foreground deferral, manual override, cancellation/resume and retry on subsequent events. Confirm manual controls remain usable.
- [ ] If Home completion is selected, verify it occurs only after success while Signia remains foreground. Default completion is stay.

## 6. Resolve native accessibility support separately

The default accessibility backend has not passed live movement/commit acceptance. Touch exploration was off during inspection. This is a separate acceptance path from the working balance/tinnitus gesture backend.

- [ ] Decide whether native accessibility must be supported for the finished setup. Record the accepted backend for each family and any unsupported backend clearly.
- [ ] If testing native support, verify native/display mapping before setting each family's RangeConfirmed flag; touch exploration must be intentionally enabled by the user.
- [ ] Test adjacent target, repeat, reverse and audible aid response; record ProgressAccepted, observed value and errors. No automatic backend fallback is available.

## 7. Close out the release record

- [ ] After any code/export changes, rerun the repository checks listed in the [test checklist](HeySig3-test-checklist.md); fix failures and confirm generated exports match source.
- [ ] Update the manual, checklist and phone evidence with accepted configurations, verified profiles, remaining limitations and recovery steps.
- [ ] Preserve the final tested project, separate device setup task and phone profile exports together.

Already established: Tasker balance and tinnitus 0 → 1 → 0 in Universal, TV tinnitus rejection through Up, selected read-only checks, and repository simulations/static validation. These do not complete the remaining live tests above.

Outside current completion scope: relative Up/Down voice phrases, a new EQ controller, spoken-result synthesis, AppBlock, force-close/lock behavior, BLE/root/helper-app control, and automatic secure unlock.
