# HeySig3 numeric voice controls

The current HeySig3 export now includes numeric Volume, Balance, and Tinnitus controls. Import [HeySig3.prj.xml](../projects/HeySig3.prj.xml) as a new, separate project. The original HeySig project remains unchanged. `SIG3_VolumeCurrent` copies the proven HeySig2 reader into the isolated project; no HeySig2 export is modified.

Run `SIG3_VoiceRouter` with Parameter 1 containing the spoken text, or call it from an AutoVoice recognition task that provides `%avcomm`. Existing recognition profiles are not rewired automatically.

Examples: `volume 10`, `set volume to ten`, `balance minus three`, `balance 0`, `tinnitus five`. Supported ranges are volume/tinnitus 0–15 and balance −8–7. Max/mute and balance sharp/soft phrases also route to numeric targets. Repeating the same number is a no-op after a fresh current query.

`SIG3_VolumeSet`, `SIG3_BalanceSet`, and `SIG3_TinnitusSet` accept an integer in Parameter 1. Out-of-range input fails rather than clamps. Up/Down and endpoint tasks are wrappers around Set. Volume/tinnitus mute requests zero; balance soft/sharp request −8/7.

All public commands enter `SIG3_Worker`. Tasker’s default **Abort New Task** collision policy keeps one worker active; commands arriving while it runs are rejected, not queued. Child tasks run at higher priority. Confirm the worker’s collision setting after import; do not change it to Run Both or Abort Existing. No persistent busy flag needs resetting after failure or manual Stop. Internal tasks are not user entry points.

Each Set reads the active control, starts on its current numbered knob, holds 200 ms, moves one stop over 300 ms using the same pointer, releases, waits 500 ms, and queries again. Every stop must change by exactly one toward the target. An unchanged, skipped, ambiguous, unavailable, or failed reading stops without escalating the distance. At most 16 steps are allowed. `%SIG3_Gesture` records DOWN-HOLD-MOVE-UP timing and mechanism; `%SIG3_Error` records failure; each family has its own `%SIG3_<Family>OK`. Voice completion uses `%SIG3_CommandOK`.

## Calibration before use

Set `%SIG3_KnobId` to the phone-confirmed current-value ID `com.signia.rta:id/TA-SliderValue`, or use the four `%SIG3_KnobXMin/XMax/YMin/YMax` bounds. Its measured step defaults to 40 px through `%SIG3_VolumeStepPx`.

Balance and tinnitus require their own selector: `%SIG3_BalanceKnobId` / `%SIG3_TinnitusKnobId`, or the matching four region bounds such as `%SIG3_BalanceKnobXMin`. Set `%SIG3_BalanceStepPx` and `%SIG3_TinnitusStepPx` to measured adjacent-stop spacing (1–200 px). These distances have no guessed default. Run the respective Current task and inspect `%SIG3_QueryData` before attempting movement. Configure `%SIG3_BalanceDirection` / `%SIG3_TinnitusDirection`: `1` means upward increases the displayed value; `-1` means downward increases it. Volume defaults to `1` from the observed phone behavior. Direction must be confirmed on the phone. Tab labels are `Balance Tab` and `Tinnitus Tab`; unavailable tinnitus fails readback.

Current tasks publish `%SIG3_BalanceLevel/X/Y` and `%SIG3_TinnitusLevel/X/Y`. Volume continues publishing `%SIG3_Level` and `%SIG3_VolumeX/Y`. Your configuration uses the common slider controlling both aids; no separate left/right operation is introduced.

## Validation and limitations

Phone testing should begin with an explicit numbered target, such as `volume 10` or `SIG3_VolumeSet` with Parameter 1 `10`. The legacy Up/Down tasks were not reliable; the rewritten SIG3 Up/Down wrappers remain unverified on the phone. Set currently reaches its target using verified one-stop gestures, not one direct gesture to the target.

The Chromebook can generate and inspect these exports, but cannot test Signia because the app does not run there. Actual import, accessibility, gesture, and acoustic behavior must be tested on the Android phone with Tasker, AutoInput, and Signia.

The simulated XML execution checks all 768 source/target transitions, repeated targets, spoken negative balance values, invalid ranges, missing calibration, unavailable controls, unchanged gestures, overshoot, and gesture failure. Static XML validation also passes. These checks do not execute Tasker's Android importer, Java Code, AutoVoice, or the real Signia app. Import and device verification remain necessary. Displayed readback is Signia app state, not independent hearing-aid acknowledgement.

## Additional prerequisites and operation results

Set `%SIG3_AudioStream` to `media` or `ring`, matching the choice in Signia. Preflight reads phone stream volume, audio mode, DND, and connected output devices without changing them. It rejects muted stream, an active call/communication mode, known connected external audio outputs, and silent/DND ringtone playback. Connected outputs are a conservative presence check, not an active-route measurement. Signia still owns its configurable audio thresholds; no guessed 50–90% setting is imposed. The phone must be on and unlocked.

The UI guard requires one visible enabled common control and one visible current-program node. APK-derived defaults (not yet phone-confirmed) are:

| Variable | Initial ID |
|---|---|
| `%SIG3_VolumeControlId` | `com.signia.rta:id/VolumeSlider` |
| `%SIG3_BalanceControlId` | `com.signia.rta:id/TA-SoundBalanceSlider` |
| `%SIG3_TinnitusControlId` | `com.signia.rta:id/TA-TinnitusSlider` |
| `%SIG3_ProgramId` | `com.signia.rta:id/TA-ProgramName` |

Override these with IDs observed in your phone's UI query. The control ID must uniquely identify the visible control for that family; a reused numeric label ID alone is insufficient. A missing control/program or changed program causes failure rather than guessing. Dialogs that hide these nodes likewise fail. These checks do not prove every possible overlay is absent.

Run `SIG3_Calibrate` with Parameter 1 `Balance` or `Tinnitus` and Parameter 2 such as `40,1` (measured pixel spacing, direction). It performs a read-only Current check and stores calibration only after successful validation. It does not measure spacing itself: inspect adjacent numbered stops first. Verify actual ranges on the phone against volume/tinnitus 0–15 and balance −8–7; changed ranges require updating the generator before movement. Defaults never overwrite already configured IDs.

`%SIG3_OperationId`, `%SIG3_Family`, `%SIG3_Target`, `%SIG3_Program`, `%SIG3_Previous`, `%SIG3_Expected`, `%SIG3_Observed`, `%SIG3_MoveStage`, and `%SIG3_AudioDiagnostics` describe the operation. `%SIG3_Result` is logged and shown as a toast at completion. A manually stopped operation may retain a pending result, but does not leave a lock. `%SIG3_CommandOK` describes the last accepted operation, not a rejected/unrecognized voice request. Requests rejected as busy leave the owner's diagnostics intact. No automatic retry is made.

Signia stays open through verification and afterward. This is the current explicit cleanup policy; no automatic Back, force-close, screen lock, or return to another app occurs. A successful result says **Signia displayed the level**, not that the hearing aids acknowledged it. Test volume 9→10, repeat 10, 10→9, 1→0 and 0→1 separately; repeat equivalent minimum-boundary checks for tinnitus if available.

## Supported import and legacy migration

Import only `projects/HeySig3.prj.xml` for the new slider workflow. Point voice/button/watch adapters to `SIG3_VoiceRouter` or the public SIG3 Set tasks. Disable old slider-triggering profiles while testing; their events can otherwise operate Signia outside the new worker. Keep `HeySig.prj.xml`, `sig.tasks.tsk.xml`, and `xml/backup.xml` as references/backups, not competing active imports. Original SIG tasks remain untouched. Priority 3 now supplies the program, battery, noise, sleep, initialization, and event-adapter tasks described below.

The worker relies on [Tasker’s documented default collision policy](https://tasker.joaoapps.com/userguide/en/tasks.html), [child task priority behavior](https://tasker.joaoapps.com/userguide/en/help/ah_run_task.html), and the live [Tasks Running variable](https://tasker.joaoapps.com/userguide/en/variables.html). Android guards use [Tasker Java Code](https://tasker.joaoapps.com/userguide/en/help/ah_java_code.html). Export simulations model these APIs; on-phone import and execution remain necessary.


## Priority 3 setup

Run `SIG3_Init` once after import. It fills missing settings and preserves existing ones. Noise and sleep automation default to **disabled**. No profile is installed or activated by the export.

Configure `%SIG3_ProgramName1` through `%SIG3_ProgramName6` with the exact names of programs actually available in Signia; leave unused slots unset. `SIG3_ProgramSwitch` accepts the slot number in Parameter 1. Voice accepts `program two` or `change program to Music`. It reads the current program, opens the picker, clicks a uniquely matching visible name, and verifies the displayed program with bounded waits. Repeating the current program is a no-op. No coordinate fractions or cached success assignments are used.

Additional APK-derived IDs require confirmation from the phone:

| Variable | Initial ID |
|---|---|
| `%SIG3_ProgramOpenId` | `com.signia.rta:id/TA_HomePage_ProgramSwitch_Icon` |
| `%SIG3_BatteryOpenId` | `com.signia.rta:id/TA-BatteryIcon` |
| `%SIG3_BatteryPageId` | `com.signia.rta:id/TA-BluetoothAndBatteryPageCloseIcon` |

`SIG3_BatteryCheck` defaults to Parameter 1 `open`: open/recognize the battery page and record visible text in `%SIG3_BatteryText`. Parameter 1 `listen` additionally clicks a **phone-confirmed** `%SIG3_BatteryRequestId`, with audio preflight. There is no default request button, no left/right routing, and no inferred percentage. A click result does not confirm receipt or decode the audible indication. Voice phrases are `battery check` and `battery listen`. The page remains open; return to the home control page before another operation if needed.

### Voice and watch events

Create or edit an actual AutoVoice recognition profile on the phone to run `SIG3_AutoVoiceCommand`. It prefers the event's `%avcommnofilter`, falling back to `%avcomm`. Connect the actual AutoWear command event to `SIG3_WatchCommand`; it prefers `%awcomm`, falling back to `%awmessage`. Both adapters accept explicit command text in Parameter 1, trim it, remove an optional leading `sig3 `, and pass it to the same router. Verify which event variables your installed plugins expose; use Parameter 1 explicitly when necessary. Plugin-specific Profile XML is deliberately absent because an authentic export from those installed event versions is unavailable. Disable competing legacy profiles while testing.

### Noise and sleep

`SIG3_CurrentNoise` uses the existing repository's AutoVoice Current Noise action envelope, then processes `%avnoiselevel`. Its compatibility still needs phone testing. `SIG3_NoiseMonitor` instead accepts a numeric sample in Parameter 1. Both use the worker, so sampling and Signia operations cannot interleave through SIG3. `%SIG3_NoiseRaw` preserves the input and `%SIG3_NoiseIndex` records the optionally inverted value. These values are **uncalibrated indices**, not established sound-pressure dB.

To enable noise-driven program selection after manual controls work, confirm the sample's units/sign on the phone, set `%SIG3_NoiseScaleConfirmed=1`, and configure:

- `%SIG3_NoiseInvert`: `0` to preserve the sign, `1` to negate it.
- `%SIG3_NoiseLow` and `%SIG3_NoiseHigh`: measured thresholds, low strictly below high.
- `%SIG3_NoiseQuietProgram` and `%SIG3_NoiseLoudProgram`: configured slots 1–6.
- `%SIG3_NoiseStrikeLimit`: consecutive samples required, 1–20; default 3.
- `%SIG3_NoiseEnabled=1`: enable automatic selection.

The middle band clears the candidate/count. Changing quiet/loud classification restarts the count. Once the count reaches the limit, program selection runs through the same worker and readback path. Sampling frequency is supplied by a phone profile; no timer is activated here. `%SIG3_SleepActive=1` suppresses noise changes.

`SIG3_Override` takes `1` for manual override or `0` to release it; voice accepts `override on/off` and `manual/automatic mode`. Override blocks noise/sleep program changes and resets noise history. Releasing override does not itself enable either automation.

`SIG3_SleepState` accepts `asleep` or `awake`. It requires `%SIG3_SleepEnabled=1`, configured `%SIG3_SleepProgram` / `%SIG3_WakeProgram` slots, and no manual override. A real time/sleep-provider profile must supply that state. The task selects and verifies the configured program before updating `%SIG3_SleepActive`. It does not infer sleep, use a hearing-aid standby enum, or assume that a program mutes the microphone.

Priority 3 tests model initialization preservation, program routing/readback failures, voice/watch inputs, battery request configuration, native noise capture, sign handling, thresholds/strike count, override, and sleep transitions. They do not execute Android accessibility, BeanShell, plugin events, or acoustic playback. On-phone import and capture remain the acceptance step.
