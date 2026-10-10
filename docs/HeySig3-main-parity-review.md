# Main versus HeySig3 functionality review

Re-audited October 10, 2026. Baseline: local `main` at `91cd6474e2491e1a41bfaf8081b0784744175402`. Compared with current `HeySid3` checkout at `c458d0ddbc9f0e6481cc5531deba76be5ad8e5f7`, including its generated HeySig3 export. The branch is spelled HeySid3; the project/task prefix is HeySig3/SIG3. No branch named HeySig2 exists locally; that separate project lives on `codex`. This review follows the correction to compare **HeySig3**.

**HeySig3 has broader task coverage than its original numeric scope, but it is not behaviorally equivalent to main.** Missing voice phrases, prompted recognition and three-tier noise selection remain differences. The working battery sequence has now been restored. Some advertised main functionality exists only as documentation or placeholder actions. Task presence does not prove physical execution: the new default slider backend uses accessibility progress and still requires phone confirmation of acoustic command commit.

User constraints remain acoustic control, no BLE, no root, no persistent ADB, and no helper application. This review changes documentation only.

## Implementation status — October 10

Repository parity work now adds prompted mode/battery recognition, configured semantic aliases, override toggle, optional three-tier noise, a watch numeric-sample adapter/source policy, cancellation/resume, default foreground deferral, optional Home completion and an explicit legacy caller adapter. Battery and ProgramCurrent are restored. SoundWear was removed at the user's request. Numeric slider code is shared across all three families.

See [completion and event wiring](HeySig3-completion.md) for the final supported behavior. Old source comparisons below are the findings that prompted implementation, not a claim that these tasks are still missing. Actual plugin event profiles, configured program/control IDs and acoustic reception remain phone acceptance items. No functional EQ controller was established in main; its placeholder is not implemented. Spoken-result synthesis was an optional suggestion, not main parity, and remains absent. AppBlock/force-close/lock are replaced by an explicit completion policy rather than copied.

## Subsequent phone verification — October 10

The historical findings below predate the slider repair in [cc3fc3f](https://github.com/5310H/HeySig/commit/cc3fc3f). Balance and tinnitus now have successful Tasker 0 → 1 → 0 tests in Universal through the explicitly configured Pixel 9a gesture backend. TV's missing tinnitus tab stops cleanly without a gesture. Updated read-only checks passed for tinnitus in Universal and balance in TV. Native accessibility movement, Tasker's Volume Set and aid receipt remain separate acceptance items. Use the [current checklist](HeySig3-test-checklist.md) rather than the historical unresolved-slider finding to plan testing.

## Original audit findings

## Findings in priority order

### 1. Resolved by scope: use absolute numeric voice targets

Main `tasks/SIG_VoiceRouter.tsk.xml` act11–19 recognizes `volume down`, `turn it down`, `decrease volume`, `volume up`, `turn it up`, and `increase volume`, then calls the dispatcher. HeySig3 `SIG3_VoiceRouter` contains numeric targets and endpoint/program/battery/noise/override phrases, but **no Up/Down voice branch**, despite public `SIG3_VolumeUp/Down`, BalanceUp/Down and TinnitusUp/Down tasks existing.

Additional main synonyms absent from SIG3 include `silence`, `volume zero`, bare `max`, `max volume`, `full volume`, and `go to volume ...` / `make volume ...`. `volume 15` and ordinary numeric requests are present. Main's loose matching can produce unwanted overlap, so restore explicitly anchored phrases rather than copying its regex verbatim.

User decision: simplify all three controls to absolute targets such as `change volume to 10`, `change balance to minus 3`, and `change tinnitus to 5`. These phrases already route to Set. Do not restore relative Up/Down voice branches. Existing task wrappers remain only for compatibility; endpoint voice aliases now dispatch directly to numeric Set targets. The physical Set backend still needs a working command mechanism; a numeric phrase is not proof of direct volume transmission.

### 2. Restored: working acoustic battery sequence

The user confirms the original HeySig battery check worked. SIG3 now preserves `tasks/SIG_BatteryCheck.tsk.xml` act2–12, including original AutoInput envelopes and waits: open page, request left, acknowledge `TA-PopupButton2`, request right, acknowledge again, close page. The generator adds worker ownership and immediate plugin-error reporting. `SIG3_BatteryCheck` defaults to `listen`; `battery check` and `battery listen` both use this sequence. The old single configured request was replaced; no new button calibration is required.

Optional `open` remains page-only inspection. Signia stays open after normal checks; legacy app-close/screen-lock/scene cleanup is omitted to follow SIG3's current policy. The migrated export requires a phone import/run check, but the source sequence is user-confirmed working.

Standalone prompted `SIG_Voice_Battery_Chk_Pgm` is still a separate parity gap; it was not included in main's project export.

### 3. High: preserved slider task names do not mean usable slider control

SIG3 contains all six main tasks for each of Volume, Balance and Tinnitus: Current, Up, Down, Set and endpoints. The default Set path now uses `tools/sig3_slider_progress.java` for one absolute accessibility action, shared across all three families. Explicit `legacy-gesture` compatibility remains; the user reports those gestures did not change Signia volume. Treat physical slider functionality as **unresolved**, even though source/target simulations pass.

Required next work: phone-test the implemented native accessibility progress route described in [the Signia analysis](../SIGNIA_REVERSE_ENGINEERING.md), including its touch-exploration/commit gate. Do not spend parity work retuning gesture distance. Acoustic transmission remains owned by Signia unless a separately validated direct acoustic implementation is chosen.

### 4. Medium: interactive program/mode recognition prompt is absent

Main `SIG_Voice_Mode` act0 prompts `What Mode Would You Like?`, consumes `%VOICE`, processes it and writes `%SIG_Mode` / `%SIG_ModeChanged`. SIG3 accepts already supplied speech through `SIG3_AutoVoiceCommand`, `SIG3_WatchCommand` and `SIG3_VoiceRouter`, but provides no equivalent task that starts recognition and asks for a mode.

Main's prompt task only sets state; its dispatcher checks `%SIG_ModeChanged` to initiate program selection. The old router's `program_switch` action is not itself a matching dispatcher branch. Copying the old task alone would not integrate it into SIG3.

Required restoration: a user-callable recognition prompt that resolves an actual configured program name/slot and calls `SIG3_ProgramSwitch`, retaining cancellation/error handling. Keep existing event-driven recognition as another entry point.

### 5. Medium: three-tier environment automation is absent

Main `SIG_Current_dB` act2–7 describes quiet/medium/loud classification, but act1 writes local `%noisePos` while conditions read `%SIG_NoisePos`: the implementation is broken. Main `tasks/sig.tasks.tsk.xml` describes Conversation/Noisy/VeryNoisy targets and phone/watch sample variables, but uses code-6 pseudo-dispatch entries and incomplete Variable Set actions. This is intended functionality, not a reliable implemented controller.

SIG3 `SIG3_InternalNoiseProcess` (`tools/sig3_noise.java`) implements consecutive samples and a middle dead band, with only `%SIG3_NoiseQuietProgram` / `%SIG3_NoiseLoudProgram`. The middle band resets history; it does not select a medium program. Phone samples and explicit numeric input are supported; there is no exported watch-noise event/source adapter or phone/watch source-selection policy.

Required extension: configure three actual program targets and measured threshold behavior if preserving the three-tier design; define source selection if watch noise is needed. Preserve hysteresis/consecutive samples and acoustic playback coordination. Neither old nor new samples are established calibrated sound-pressure dB.

### 6. Medium: old watch/voice mode aliases and override toggle are absent

Main's placeholder state bundle lists `mode conversation`, `mode noisy`, `mode vnoisy`, `sig conversation`, `sig noisy`, `sig vnoisy`, `sig sleep` and `override toggle`. SIG3 program-name matching can cover actual configured names following `mode`/`program`, but does not automatically define these semantic aliases or strip a leading `sig` (adapters strip `sig3`). SIG3 override accepts explicit 1/0 and voice on/off; there is no toggle action.

Required decision in implementation: map preserved semantic aliases to configured actual program slots; add a worker-owned toggle if desired. Sleep event handling exists, but `sig sleep` is not a router command. Do not assume a sleep program mutes or powers off the aids.

### 7. Medium: automatic closure/screen lifecycle and AppBlock were not carried forward

Main project includes the `AppBlock` scene: black background, portrait 855×1920, no interactive elements in the exported scene. Several old tasks close Signia and lock/restore screen state; standalone battery prompt shows/hides the scene. SIG3 includes no scenes, requires an on/unlocked phone, and leaves Signia open. Normal battery checks now close the battery page; optional page-only inspection leaves it open.

These are deliberate current policy differences, but they affect user experience and parity. Restore an explicit configurable completion/navigation policy only after determining the desired behavior. Do not import old blanket close/lock actions or claim automatic secure unlock. AppBlock's exported appearance does not prove it safely coexists with accessibility/acoustic control.

### 8. Medium: event wiring remains outside both project exports

Main project: **23 tasks, 0 profiles, 1 scene**. Current SIG3 project: **68 tasks including internal helpers, 0 profiles, 0 scenes**. Main `xml/profiles.md` describes AutoVoice, AutoWear and recurring noise events but exports no actual profiles; it also references missing main `SIG_NoiseMonitor`. SIG3 supplies real event adapters and NoiseMonitor/SleepState tasks, but importing the project still does not install voice/watch/time/sleep triggers.

Required completion: connect authentic phone event profiles to the SIG3 adapters, with actual plugin variables and timing. This is unfinished setup in SIG3, not a profile export removed from main. Task-count growth is not evidence that event functionality is active.

## Follow-up audit: additional gaps found October 10

### Legacy variables and external callers

Main uses `%SIG_CurrentProgram`, `%SIG_Mode`, `%SIG_ModeChanged` and `%SIG_Level`; SIG3 uses `%SIG3_Program`, family-specific levels and worker results. There is no migration adapter synchronizing those old globals or redirecting external `SIG_` task callers. An old watch shortcut/profile can therefore continue reading stale legacy variables or running a competing task. Audit actual phone callers when importing; route them to SIG3 instead of assuming renamed tasks are drop-in replacements.

### Non-interrupting automation and cancellation

Main `xml/screen_state_and_error_handling.md` proposes `SIG_SafeExecute` and a cancellation prompt before background program changes. No such task exists in main's XML. SIG3 also does not provide cancellation or defer automation while another app is in use; it checks on/unlocked state and can launch Signia. This is a documented design gap, not removed working functionality. Automatic secure unlocking in the old notes is not established.

### Backup helpers and EQ scope

Main `xml/backup.xml` contains `SIG_Chg_Pgm` (opens Program), `SIG_positions` (coordinate click/debug flash) and `SIG_Voice_Mode_Pgm` (recognition plus fixed coordinates). No equivalent diagnostic coordinate task or prompted chooser exists in SIG3. Opening/selecting programs is already covered by ProgramSwitch; prompted recognition remains missing.

Backup `SIG_ApplyEQ` only launches Signia and clicks the point `58.4259%,16.9554%`; it has no EQ value mapping or verification. The state bundle's same-name task is an explicit placeholder. There is no established EQ controller to restore.

### Spoken results

Current program and operation results currently use toast/log feedback. They do not speak the current program, numeric level or completion result. Main has recognition prompts and debug flashes, but this audit found no general spoken-result implementation in its task exports. Spoken response would be a useful addition, not a recovered main feature.

### Coverage decisions already settled

Battery's left/right sequence has been restored from the user-confirmed working task. ProgramCurrent has been added as a fresh read. Volume, Balance and Tinnitus use absolute numeric commands by user choice; missing relative voice commands are not restoration work. No BLE work is required. Save/reset tasks from the `codex` branch are not features of the audited main baseline and should not be labeled missing-from-main.

## Feature coverage matrix

| Main feature | SIG3 status | Work remaining |
|---|---|---|
| Volume Current/Set/Up/Down/Max/Mute | Tasks present | Resolve physical command backend; use absolute numeric voice targets |
| Balance Current/Set/Up/Down/Sharp/Soft | Tasks present | Phone calibration and actual command validation |
| Tinnitus Current/Set/Up/Down/Max/Mute | Tasks present | Availability/calibration and actual command validation |
| Numeric voice volume | Present, stronger parsing | Use absolute target phrases |
| Program selection, slots 1–6 | Present, name-based/readback | Configure actual programs and phone IDs |
| Current displayed program | Added: SIG3_ProgramCurrent and voice query | Confirm phone node/readback |
| Prompted mode recognition | Missing | Add prompt-to-worker entry point |
| Battery audible left/right sequence | Restored from working HeySig sequence | Confirm migrated import/run |
| Prompted battery task | Missing | Restore prompt behavior if used; avoid old coordinates |
| Ambient noise sample | Present | Verify plugin sample units/sign |
| Quiet/medium/loud program selection | Only quiet/loud | Implement configured third tier |
| Phone/watch noise source policy | Missing watch-specific adapter/policy | Implement only against actual event source |
| Sleep/wake program tasks | Present | Supply real state/time profiles; preserve aliases if used |
| Manual override | On/off present | Legacy toggle alias missing |
| Voice/watch adapters | Present | Actual phone profiles still required |
| Initialization | Present, preserves existing values | Migrate useful old settings explicitly |
| AppBlock scene | Missing | Review desired screen/overlay behavior |
| Cleanup/return/screen policy | Changed: Signia stays open | Explicit completion preference and navigation |
| EQ | No SIG3 implementation | State bundle is placeholder; backup only clicks an unexplained point |

## Main defects that must not be restored

- `SIG_BalanceSet` act4/19/23 reads and moves **Volume**; balance functionality must retain SIG3's separate routing.
- `SIG_TinnitusSet` references nonexistent `SIG_TinnitulsUp` and mixed target/state variables.
- Current/Up/Down paths click numeric labels rather than prove a unique read-only current control; some legacy Up/Down Stop actions precede movement.
- Main router derives numeric targets from `%avcommgroup` and uses unanchored regex; program routing is inconsistent with the dispatcher.
- Main `sig.tasks.tsk.xml` has another `SIG_Dispatcher` plus placeholders; importing it can conflict with the real dispatcher.
- Main `xml/Sig_init.tsk.xml` has repeated action identifiers and a nonnumeric task ID; its prose lists settings the XML does not supply.
- Main `SIG_Current_dB` local/global mismatch breaks classification; the thresholds/sign are not independently calibrated.

These are static source findings, not phone tests. See [the existing detailed Tasker review](Tasker-change-review.md) for further main defects and existing SIG3 coordination work.

## Recommended restoration order

1. Preserve the main feature inventory as the scope baseline; keep the source branches and original exports intact.
2. Resolve the non-drag acoustic volume command route before treating SIG3 as a functional replacement.
3. Keep numeric Set as the manual control path for all three families; restore interactive recognition prompts through the existing worker.
4. Confirm the migrated working battery sequence imports and runs.
5. Restore three-tier environment mapping, desired mode aliases and override toggle; wire actual voice/watch/noise/sleep profiles.
6. Define completion/screen behavior and decide whether AppBlock is useful before reproducing the old scene.

The initial review changed documentation only. The subsequent battery restoration updates the generator, helper and generated SIG3 exports; legacy HeySig remains unchanged. Validation consisted of parsing both project inventories and tracing their exported action codes, task calls, router conditions and SIG3 Java bodies. Simulators were not rerun: this review introduces no executable change, and simulation cannot resolve the reported physical gesture failure.

## Complete main XML task inventory

Includes project tasks, standalone tasks, state bundle and backup. Duplicate names are intentionally listed by source.

| Main source | Task | SIG3 disposition |
|---|---|---|
| projects/HeySig.prj.xml | SIG_ProgramSwitch | SIG3_ProgramSwitch |
| projects/HeySig.prj.xml | SIG_BatteryCheck | SIG3_BatteryCheck |
| projects/HeySig.prj.xml | SIG_TinnitusDown | SIG3_TinnitusDown |
| projects/HeySig.prj.xml | SIG_TinnitusMute | SIG3_TinnitusMute |
| projects/HeySig.prj.xml | SIG_VolumeUp | SIG3_VolumeUp |
| projects/HeySig.prj.xml | SIG_VolumeDown | SIG3_VolumeDown |
| projects/HeySig.prj.xml | SIG_VolumeMute | SIG3_VolumeMute |
| projects/HeySig.prj.xml | SIG_VolumeCurrent | SIG3_VolumeCurrent |
| projects/HeySig.prj.xml | SIG_VolumeMax | SIG3_VolumeMax |
| projects/HeySig.prj.xml | SIG_VolumeSet | SIG3_VolumeSet |
| projects/HeySig.prj.xml | SIG_VoiceRouter | SIG3_VoiceRouter |
| projects/HeySig.prj.xml | SIG_TinnitusCurrent | SIG3_TinnitusCurrent |
| projects/HeySig.prj.xml | SIG_TinnitusMax | SIG3_TinnitusMax |
| projects/HeySig.prj.xml | SIG_TinnitusSet | SIG3_TinnitusSet |
| projects/HeySig.prj.xml | SIG_BalanceUp | SIG3_BalanceUp |
| projects/HeySig.prj.xml | SIG_BalanceDown | SIG3_BalanceDown |
| projects/HeySig.prj.xml | SIG_BalanceSoft | SIG3_BalanceSoft |
| projects/HeySig.prj.xml | SIG_BalanceCurrent | SIG3_BalanceCurrent |
| projects/HeySig.prj.xml | SIG_BalanceSharp | SIG3_BalanceSharp |
| projects/HeySig.prj.xml | SIG_BalanceSet | SIG3_BalanceSet |
| projects/HeySig.prj.xml | SIG_TinnitusUp | SIG3_TinnitusUp |
| projects/HeySig.prj.xml | SIG_Voice_Mode | Missing / see prompted-workflow findings |
| projects/HeySig.prj.xml | SIG_Dispatcher | SIG3_Worker + SIG3_VoiceRouter |
| tasks/SIG_BalanceCurrent.tsk.xml | SIG_BalanceCurrent | SIG3_BalanceCurrent |
| tasks/SIG_BalanceDown.tsk.xml | SIG_BalanceDown | SIG3_BalanceDown |
| tasks/SIG_BalanceSet.tsk.xml | SIG_BalanceSet | SIG3_BalanceSet |
| tasks/SIG_BalanceSharp.tsk.xml | SIG_BalanceSharp | SIG3_BalanceSharp |
| tasks/SIG_BalanceSoft.tsk.xml | SIG_BalanceSoft | SIG3_BalanceSoft |
| tasks/SIG_BalanceUp.tsk.xml | SIG_BalanceUp | SIG3_BalanceUp |
| tasks/SIG_BatteryCheck.tsk.xml | SIG_BatteryCheck | SIG3_BatteryCheck |
| tasks/SIG_Current_dB.tsk.xml | SIG_Current_dB | SIG3_CurrentNoise (uncalibrated index) |
| tasks/SIG_Dispatcher.tsk.xml | SIG_Dispatcher | SIG3_Worker + SIG3_VoiceRouter |
| tasks/SIG_ProgramSwitch.tsk.xml | SIG_ProgramSwitch | SIG3_ProgramSwitch |
| tasks/SIG_TinnitusCurrent.tsk.xml | SIG_TinnitusCurrent | SIG3_TinnitusCurrent |
| tasks/SIG_TinnitusDown.tsk.xml | SIG_TinnitusDown | SIG3_TinnitusDown |
| tasks/SIG_TinnitusMax.tsk.xml | SIG_TinnitusMax | SIG3_TinnitusMax |
| tasks/SIG_TinnitusMute.tsk.xml | SIG_TinnitusMute | SIG3_TinnitusMute |
| tasks/SIG_TinnitusSet.tsk.xml | SIG_TinnitusSet | SIG3_TinnitusSet |
| tasks/SIG_TinnitusUp.tsk.xml | SIG_TinnitusUp | SIG3_TinnitusUp |
| tasks/SIG_VoiceRouter.tsk.xml | SIG_VoiceRouter | SIG3_VoiceRouter |
| tasks/SIG_Voice_Battery_Chk_Pgm.tsk.xml | SIG_Voice_Battery_Chk_Pgm | Missing / see prompted-workflow findings |
| tasks/SIG_Voice_Mode.tsk.xml | SIG_Voice_Mode | Missing / see prompted-workflow findings |
| tasks/SIG_VolumeCurrent.tsk.xml | SIG_VolumeCurrent | SIG3_VolumeCurrent |
| tasks/SIG_VolumeDown.tsk.xml | SIG_VolumeDown | SIG3_VolumeDown |
| tasks/SIG_VolumeMax.tsk.xml | SIG_VolumeMax | SIG3_VolumeMax |
| tasks/SIG_VolumeMute.tsk.xml | SIG_VolumeMute | SIG3_VolumeMute |
| tasks/SIG_VolumeSet.tsk.xml | SIG_VolumeSet | SIG3_VolumeSet |
| tasks/SIG_VolumeUp.tsk.xml | SIG_VolumeUp | SIG3_VolumeUp |
| tasks/sig.tasks.tsk.xml | SIG_Dispatcher | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_NoiseEngine | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_SleepEngine | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_WatchCommand | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_VoiceHandler | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_SetMode_Conversation | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_SetMode_Noisy | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_SetMode_VeryNoisy | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_SetMode_Sleep | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_ExitSleep | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_OverrideToggle | State-bundle intent; see noise/sleep/alias findings |
| tasks/sig.tasks.tsk.xml | SIG_ApplyEQ | State-bundle intent; see noise/sleep/alias findings |
| xml/Sig_init.tsk.xml | Sig_init | SIG3_Init |
| xml/backup.xml | SIG_ProgramSwitch | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Current_dB | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_BatteryCheck | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeUp | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeDown | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeMute | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeCurrent | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeMax | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_ApplyEQ | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VolumeSet | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_VoiceRouter | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Chg_Pgm | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Voice_Battery_Chk_Pgm | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_positions | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Voice_Mode_Pgm | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Voice_Mode | Historical duplicate/helper; not a supported import |
| xml/backup.xml | SIG_Dispatcher | Historical duplicate/helper; not a supported import |
