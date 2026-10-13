# HeySig3 completion and event wiring

Updated October 12, 2026. See the [user manual](HeySig3.md), [completed/remaining test checklist](HeySig3-test-checklist.md), and [phone verification notes](HeySig3-verified-usb-drags.md). Import `projects/HeySig3.prj.xml` and run `SIG3_Init`. Existing settings are preserved. Automatic noise/sleep changes remain disabled until configured and tested. SoundWear is removed.

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

The project includes the opt-in AutoVoice Continuous wake profile. Configure other AutoVoice/AutoWear/sleep-provider events separately. On the phone:

| Event | Entry task | Input |
|---|---|---|
| AutoVoice Continuous Hey Sig / Hey Cig | SIG3_WakeTrigger | Whole wake phrase; regex on, Exact Command off |
| AutoVoice Recognized | SIG3_AutoVoiceCommand | Event recognition text; adapter prefers avcommnofilter then avcomm |
| AutoWear Command | SIG3_WatchCommand | Event text; adapter prefers awcomm then awmessage |
| Periodic phone noise | SIG3_CurrentNoise | None; choose the polling interval in the actual Time profile |
| Watch noise event | SIG3_WatchNoise | Actual numeric sample in Parameter 1 via an event wrapper |
| Sleep/time provider | SIG3_SleepState | `asleep` or `awake` via an event wrapper |
| Cancel/resume buttons | SIG3_CancelAutomation / SIG3_ResumeAutomation | None |

Tasker event variables are local to the event task. If a profile needs an intermediate task, use Perform Task to pass the event value explicitly. Export actual configured event profiles from the phone before treating their setup as version-portable XML. No SoundWear profiles should remain active on the phone.

## Verified setup and remaining acceptance

Direct Tasker volume 8 → 7 → 8 in Noisy, balance/tinnitus adjacent changes, repeated-target no-ops and restoration passed using fresh Signia readback. Known unavailable program icons stop tinnitus requests without a tab search. Native accessibility movement and broader endpoint checks remain separate. Physical aid responses are not required for program/slider acceptance; battery indications already work.

The general voice task passed program/current-value queries, numeric changes, battery, retry and cancellation. Spoken **cancel** exits cleanly; **tin** is a tinnitus shorthand. Automatic saved settings and **restore settings** passed app-only checks. See the [manual](HeySig3.md) and [saved settings](HeySig3-saved-settings.md).

`SIG3_VoiceSettings` independently controls voice prompts and results. All four combinations and two Tasker application restarts passed. Full phone reboot remains untested.

The wake profile requires regex on and Exact Command off; AutoVoice Stream to Mute must be Media. Two consecutive cue/microphone/reply flows, locked unlock guidance/manual recovery and restoration of media to 22/25 after stopping passed. Background wake subsequently failed despite the foreground service remaining active. Listening was left off; use the direct voice task. See [wake limitations](HeySig3-wake-phrase.md).

All 19 repository checks passed after the October 12 changes. Some helper checks execute actual Java in local BeanShell; simulations do not establish Android/plugin delivery. Watch events, optional noise/sleep automation, long-duration background/battery endurance and other unchecked phone paths remain open in the [checklist](HeySig3-test-checklist.md).
