# HeySig3 verification run — October 10, 2026

This run follows creation of the remaining-work list. Results below distinguish repository simulation from execution on the connected Pixel 9a.

## Repository checks: passed

All eight commands exited successfully:

```text
python3 tests/check_sig3_numeric.py
python3 tests/check_sig3_progress.py
python3 tests/check_sig3_tinnitus_available.py
python3 tests/check_sig3_coordination.py
python3 tests/check_sig3_parity.py
python3 tests/check_sig3_migration.py
python3 tests/validate_heysig3_xml.py
python3 tests/check_heysig3.py
```

Coverage includes 768 numeric transitions, target validation, repeated targets, voice routing, backend isolation/prerequisites, unavailable tinnitus, worker coordination/recovery, program guards, initialization, battery/noise/sleep simulations, migration, prompted workflows and selector regressions. Static validation checked 79 XML files and 4,921 actions with zero failures. These checks do not execute Android/BeanShell, plugin events or acoustic delivery.

## Live phone: ProgramCurrent failed

Ran public SIG3_ProgramCurrent using Tasker's Play button on the connected Pixel 9a. After execution, Signia Controls showed Universal and balance 0. Collected Tasker globals:

```text
SIG3_CommandOK = 0
SIG3_ProgramOK = 0
SIG3_Error = empty/unset
SIG3_Program = empty/unset
SIG3_Result = Failed: %SIG3_Error; family=Program target=%sig3_request3 previous=%SIG3_Previous expected=%SIG3_Expected observed=%SIG3_Observed; program=%SIG3_Program; stage=start
```

The task is not accepted as working. Failure reporting also needs investigation because it provides no concrete error and leaves unresolved variables. Source inspection shows ProgramCurrent still relies on direct view-ID lookup; earlier slider inspections found zero matches through that API and were repaired with tree traversal. This is a candidate cause, not an established diagnosis. The phone's imported task revision was not independently exported and compared with the repository during this check.

## Live phone: TinnitusInspect passed

Ran public SIG3_TinnitusInspect through Tasker's Play button in Universal. Tasker reported CommandOK=1, MoveStage=complete and an empty/unset Error. Diagnostics identified the visible enabled `com.signia.rta:id/TA-TinnitusSlider`, class SeekBar, bounds `(501,652)-(580,2047)`, native minimum 0, maximum approximately 2.1474836E9, and current 0. Touch exploration remained false. No slider movement was requested.

The result string still contained unresolved `%SIG3_Program` and `%sig3_request3` fields after the failed ProgramCurrent run. Inspection success does not certify program reporting, native movement or acoustic delivery.

## Additional read-only checks

The user selected read-only testing and confirmed they were not wearing the aids. No slider or battery command was requested.

| Public task | CommandOK | Stage | Program | Outcome |
|---|---|---|---|---|
| SIG3_VolumeCurrent | 0 | start | empty/unset | Failed; stored Level=0 is not certified as a fresh reading |
| SIG3_BalanceCurrent | 1 | complete | Universal | Passed; BalanceLevel=0, empty/unset Error |
| SIG3_TinnitusCurrent | 1 | complete | Universal | Passed; TinnitusLevel=0, empty/unset Error |

VolumeCurrent's result was `Failed: %SIG3_Error; family=Volume target=%par1 previous=%SIG3_Previous expected=%SIG3_Expected observed=%SIG3_Observed; program=%SIG3_Program; stage=start`, with an empty/unset Error. BalanceCurrent's result was `Balance: 0; program=Universal; target=%par1 (app state; aid receipt unverified)`. TinnitusCurrent's result was `Tinnitus: 0; program=Universal; target=%par1 (app state; aid receipt unverified)`. Unresolved optional target fields remain a reporting issue even in successful read-only results. Balance and tinnitus ended at 0 in Universal; no movement was requested.

### Saved phone export comparison

Read copies of the phone's existing saved exports into `/tmp`; these are not newly exported active Tasker state.

- `/sdcard/Tasker/projects/HeySig3-Updated-20261010.prj.xml` contains 17 actions for InternalProgramCurrent versus 19 in the repository, and 341 Worker actions versus 347. Its older ProgramCurrent launch-error action contains the self-referential `Program launch failed: %SIG3_Error`.
- The separately saved `/sdcard/Tasker/tasks/SIG3_Worker.tsk.xml` has 347 actions and matches the repository's Worker action content after whitespace normalization.
- The saved project also predates the latest TinnitusCurrent changes: 148 actions versus 155 in the repository.

These files demonstrate mixed saved revisions. They do not establish which revisions are currently imported, nor prove the cause of the live failures. Exporting and comparing the actual active tasks remains necessary before a controlled update/retest.

## Correction and live retest

After the user requested continued work, exported the actual active HeySig3 project from Tasker and copied it to `/tmp/HeySig3-active-20261010.prj.xml`. Tasker's XML-to-storage action saved to its default `/sdcard/Tasker/projects/HeySig3.prj.xml` path, replacing that saved export. The other saved project remained separate.

Comparison sorted actions by their numeric `act` index because Tasker exports them in lexical XML order. The active project confirmed an older 17-action ProgramCurrent helper and an old direct-ID-only Java guard in VolumeCurrent. Balance and tinnitus had the repaired tree guard. Tasker also normalizes plugin action codes and XML fields on import/export; raw XML differences alone do not establish behavioral differences.

Updated `tools/sig3_program_current.java` and regenerated the project/task export. ProgramCurrent now traverses the bounded live tree, reads the configured label or unique active-program header, rejects ambiguity/disagreement, enables view-ID reporting, and stores Java errors before rethrowing. Imported this helper and the repository's already-repaired VolumeCurrent helper into the phone. Backend selections and automation settings were not changed.

ProgramCurrent retest passed in Universal: CommandOK=1, ProgramOK=1, MoveStage=complete, Error empty/unset, Program=Universal, and result `Program: Universal; program=Universal; target=%sig3_request3 (app state; aid receipt unverified)`. The optional target token still needs reporting cleanup.

VolumeCurrent retest passed after importing the existing repaired helper: CommandOK=1, MoveStage=complete, Error empty/unset, fresh Level=0, and result `Volume: 0; program=Universal; target=%par1 (app state; aid receipt unverified)`. The initial failed result is retained above as history; it is superseded by this successful retest for the corrected phone tasks.

A temporary read-only harness attempted to record results to a phone file but produced no file. Its recording path was not accepted as evidence. Collected retest outcomes directly from Tasker's filtered variable list instead.

Removed the temporary harness task afterward and exported the corrected active project to `/tmp/HeySig3-active-after-repair-20261010.prj.xml` via Tasker's default phone storage path. Compared Java action bodies in that fresh export: both InternalProgramCurrent and InternalVolumeCurrent match the repository. Confirmed the temporary harness is absent from the active project. Transfer files remain on phone storage for reference.

After regeneration, repository parity, migration, coordination and static XML checks passed; static validation remained 79 XML files and 4,921 actions with zero failures. Live tests establish the successful read paths described here, not every guard failure or acoustic behavior.

## Remaining verification

See [remaining work](HeySig3-remaining-work.md). No new acoustic aid-response confirmation, live recognition/watch event, automation, restart or fresh-import acceptance is established. The balance app movement and repeated-target checks are recorded below. No backend settings were changed and no program switch was requested.

## Phone audio guards and balance repeat

The direct public balance requests passed app readback 0 → 1 → 0; repeating 0 passed with an empty gesture trace. Signia displayed its muted/DND popup after the first movement, so these results do not establish hearing-aid receipt. After the user disabled night/DND mode, Android reported interruption filter ALL and media volume 14/25.

The inspected APK’s `WSA.Foundation.Audio.Droid.Internal.SoundPlayManager` constructor defaults its low-volume threshold to 50%. `IsVolumeTooLow` compares current volume strictly below maximum × threshold/100. `NoNotificationsAreSuppressed` requires interruption filter ALL; silent ringer mode is also blocked. Threshold setters exist, so the default is configurable rather than a guaranteed value for every Signia configuration.

HeySig3 now stops with instructions for DND, silent mode and low nonzero volume, preserving phone settings. A standalone `SIG3_PhoneAudioCheck` reads Android without launching Signia. Local tests execute the actual Java policy for 20 cases including both streams, DND modes, silent/vibrate modes, the 12/25 versus 13/25 boundary and a configured 80% minimum. Live negative guard and hearing-aid acoustic receipt checks remain pending.

Live standalone `SIG3_PhoneAudioCheck` passed: AudioReady=1, Error blank, stream media, volume 14/25, minimum 13/25, ringerMode=2, mode=0, interruptionFilter=1. It read Android audio settings without launching Signia or issuing a hearing-aid command. Flow simulations also confirm preflight failure prevents slider/program/listen operations, battery open stays available, and initialization preserves a configured minimum.

Imported the standalone audio check and updated BalanceSet, VolumeSet, TinnitusSet, ProgramSwitch, BatteryCheck, SetupInit and Worker tasks into the phone. Exported the active project to `/tmp/HeySig3-active-audio-20261010.prj.xml`; all eight tasks match repository Java bodies and action counts. Phone audio settings were not changed. Static validation after generation: 80 XML files, 5,025 actions, zero failures.

## Remaining-work follow-up

The user selected app/software testing without wearing the aids. Live DND guard passed with AudioReady=0, media14/25, ringerMode=0 and interruptionFilter=2; the error explicitly requested disabling DND/bedtime mode. The user then disabled DND and lowered media volume: the live low-volume guard passed with AudioReady=0, volume10/25, required13/25, normal ringerMode=2 and interruptionFilter=1; the error explicitly requested raising the media slider to13/25. Settings were changed manually by the user, who then confirmed restoring them.

The first combined tinnitus/balance acceptance task stopped before its first movement: TinnitusSet1 reported Signia launch did not complete. This is not a passed movement test. Changed the launch helper to reuse Signia when already foreground and changed current guards to preserve the original launch failure. ProgramSwitch now traverses the live tree for current program, opener and exact target text, preserving dynamic names and ambiguity checks. Concrete reporting omits unresolved optional tokens; its actual BeanShell source passed three formatting cases. Battery open now traverses the live tree and can use the phone-captured toolbar description; no battery slider is introduced.

### Battery priority

The user requested battery testing first and accepted screen verification for now. Paused the queued core slider test. Initial public BatteryCheck listen failed with CommandOK0 and a concrete fallback report; its audio diagnostics showed media16/25, required13/25, normal ringer and DND off. This is not a passed battery sequence.

Confirmed `tasks/SIG_BatteryCheck.tsk.xml` reference actions match the local main branch. Captured the current Controls toolbar opener: content description `TA-BatteryToolbarItem`, top-right bounds954,162–1080,288, clickable button. Opening it manually showed one close marker `TA-BluetoothAndBatteryPageCloseIcon`, left/right check descriptions and two `TA-BatteryIcon` nodes inside the page. The old main-branch opener ID therefore does not identify the current toolbar button. Replaced only that opening step with a unique live-tree ID/description check; preserved original left/request/acknowledge/right/request/acknowledge/close plugin actions and waits. Added named battery stages to diagnose interrupted or failed steps. Retest pending.

Battery retest passed and the user confirmed it worked on screen. Final Signia screen was Controls with the battery page closed. Tasker reported CommandOK1, Error blank, MoveStage complete, and Result `Battery: Left and right battery checks requested; battery page closed. Listen for the aid indications.; target=listen (app state; aid receipt unverified)`. Captured battery page text contained Hearing aids status, Left, Right and Tap to check battery level; no battery percentage was inferred. This establishes app sequence acceptance, not audible aid receipt.

### Program-change demonstration

The user requested a visible program change after confirming battery screen behavior. Captured the actual picker into `/tmp/HeySig3-program-picker-20261010.xml`: six unique `TA-ProgramName` labels, one selected row. Generated phone slot setup from that capture, filling unset names while preserving any configured slot values. The program rows and opener icon are reported non-clickable on this phone. Added an explicit `gesture-tap` program backend that taps only current, visible, uniquely matched nodes using their live bounds and waits for dispatch completion; the existing accessibility-click backend remains the default and no automatic fallback is added. This selection is separate from slider backends. A guarded change/20-second-display/restore test was prepared using the captured starting program and first other program. Phone retest pending.

First program demonstration changed Universal to Off just Tinnitus successfully (CommandOK1, Error blank, displayed active header captured) but its temporary harness reused the same XML action element twice, producing a missing action13 and duplicated action26. Tasker omitted the later restore actions. Restored the captured starting program manually and confirmed its active header. Corrected the generator to clone action templates before numbering; a regression test proves shared templates produce independent consecutive actions. Renumbered/reimported the temporary demo.

Corrected Tasker demonstration passed both Universal → Off just Tinnitus and Off just Tinnitus → Universal, with each result logged, CommandOK1, Error blank and final Program Universal. The explicit gesture-tap backend passed with node bounds measured at dispatch; the first selection trace was center640,578 in Rect221,543–1059,614. Program slot names were read from the actual picker and unset slots filled from that capture. No hardcoded program-name guards were added to control code.

### Initial combined slider run

Imported the separate Pixel9aVolumeGestureSetup and ran its explicit measured Volume gesture calibration. Combined slider test established Tasker VolumeSet0 → 1 → 0 with matching app results and completed 650ms strokes at540,2000 →540,1913 and reverse. The variable-list view truncated the longer log before the entire no-op record, so full no-op evidence still needs capture. The combined task stopped at the following BalanceCurrent read; its temporary guard overwrote the global error with Acceptance current read failed. The worker Result is being inspected for the original cause. This is not a passed combined balance/tinnitus test.
