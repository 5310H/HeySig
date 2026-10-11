# HeySig3 remaining work

Updated October 11, 2026. This is the prioritized completion list, based on the [current test checklist](HeySig3-test-checklist.md), [phone evidence](HeySig3-verified-usb-drags.md), and [event wiring](HeySig3-completion.md). Unchecked items are pending, not necessarily missing implementations. Historical gaps in the main-parity review may already be implemented.

Acceptance clarification: the user reports that the aids provide confirmation only for battery checks, which already work. Program and slider tests use fresh Signia readback and command results; audible aid confirmation is not a completion requirement. This readback does not independently prove acoustic receipt.

Program names must come from actual Signia readback or configured slots, never hardcoded into controls or test guards. Named programs in historical evidence describe what was tested. New tests should capture their starting program and verify that it remains unchanged.

## 1. Finish core slider acceptance

- [ ] Establish a working **Tasker VolumeSet** backend on the phone. Record its configuration, test an adjacent move and reverse, repeat the target to prove no additional movement, and verify fresh app readback. Successful ADB volume drags do not complete this item.
- [x] Run **BalanceSet** directly with Parameter 1: 1 → 0, then repeat 0 and verify no gesture (app readback only).
- [x] Test balance 0 → −1 → 0 with fresh app readback and spoken results.
- [ ] Run **TinnitusSet** directly in Universal: 1 → 0, then repeat 0 and verify no gesture.
- [ ] After small moves pass, test other numbered targets, long jumps and endpoints: volume/tinnitus 0–15, balance −8–7. Restore starting values after testing.
- [ ] Verify availability and current readback in Off just Tinnitus, Noisy, Outdoor and Very Noisy; record actual tab availability rather than infer it from program names.
- [ ] Verify balance/tinnitus movement in another program where each control exists.
- [ ] In TV, run TinnitusCurrent, Set, Mute, Max and Inspect; verify the unavailable error, no movement and no program switch. TinnitusUp already passed.
- [x] Run TinnitusInspect in a program with tinnitus available; record its diagnostics. Passed in Universal during the [verification run](HeySig3-verification-2026-10-10.md).

Completion evidence: chosen per-family backend, starting/target/observed values, command result/error, repeated-target behavior, and fresh app readback. Use the [slider acceptance guide](HeySig3-slider-acceptance.md).

## 2. Verify program, battery and prompted commands

- [x] Read six exact program names from the live picker and fill unset slots; confirm the program opener and battery page selectors on the phone.
- [ ] Configure desired Conversation/Noisy/VeryNoisy aliases when selected.
- [ ] Test SIG3_ProgramCurrent and ProgramSwitch across actual programs, including repeated-current no-op, missing/ambiguous names and failed selection. The slider guard's program read does not certify these separate tasks.
- [x] Investigate and correct the live ProgramCurrent failure, compare active imported tasks with repository exports, and retest in Universal. The repaired read path passed; see the [verification run](HeySig3-verification-2026-10-10.md).
- [x] Investigate the live VolumeCurrent failure and restore a fresh successful read. Importing the repaired tree guard passed in Universal with value 0.
- [ ] Clean up unresolved optional fields in result messages and verify concrete reporting for failed requests.
- [x] Import/run SIG3_BatteryCheck listen: repaired current top-right opener, left request, acknowledge, right request, acknowledge, close; app screen and Tasker result passed, user confirmed.
- [x] Battery indications work, as confirmed by the user; no further audible confirmation test is required.
- [ ] Test prompted mode and battery recognition, configured aliases, empty/cancelled input and override toggle.

## 3. Connect and verify actual phone events

The project supplies tasks but imports **no event profiles**.

- [x] Connect the original AutoVoice recognition profile to SIG3_AutoVoiceCommand; its typed event test reached HeySig3. AutoVoice microphone prompt remains unresolved.
- [x] Verify the separate SIG3_VoiceCommand phone prompt: current-program query, explicit Try again, spoken program result, and spoken program change followed by restoration passed.
- [x] Verify live spoken current-volume, current-balance, and current-tinnitus queries; user confirmed each matched the phone screen.
- [x] Verify live spoken battery request; user confirmed app prompts and spoken confirmation.
- [x] Verify live spoken volume change and restoration: 8 → 7 → 8, with final screen confirmation.
- [x] Verify live spoken balance change and restoration: 0 → -1 → 0, including final screen confirmation.
- [x] Verify live spoken tinnitus change and restoration: 0 → 1 → 0, including final screen confirmation.
- [x] Verify TV spoken volume change/restoration (8 → 7 → 8) and unavailable-tinnitus query explanation.
- [x] Verify spoken DND instruction: check battery stopped and the user heard the instruction.
- [x] Verify spoken low-phone-volume instruction: check battery stopped at media 6/25 and the user heard the instruction.
- [ ] Verify other live spoken blocked-command messages. Complete AutoVoice microphone capture separately.
- [ ] Connect the actual AutoWear command event to SIG3_WatchCommand and verify its input variable and target routing.
- [x] Confirm unrecognized speech followed by Cancel closes without a control change; recorded result says no command sent.
- [x] Verify physical Back dismissal: retry dialog closed immediately without retry or control change.
- [x] Verify retry-dialog timeout: user confirmed automatic closure without retry or control change.
- [x] Verify cancellation inside the microphone prompt: Back before speaking ends quietly without retry, speech, or a control change. Empty silence/timeout results also end quietly.
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
- [ ] Test adjacent target, repeat, reverse and fresh app readback; record ProgressAccepted, observed value and errors. No automatic backend fallback is available.

## 7. Close out the release record

- [ ] After any code/export changes, rerun the repository checks listed in the [test checklist](HeySig3-test-checklist.md); fix failures and confirm generated exports match source.
- [ ] Update the manual, checklist and phone evidence with accepted configurations, verified profiles, remaining limitations and recovery steps.
- [ ] Preserve the final tested project, separate device setup task and phone profile exports together.

Already established: Tasker balance and tinnitus 0 → 1 → 0 in Universal, TV tinnitus rejection through Up, selected read-only checks, and repository simulations/static validation. These do not complete the remaining live tests above.

Outside current completion scope: relative Up/Down voice phrases, a new EQ controller, AppBlock, force-close/lock behavior, BLE/root/helper-app control, and automatic secure unlock.

## Future: save and restore settings after charging

Requested October 11, 2026. The user reports that charging turns the aids off and they restart with default settings. Investigate this behavior separately from Signia app readback.

- [ ] Add explicit Save settings / Restore settings commands. Save fresh verified readings of the actual selected program, volume, balance, and tinnitus when available, with a timestamp and configuration identity. Persist the snapshot across restarts; do not overwrite it with charging defaults automatically.
- [ ] Restore and verify the saved program first, then restore its available controls through the existing worker and audio guards. Skip unavailable tinnitus explicitly; reject changed or ambiguous program mappings and invalid snapshots.
- [ ] Report partial restoration and stop on failures rather than claiming full success. Preserve the saved snapshot for a later manual retry.
- [ ] Test charging/restart, missing tinnitus, renamed programs, partial failures, and accurate app readback after restoration. Begin with user-triggered restoration; any automatic reconnect trigger needs separate verification.

## Future: Hey Sig wake phrase and spoken readiness cue

Requested October 11, 2026: use **“Hey Sig”** as the wake phrase and say **“Sig here”** when ready to receive the command, so the user can operate without viewing the phone.

- [ ] Investigate and implement an explicitly enabled wake-word listener for **“Hey Sig”**, accounting for microphone permissions, battery use, false activations, and Android background restrictions. Provide an easy way to disable listening.
- [ ] Add the spoken readiness cue to the general voice prompt and explicit Try again flow. Sequence playback and microphone capture so recognition does not capture the cue itself; verify that the cue accurately indicates when speech can begin.
- [ ] Test with the screen off and locked, including Android microphone/background restrictions. If recognition or Signia control requires unlocking, give clear spoken instructions where possible; do not bypass the lock screen.
- [ ] Respect the existing speech preference and DND/phone-volume handling. Verify the cue is audible under supported settings and preserve an on-screen indication.

Both wake-word activation and the readiness announcement are future work. No always-listening service is currently enabled; screen-off/locked operation remains unverified.

## Future: spoken-response on/off switch

Requested October 11, 2026: add a visible **Spoken responses** on/off switch so the user can enable or silence voice replies without editing Tasker variables.

- [ ] Connect the switch to the existing `%SIG3_VoiceResponses` setting (0 off, 1 on), show its current state, and persist the choice across restarts.
- [ ] Keep on-screen results available when speech is off. Apply the choice to result replies, retry instructions, and the future **Sig here** readiness cue.
- [ ] Keep wake-word listening independently controlled; turning spoken responses off must not silently change whether **Hey Sig** listening is enabled. Verify both switch states and restart persistence.
