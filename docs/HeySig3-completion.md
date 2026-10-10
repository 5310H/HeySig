# HeySig3 completion and event wiring

Updated October 10, 2026. Import `projects/HeySig3.prj.xml` and run `SIG3_Init`. Existing settings are preserved. Automatic noise/sleep changes remain disabled until configured and tested. SoundWear is removed.

## User commands

- Absolute controls: `change volume to 10`, `change balance to minus 3`, `change tinnitus to 5`.
- Program: `program two`, `change program to Music`, `current program`.
- Battery: `battery check` runs the original left/acknowledge/right/acknowledge/close sequence.
- Prompted recognition: run `SIG3_VoiceMode` or `SIG3_VoiceBattery` to start Tasker's recognition prompt. The mode prompt accepts a slot, exact configured name or semantic alias. Empty/cancelled recognition sends no command.
- `override toggle`, `override on`, `override off`; `sleep` and `wake` use configured SleepState behavior.

Mode aliases require actual slots: `%SIG3_ModeConversationProgram`, `%SIG3_ModeNoisyProgram`, `%SIG3_ModeVeryNoisyProgram`. They enable `sig conversation`, `mode noisy`, `sig vnoisy` and equivalent forms. Alias slots are not guessed from program order. ProgramName1..6 still contain the actual names shown by Signia.

## Noise sources and three tiers

Set `%SIG3_NoiseSource=phone` (default) to use `SIG3_CurrentNoise`. Set it to `watch` to use `SIG3_WatchNoise` with a numeric sample in Parameter 1; no plugin-specific watch variable is assumed. The nonselected capture entry point does nothing. `SIG3_NoiseMonitor` accepts an explicit sample independently of source, for testing or another caller.

Existing sign/units confirmation, inversion, low/high thresholds and strike count apply. Configure `%SIG3_NoiseMiddleProgram` with an actual program slot to enable a third tier: quiet at/below Low, middle between Low and High, loud at/above High. All tiers require consecutive samples. Leave MiddleProgram unset to retain the prior two-tier design with a middle dead band. Sample values are uncalibrated indices, not verified sound-pressure dB.

## Defer and cancel automatic changes

`%SIG3_DeferAutomation=1` defaults to requiring Signia already foreground before automatic noise/sleep program changes. This prevents taking over another app. A deferred operation fails visibly; a subsequent sample/state event can try again. Set 0 only if you want automatic changes to launch Signia while the phone is usable.

`SIG3_CancelAutomation` sets a persistent cancellation flag. `SIG3_ResumeAutomation` clears it. The guard checks the flag before an automatic program-switch call. Cancellation cannot recall a command already handed to Signia; manual controls still work. Manual override independently blocks automatic changes. Neither Resume nor override-off enables noise or sleep by itself.

## Completion navigation

`%SIG3_CompletionPolicy=stay` is the default. `home` goes to Android Home after successful work only if Signia is still foreground. It does not kill Signia, lock the phone or unlock a secure screen. Failures remain available for inspection. The AppBlock scene is not required for the supported workflow and is not imported.

## Legacy caller migration

Old task exports remain references, apart from the requested SoundWear removal. Disable competing legacy profiles. Update phone shortcuts/profiles to public SIG3 task names; do not call Internal tasks.

`SIG3_LegacyCommand` is an explicit adapter for callers you edit: Parameter 1 is an old name such as `SIG_VolumeSet`, Parameter 2 is the numeric target. For Set, an omitted target can use `%SIG_TargetVolume/Balance/Tinnitus`; program switching requires a slot in Parameter 2. Battery and Current/endpoint commands are mapped to the worker. Relative Up/Down callers are rejected; use absolute targets. This task does not intercept an unchanged old profile.

Read `%SIG3_Program` for current program; `%SIG3_Level`, `%SIG3_BalanceLevel`, `%SIG3_TinnitusLevel` for displayed levels. Old `%SIG_CurrentProgram` / `%SIG_Level` are not synchronized: migrate readers explicitly rather than combining controllers. Add ProgramCurrent before a caller needs fresh program state.

## Phone profiles to connect

The repository supplies adapters, not fabricated AutoVoice/AutoWear/sleep-provider event configurations. On the phone:

| Event | Entry task | Input |
|---|---|---|
| AutoVoice Recognized | SIG3_AutoVoiceCommand | Event recognition text; adapter prefers avcommnofilter then avcomm |
| AutoWear Command | SIG3_WatchCommand | Event text; adapter prefers awcomm then awmessage |
| Periodic phone noise | SIG3_CurrentNoise | None; choose the polling interval in the actual Time profile |
| Watch noise event | SIG3_WatchNoise | Actual numeric sample in Parameter 1 via an event wrapper |
| Sleep/time provider | SIG3_SleepState | `asleep` or `awake` via an event wrapper |
| Cancel/resume buttons | SIG3_CancelAutomation / SIG3_ResumeAutomation | None |

Tasker event variables are local to the event task. If a profile needs an intermediate task, use Perform Task to pass the event value explicitly. Export actual configured event profiles from the phone before treating their setup as version-portable XML. No SoundWear profiles should remain active on the phone.

## Acceptance still required

Follow `HeySig3-slider-acceptance.md` for the accessibility commit gate, native range confirmation and audible volume response. Then test Balance/Tinnitus separately. Import/recognition/plugin event/Java Code compatibility and actual acoustic delivery cannot be certified by repository simulations. Program selection and new Current require phone-confirmed IDs. The original battery sequence is user-confirmed working; its SIG3 import still needs verification.

Repository checks cover XML structure, shared numeric action flow, original battery sequence, program read/switch, prompts and cancellation, semantic aliases, override toggle, three-tier noise, watch sample routing, cancellation/resume and legacy adapter flow. Old gesture simulations explicitly select the compatibility backend; they do not prove the new accessibility backend works on the phone.
