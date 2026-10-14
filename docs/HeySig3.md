
# HeySig3 user manual

Updated October 12, 2026. Use this manual for operation, the [test checklist](HeySig3-test-checklist.md) for completed and remaining checks, and the [phone verification notes](HeySig3-verified-usb-drags.md) for measured results. [Completion and event wiring](HeySig3-completion.md) covers profiles and optional automation.

## Current verified setup

The Pixel 9a passed direct Tasker volume 8 → 7 → 8 in Noisy, balance and tinnitus adjacent changes, repeated-target no-ops, and restoration using fresh Signia app readback. See the [checklist](HeySig3-test-checklist.md) for individual results and untested endpoints. Physical hearing-aid confirmation is not required for program/slider acceptance; battery indications already work.

Tinnitus availability comes first from the icon left of the active program name. A known unavailable icon stops with **Tinnitus unavailable for this program**, without searching for a tinnitus tab. Unknown icons use visible-tab detection as a fallback. Program names and availability are not hardcoded. TV's two-tab layout and programs with three tabs passed phone checks.

Balance displays **−8 through 0 through +7**. Native step 0 maps to −8, step 8 to 0, and step 15 to +7. Volume and tinnitus display 0–15. Signia app readback does not independently acknowledge receipt by the hearing aids.

Balance and tinnitus use the explicitly configured `legacy-gesture` backend on this phone. It now sends one continuous 650 ms stroke, locates the thumb from native progress and calibrated track endpoints, and checks the displayed result after each step. Despite its compatibility name, this is the path that passed the Tasker phone tests. It needs no ongoing ADB connection or helper app.

The general project default remains `accessibility`, which uses one `ACTION_SET_PROGRESS`. That path requires confirmed native/display mapping and touch exploration. Inspection reported touch exploration off on this phone, so native Set remains gated and has not passed a live movement test. Backend selection never falls back automatically. Per-family settings let balance/tinnitus use gestures without changing the Volume backend.

Direct Tasker VolumeSet passed 8 → 7 → 8 in Noisy using the configured dispatchGesture backend, including repeated targets without movement and restoration. This does not certify the separate native accessibility backend or all endpoints.

## Import and setup

1. Import [HeySig3.prj.xml](../projects/HeySig3.prj.xml) as the separate HeySig3 project, preserving phone-side settings. Keep the original HeySig exports as backups and disable competing old slider profiles while testing.
2. Enable Tasker accessibility, keep the phone on and unlocked, and open Signia's **Controls** page. Launching Signia while it was left on App settings failed the launch check during testing.
3. Run `SIG3_Init` to fill missing defaults. Existing settings are preserved; noise/sleep automation defaults off.
4. For the measured Pixel 9a layout only, import [SIG3_Pixel9aGestureSetup.tsk.xml](../tasks/SIG3_Pixel9aGestureSetup.tsk.xml) as a separate task and run `SIG3_Pixel9aGestureSetup`. This selects the balance/tinnitus gesture backends and stores their calibration. It fills an unset audio-stream setting with `media`, matching the observed Signia **Media sound** setting. It does not change an existing audio-stream setting or the Volume backend.

The setup was already run on the tested phone. Its calibration is portrait 1080×2424, slider bounds `[501,652][580,2047]`, track endpoints Y=695/2000, StepPx=87, and Direction=1 (up increases). It overwrites balance/tinnitus calibration settings when run; do not apply these measurements to another device or layout. Changed bounds stop the calibrated position check and require fresh measurements.

## Commands

See the [voice command list](HeySig3-voice-commands.md) for every supported phrase, numeric ranges, configured program aliases, and optional automation commands.

Run `SIG3_VoiceCommand` in Tasker for the general microphone prompt. With voice prompts enabled it says **Sig here**, then opens the microphone. Speak one command; the task speaks the verified result when spoken results are enabled. Program, numeric controls, battery, cancellation and retry have live phone acceptance; see [voice verification](HeySig3-voice-verification-2026-10-11.md).

Run `SIG3_VoiceSettings` to independently turn **Voice prompts** and **Spoken results** on or off, then tap **Save**. Cancel or Back preserves the previous choices. Both may be off while capture and on-screen results continue. All four combinations and two Tasker application restarts passed; full phone reboot remains untested. These switches do not turn wake listening on or off. See [voice settings](HeySig3-voice-settings.md).

Say **cancel** in the microphone prompt to close cleanly without sending a command or opening Try again. Unsupported speech offers **Try again / Cancel**; retry opens a new prompt. Empty input, Back and timeout end quietly.

### Optional Hey Sig listening

Run `SIG3_WakeEnable` to start, or `SIG3_WakeDisable` to stop. Say **Hey Sig**, wait for **Sig here** and the microphone, then say your command. **Hey Cig** is a recognition alias; speaking the wake phrase and command together is unsupported. AutoVoice's wake event needs **Use Regex on** and **Exact Command off**. Set AutoVoice **General Settings → AutoVoice Continuous → Stream to Mute → Media** to suppress repeated tones.

Two consecutive full wake commands passed without tones. A locked phone gave the spoken unlock instruction, and the command worked after manual unlock. **Background wake still failed**, even though its service remained running; use the direct voice task when wake listening does not respond. Full phone reboot and long-duration battery/endurance remain untested. See [wake setup and limitations](HeySig3-wake-phrase.md).

Media suppression temporarily mutes media while continuous listening is active. Pausing/stopping restores the captured level before speech; stopping restored the tested 22/25 level. Listening was left off after testing. To turn the listening microphone off, run `SIG3_WakeDisable`; silencing prompts does not stop listening.

Pass spoken text in Parameter 1 of `SIG3_VoiceRouter`, or use the configured AutoVoice adapter:

| Request | Example | Range |
|---|---|---|
| Volume | `change volume to 10` | 0–15 |
| Balance | `change balance to minus 3` | −8–7 |
| Tinnitus | `change tinnitus to 1` | 0–15, only when available |

Short forms such as `volume 10`, `balance 0`, and `tin one` also work. **Tin** is a shorthand for tinnitus: `current tin`, `tin 3`, and `tin mute`. The live `current tin` test correctly reported unavailable for the active program. Volume/tinnitus mute requests 0; balance soft/sharp requests −8/7. Invalid targets fail rather than clamp. Repeating a target is a no-op after a fresh current query. Router behavior has simulated coverage; actual recognition and event delivery remain on the checklist.

The gesture backend defaults to one-level steps with fresh readback after each step. An opt-in **direct slider drag** uses one continuous 650 ms stroke to the requested position, then checks the final value. Set the desired family’s DragMode to `direct` (`%SIG3_VolumeDragMode`, `%SIG3_BalanceDragMode` or `%SIG3_TinnitusDragMode`) with its `legacy-gesture` backend and measured track endpoints/bounds. Changed bounds stop the operation. A missed target reports failure after that one stroke; it does not retry automatically. Set the mode to `incremental` to return to the existing method. Both modes show/speak only the finished result. See [direct-slider setup and verification](HeySig3-direct-volume.md). Direct mode passed normal Tasker volume 10 → 7 → 10 and balance −4 → −1 → −4 on October 12; tinnitus 0 → 3 → 0 also passed with a brief activation tap at zero. The separate native accessibility backend remains independently unverified.

For manual numbered requests, use `SIG3_VolumeSet`, `SIG3_BalanceSet`, or `SIG3_TinnitusSet` with an integer in Parameter 1. Public Up/Down tasks are compatibility wrappers around Set; balance/tinnitus wrappers passed the adjacent phone tests above. Relative Up/Down voice phrases are not routed. Use public SIG3 tasks, not Internal tasks.

All public UI commands use `SIG3_Worker`. Keep its Tasker collision setting **Abort New Task**: a new command while it is running is rejected, not queued. No persistent busy flag needs resetting after failure or manual Stop. Do not enable competing legacy profiles during acceptance testing.

## Readback and program checks

The verified current-value ID is `com.signia.rta:id/TA-SliderValue`. Volume uses `%SIG3_KnobId`; balance/tinnitus use `%SIG3_BalanceKnobId` / `%SIG3_TinnitusKnobId`. A calibrated selector region remains an alternative. The numeric label's oversized accessibility bounds do not locate its thumb reliably; the Pixel setup supplies track calibration instead.

| Family | Verified control ID | Actual tab description |
|---|---|---|
| Volume | `com.signia.rta:id/VolumeSlider` | `Volume Tab` |
| Balance | `com.signia.rta:id/TA-SoundBalanceSlider` | `Sound Sharpness Tab` |
| Tinnitus | `com.signia.rta:id/TA-TinnitusSlider` | `Tinnitus Signal Tab` |

Direct view-ID lookup returned zero matches on this phone. The repaired inspection/UI guards traverse the accessibility tree and require the exact visible enabled control. Inspection does not move a slider.

Signia changes the program label ID with the selected program (`Universal`, `TV`, etc.). The slider guard also recognizes the uniquely visible **Hearing program … Active** accessibility header when the configured `%SIG3_ProgramId` label is absent. Ambiguity, disagreement, or a program change during an operation fails the guard. Read-only balance detection passed in TV. ProgramCurrent and a program change followed by restoration also passed on the phone; program names came from the actual picker.

Current tasks publish `%SIG3_Level` for volume, `%SIG3_BalanceLevel`, and `%SIG3_TinnitusLevel`, plus their family X/Y coordinates. The controls are common sliders; no separate left/right operation is introduced.

## Audio checks and results

Set `%SIG3_AudioStream` to `media` or `ring`, matching Signia. Preflight reads stream volume, call/audio mode, DND, and connected outputs without changing them. It stops with instructions when DND/bedtime mode is active, the phone is silent, the selected stream is below the configured minimum, a call/communication mode is active, or a known external output is connected. Ring sound also requires normal ringer mode. Command audio preflight does not change those settings. Optional wake listening separately restores its captured media level as described above. The tested Media sound stream was unmuted and routed to the speaker. Connected-output checks are conservative presence checks, not proof of the active route.

Run `SIG3_PhoneAudioCheck` to check Android phone audio without opening Signia or sending a hearing-aid command. `%SIG3_AudioReady` is 1 on success and 0 on failure; `%SIG3_Error` tells you what to change, and `%SIG3_AudioDiagnostics` includes the measured volume and required level. This checks phone volume, not hearing-aid volume.

`%SIG3_MinAudioPercent` defaults to 50, matching the inspected Signia APK audio manager default. For a 25-step stream this requires 13/25, rounding up. Signia can configure its own threshold; if its volume-slider prompt requires a higher level, set this variable to that confirmed minimum. Match `%SIG3_AudioStream` to Signia’s Media sound or Ring sound selection. Check before retrying; HeySig3 does not move the phone volume slider or dismiss Signia’s prompt automatically. Battery `listen` also runs audio preflight before either acoustic check; battery `open` remains read-only.

Read `%SIG3_CommandOK`, `%SIG3_Error`, and `%SIG3_Result` after a command. `%SIG3_Previous`, `%SIG3_Expected`, `%SIG3_Observed`, `%SIG3_Program`, `%SIG3_MoveStage`, `%SIG3_Gesture`, and `%SIG3_AudioDiagnostics` help diagnose it. Java checks preserve their error messages; parent guards avoid overwriting them with a literal `%SIG3_Error`. A stopped command may retain a pending result; busy/unrecognized requests do not represent a new successful operation. No automatic retry is made.

Signia remains open by default (`%SIG3_CompletionPolicy=stay`). `home` returns to Android Home only after successful work while Signia is still foreground. See [completion policies](HeySig3-completion.md#completion-navigation).

## Testing status

Follow the [completed and remaining checklist](HeySig3-test-checklist.md). All 20 repository checks passed after the October 12 direct-slider changes. [Static validation](HeySig3-validation.md) checked 91 XML files and 6,725 actions with zero failures. Some checks execute actual Java bodies in local BeanShell; simulations do not replace Android/plugin or live recognition acceptance. Background wake, full phone reboot, long-duration endurance, native accessibility movement and broader endpoint checks remain open.
The Chromebook generates/validates the project; Signia runs on the phone. USB and authorized wireless ADB were used for inspection/import/testing, not as a requirement for the Tasker balance/tinnitus control path.

## Priority 3 setup

Run `SIG3_Init` once after import. It fills missing settings and preserves existing ones. Noise and sleep automation default to **disabled**. The export includes the exact-match AutoVoice wake profile; its listener remains off until `SIG3_WakeEnable` runs. See [Hey Sig wake setup](HeySig3-wake-phrase.md).

Configure `%SIG3_ProgramName1` through `%SIG3_ProgramName6` with the exact names of programs actually available in Signia; leave unused slots unset. `SIG3_ProgramSwitch` accepts the slot number in Parameter 1. Voice accepts `program two` or `change program to Music`. It reads the current program, opens the picker, selects a uniquely matching visible name, and verifies the displayed program with bounded waits. `%SIG3_ProgramBackend=accessibility-click` uses clickable accessibility ancestors; `gesture-tap` explicitly taps centers of the current visible node bounds and waits for Android completion. There is no automatic fallback between them. The phone-specific tap choice does not alter slider backends. Repeating the current program is a no-op. No coordinate fractions or cached success assignments are used.

Run `SIG3_ProgramCurrent` to read the current displayed program without changing it. Voice accepts `current program`, `current mode`, or `what is the current program?`. The result is stored in `%SIG3_Program` and `%SIG3_Observed`, with `%SIG3_ProgramOK` / `%SIG3_CommandOK` reporting success. It launches Signia if needed, reads the configured visible program label or the unique visible **Hearing program … Active** header, rejects ambiguous or disagreeing readings, and leaves the app open. It does not require audio settings or configured program slots; it does not open the program picker or send an acoustic command. The worker shows/logs the result. A missing or ambiguous program fails instead of returning stale state.

Additional APK-derived IDs require confirmation from the phone:

| Variable | Initial ID |
|---|---|
| `%SIG3_ProgramOpenId` | `com.signia.rta:id/TA_HomePage_ProgramSwitch_Icon` |
| `%SIG3_BatteryOpenId` | `com.signia.rta:id/TA-BatteryIcon` |
| `%SIG3_BatteryPageId` | `com.signia.rta:id/TA-BluetoothAndBatteryPageCloseIcon` |

`SIG3_BatteryCheck` defaults to `listen`, preserving the user-confirmed working HeySig battery check: open the battery page, click `Check Left Battery Button`, acknowledge `TA-PopupButton2`, click `Check Right Battery Button`, acknowledge again, and close the battery page. The original waits and AutoInput settings are preserved. Both `battery check` and `battery listen` run this sequence through the SIG3 worker. No `%SIG3_BatteryRequestId` configuration is needed. Plugin errors stop the sequence and report which action failed.

Parameter 1 `open` remains an optional page-only inspection that records visible text in `%SIG3_BatteryText` and leaves the page open. Normal checks close the battery page and leave Signia open, following SIG3's completion policy. Battery indications are heard from the aids; no numeric percentage is inferred. The repaired SIG3 battery sequence passed its phone import/run check and the user confirmed it worked. The user confirmed battery indications already work.

### Voice and watch events

Create or edit an actual AutoVoice recognition profile on the phone to run `SIG3_AutoVoiceCommand`. It prefers the event's `%avcommnofilter`, falling back to `%avcomm`. Connect the actual AutoWear command event to `SIG3_WatchCommand`; it prefers `%awcomm`, falling back to `%awmessage`. Both adapters accept explicit command text in Parameter 1, trim it, remove an optional leading `sig3 `, and pass it to the same router. Verify which event variables your installed plugins expose; use Parameter 1 explicitly when necessary. The wake profile uses an authentic installed AutoVoice event export. General command and AutoWear profiles still require phone configuration. Disable competing legacy profiles while testing.

### Noise and sleep

Use [selectable phone noise settings](HeySig3-noise-settings.md) to choose Quiet/Noisy/Very noisy roles and tuning. `SIG3_NoiseObserve` starts observation-only sampling; `SIG3_NoiseAuto` enables guarded switching; `SIG3_NoiseStop` stops either mode. Save leaves switching off. Measured Pixel boundaries −54.5 / −43, margin 1.5, three confirmations and 60-second cooldown passed real polling. Hidden-Tasker observation passed over twelve minutes, plus two screen-off captures; [acceptance and limits](HeySig3-noise-settings-acceptance-2026-10-14.md).

`SIG3_CurrentNoise` uses the existing repository's AutoVoice Current Noise action envelope, then processes `%avnoiselevel`. Five quiet-room samples passed on Pixel 9a after correcting the plugin timeout; see [phone noise verification](HeySig3-phone-noise-2026-10-14.md). Later fixed-position quiet/normal/louder measurements and automatic program selection passed the measured acceptance linked above. `SIG3_NoiseMonitor` instead accepts a numeric sample in Parameter 1. Both use the worker, so sampling and Signia operations cannot interleave through SIG3. `%SIG3_NoiseRaw` preserves the input and `%SIG3_NoiseIndex` records the optionally inverted value. These values are **uncalibrated indices**, not established sound-pressure dB.

To enable noise-driven program selection after manual controls work, confirm the sample's units/sign on the phone, set `%SIG3_NoiseScaleConfirmed=1`, and configure:

- `%SIG3_NoiseInvert`: `0` to preserve the sign, `1` to negate it.
- `%SIG3_NoiseLow` and `%SIG3_NoiseHigh`: measured thresholds, low strictly below high.
- `%SIG3_NoiseQuietProgram` and `%SIG3_NoiseLoudProgram`: configured slots 1–6.
- `%SIG3_NoiseStrikeLimit`: consecutive samples required, 1–20; default 3.
- `%SIG3_NoiseEnabled=1`: enable automatic selection.

With NoiseMiddleProgram unset, the middle band clears the candidate/count; configuring that slot enables three-tier selection. Changing quiet/loud classification restarts the count. Once the count reaches the limit, program selection runs through the same worker and readback path. `SIG3_NoiseObserve` and `SIG3_NoiseAuto` explicitly start the polling task, with a five-second capture and ten-second wait; actual cadence also includes processing and switching time. No automatic startup profile is installed. `%SIG3_SleepActive=1` suppresses noise changes.

`SIG3_Override` takes `1` for manual override or `0` to release it; voice accepts `override on/off` and `manual/automatic mode`. Override blocks noise/sleep program changes and resets noise history. Releasing override does not itself enable either automation.

`SIG3_SleepState` accepts `asleep` or `awake`. It requires `%SIG3_SleepEnabled=1`, configured `%SIG3_SleepProgram` / `%SIG3_WakeProgram` slots, and no manual override. `SIG3_SleepSettings` selects both programs and clock times. The exported `SIG3_SleepSchedule` / `SIG3_WakeSchedule` profiles submit the same asleep/awake requests to the worker at those times. Save leaves switching off; `SIG3_SleepEnable` arms the schedule and `SIG3_SleepDisable` stops it. External sleep providers can still call `SIG3_SleepState` directly. See [selectable sleep settings](HeySig3-sleep-settings.md). The task selects and verifies the configured program before updating `%SIG3_SleepActive`. It does not infer sleep, use a hearing-aid standby enum, or assume that a program mutes the microphone.

Priority 3 tests model initialization preservation, program routing/readback failures, voice/watch inputs, battery sequence and page-only mode, native noise capture, sign handling, thresholds/strike count, override, and sleep transitions. These workflow simulations do not execute Android accessibility, plugin events or acoustic playback; separate helper checks execute Java in local BeanShell. On-phone import and capture remain the acceptance step.

## Battery page entry

`SIG3_BatteryCheck` defaults to `listen`: phone audio preflight, open the top-right question-mark battery icon, request left, acknowledge, request right, acknowledge, then close. Parameter1 `open` only opens the page and records visible text; it has no audio preflight and sends no battery-check request. Neither mode uses a slider.

The current app’s top-right opener has content description `TA-BatteryToolbarItem`. `%SIG3_BatteryOpenDescription` supplies that captured selector when `%SIG3_BatteryOpenId` has no match. The `TA-BatteryIcon` ID appears twice inside the page on this phone; it is not a unique Controls toolbar selector. The close marker is `%SIG3_BatteryPageId`. Open mode rejects ambiguous markers/openers, and `%SIG3_MoveStage` identifies each listen step.

## Save and restore the last settings

Successful HeySig3 changes automatically save the current program, volume, balance and tinnitus level when available. For a known program, the changed value updates the complete saved record. Say **“restore settings”** to apply that record after charging. An optional **“save settings”** command refreshes all current readings. See [saved-settings behavior and verification](HeySig3-saved-settings.md). Verification covers saved settings and Signia app readback; a physical charging test is outside the requested scope.
