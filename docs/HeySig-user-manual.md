# HeySig user manual

Updated October 6, 2026. Current target: Signia app **2.8.0.18214** on the Android phone.

## What HeySig does

HeySig uses Tasker and AutoInput to operate the Signia app. It can select a configured hearing program, read and change volume, balance, and available tinnitus levels, and save a preferred configuration for restoration after charging.

The current code passes static XML checks and simulated control tests. Execution in Tasker with Signia on the phone has not yet been verified. Follow the first-use checks below before relying on it for daily use.

## Quick start

1. Sync the current repository files from GitHub to the phone using your established Tasker workflow. Pulling files alone does not confirm that Tasker is running the updated definitions; verify the tasks available in Tasker match the revision you pulled.
2. Enable AutoInput accessibility on the phone. Unlock the phone, open Signia, and wait for the hearing aids to connect.
3. Run `SIG_ConfigurePrograms` once. Check the six names below against the app.
4. Test the Current, Up, and Down tasks as described under First-use checks.
5. Select a program through HeySig, set your preferred levels, then run `SIG_SaveSettings` or say **save settings** through the configured AutoVoice profile.
6. After charging and reconnection, run `SIG_Reset` or say **restore settings**.

## Requirements and updating the phone

The phone needs Tasker, AutoInput, and Signia connected to the hearing aids. AutoVoice is needed for the voice-command route and ambient-noise monitoring. Grant microphone access for those features. The current UI selectors use English tab labels, so another app language may require selector changes.

Signia does not run on the user's Chromebook. The Chromebook is the editing and GitHub workspace; the phone is where Signia runtime testing happens. Chromebook checks found Tasker 6.6.20, AutoInput 3.0.12, and AutoVoice 4.0.14. These are observed Chromebook versions, not verified phone requirements or proof of phone compatibility.

Keep the control task families and shared helpers at the same repository revision. The shared tasks are `SIG_AppClose`, `SIG_AppError`, and `SIG_ConfigurePrograms`. Saving/restoring also needs `SIG_SaveSettings`, `SIG_Reset`, ProgramSwitch, and all relevant Current/Set/Up/Down tasks. The matching project definition is `projects/HeySig.prj.xml`.

Back up your working phone configuration before replacing task definitions. After each update, verify the phone uses the changed definitions and repeat the affected device checks.

## Programs and names

HeySig uses stable internal keys and a separate map to the names shown in Signia. The initial order follows the six names supplied by the user; confirm it matches the intended order on the phone.

| Program command | App name | Internal key | Name variable |
| --- | --- | --- | --- |
| program 1 | Normal | normal | `%SIG_Program1` |
| program 2 | Off just tinnitus | tinnitus_only | `%SIG_Program2` |
| program 3 | Noisy | noisy | `%SIG_Program3` |
| program 4 | Outdoor | outdoor | `%SIG_Program4` |
| program 5 | TV | tv | `%SIG_Program5` |
| program 6 | Very Noisy | very_noisy | `%SIG_Program6` |

`SIG_ConfigurePrograms` fills missing names and preserves existing names. If an old configuration already contains names such as Universal, check and update those variables explicitly; running ConfigurePrograms will not overwrite them.

When you rename a program in Signia, update its matching name variable in Tasker to the exact new text. For example, if Noisy becomes Busy Places, set `%SIG_Program3` to `Busy Places`. The internal `noisy` key and saved program preference remain the same. HeySig does not automatically discover renamed or reordered programs.

To select a program without voice, set `%SIG_Mode` to its internal key and run `SIG_ProgramSwitch`. A successful mapped selection establishes `%SIG_ProgramKey`, which SaveSettings requires. Selecting a program manually inside Signia alone does not establish that key for HeySig.

The name Off just tinnitus is a user-defined program label. Its actual hearing-aid behavior depends on how that program is configured.

## Controls and command reference

| Control | Range | Meaning |
| --- | --- | --- |
| Volume | 0–15 | The volume control reached by the configured Signia Volume tab |
| Balance | −8–7 | Sound tone, toward softer or sharper |
| Tinnitus | 0–15 | Tinnitus signal level, when available for the selected program |

Balance and tinnitus are separate controls. These tasks do not have verified support for separate left/right sliders or distinct streaming-volume controls.

The following are examples accepted by the current VoiceRouter. Commands match whole phrases, ignoring case and surrounding spaces. Use short commands without an added wake phrase unless your voice profile removes that phrase first. Numeric commands require digits; spoken-word number conversion depends on the recognizer's output.

| Action | Example commands |
| --- | --- |
| Set volume | `volume 8`, `set volume to 10` |
| Raise/lower volume | `volume up`, `volume down`, `turn it up`, `turn it down` |
| Volume endpoints | `mute`, `volume mute`, `volume max`, `max volume` |
| Set balance | `balance -2`, `set balance to 0` |
| Raise/lower balance | `balance up`, `balance down` |
| Balance endpoints | `balance soft` (−8), `balance sharp` (7) |
| Set tinnitus | `tinnitus 4`, `set tinnitus to 0` |
| Raise/lower tinnitus | `tinnitus up`, `tinnitus down` |
| Tinnitus endpoints | `tinnitus mute` (0), `tinnitus max` (15) |
| Choose program | `program 3`, `mode 3`, `set program to 3` |
| Save preferences | `save settings`, `save my settings` |
| Restore preferences | `reset`, `restore settings`, `restore my settings` |

The current router accepts program numbers, not program names such as “Noisy.” Battery checking has a separate task, `SIG_BatteryCheck`, but no battery phrase in the current main VoiceRouter.

Voice targets outside the listed ranges are rejected. Direct Set tasks clamp integer targets to their supported range and reject nonintegers. “Mute” sets the relevant slider to zero; it is not a power-off command.

For manual Tasker operation, set `%SIG_TargetVolume`, `%SIG_TargetBalance`, or `%SIG_TargetTinnitus`, then run the matching `SIG_VolumeSet`, `SIG_BalanceSet`, or `SIG_TinnitusSet` task. The corresponding Up, Down, and Current tasks do not require a target.

## Voice setup

Create or use an AutoVoice Recognized profile that supplies the command text to `SIG_VoiceRouter`. It accepts Parameter 1 when provided and otherwise reads `%avcomm`; verify that this variable contains the expected whole phrase on your phone.

The repository project currently contains tasks but no embedded profiles that activate voice or charging restoration automatically. Profiles must be configured on the phone. Pixel Watch 3 support uses `SIG_WatchCommand` with AutoWear; follow [AutoWear setup](AutoWear-setup.md) to configure the phone event, watch buttons, and feedback. Installing the plugin alone does not connect the watch to HeySig.

## Saving your preferred configuration

1. Choose a mapped program through HeySig so `%SIG_ProgramKey` is established.
2. Adjust volume, balance, and tinnitus as desired.
3. Run `SIG_SaveSettings` or say **save settings**.
4. Confirm `%SIG_SaveOK` is `1`. If it is `0`, read the error and resolve it before resetting.

Saving reselects/verifies the mapped program, then reads its displayed levels. Check that your preferred values remain visible if switching the program changes them. Volume and balance must both be readable before the saved profile is replaced. Tinnitus is saved only when readable; otherwise tinnitus restoration is disabled. Saving again replaces the one saved profile; HeySig does not currently keep a separate saved profile for each program.

Routine changes to a slider do not automatically overwrite saved preferences. Run SaveSettings again when you want to replace your preferred configuration. Avoid running initialization tasks as a daily reset; use `SIG_Reset` for restoration.

## Restoring after charging

Signia documents that restarting the hearing aids restores their startup settings, including Universal, volume 8, balance 0, and direction Auto. The displayed name of the default program may differ in your configuration. [Signia support](https://www.signia.net/en/support/app/)

After taking the hearing aids out of the charger:

1. Allow the aids to reconnect, unlock the phone, and open Signia.
2. Run `SIG_Reset` or say **restore settings**.
3. Let the operation finish without manually moving the app controls.
4. Check the displayed settings and `%SIG_ResetOK`; `1` means every enabled restoration step succeeded in the task logic.

Reset selects the saved program first, then restores volume, balance, and enabled tinnitus settings. Program selection allows at most three attempts. A failed step stops the routine. Steps already applied remain applied; there is no rollback. Saved preferences remain available for another attempt after the problem is resolved.

This reset restores saved app controls. It does not factory-reset the aids, change their programmed prescription, or restore direction controls. Automatic restoration on charging or Bluetooth reconnection is not yet configured.

## Keeping Signia open

By default, normal completion returns to the phone's home screen. For supported control, save, or reset tasks launched with Perform Task, set Parameter 1 to `keep_open` to leave Signia visible. This parameter is for task execution; speaking “keep open” is not a recognized voice-command option.

## First-use checks on the phone

Start near the middle of a slider's range and test one control at a time.

1. Run Current. Confirm the value matches Signia and the task does not change the slider.
2. Run Up. Confirm exactly one level of increase.
3. Run Down. Confirm it returns to the starting value.
4. Test Set in both directions, then a Set to the already-displayed value.
5. Check program selection against the displayed names, including a renamed mapping.
6. Save a configuration, change the controls, and test Reset.
7. After those work, check endpoints, negative balance, unavailable tinnitus, and restoration after charging.

The gestures retain the assumption that dragging upward increases a value. If a move goes in the wrong direction or skips a level, stop testing that control and record the app behavior for correction.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Unknown command | Use an exact example above; inspect `%avcomm` for extra words or number transcription. |
| Program not found | Correct the matching `%SIG_ProgramN` name; verify spelling, capitalization, and spaces against Signia. |
| Cannot identify a level | Check connection, the selected tab, AutoInput accessibility, and whether a dialog or another numeric control is visible. |
| Plugin action failed | Inspect Tasker's run log and AutoInput error; check accessibility and the installed plugin version. |
| Volume changed by more than one level | The task stops after detecting the mismatch. Inspect the displayed level before retrying. |
| Save says select a program | Select the program through HeySig first to establish a mapped key. |
| Reset says preferences are missing | Complete SaveSettings successfully before using Reset. |
| Reset stops on tinnitus | Confirm the saved program exposes tinnitus. Save again with the intended program/control availability. |
| Settings reset after charging | Reconnect and run Reset; charging restoration is currently manual. |

For a fault report, include the repository revision on the phone, Android/Tasker/AutoInput/Signia versions, task or command used, displayed starting and ending values, and Tasker/AutoInput errors. AutoInput UI Query text and element IDs from the affected screen help verify selectors. Do not include unrelated private information from the screen.

## Status variables and further documentation

| Variable | Meaning |
| --- | --- |
| `%SIG_ProgramOK` | Last program selection/read verification result |
| `%SIG_VolumeOK`, `%SIG_BalanceOK`, `%SIG_TinnitusOK` | Last result for the corresponding control |
| `%SIG_SaveOK`, `%SIG_ResetOK` | Overall save or reset result |
| `%SIG_Level`, `%SIG_BalanceLevel`, `%SIG_TinnitusLevel` | Last observed levels; a value below the control minimum indicates a failed reading |
| `%SIG_PreferredProgram` | Saved stable program key |
| `%SIG_PreferredVolume`, `%SIG_PreferredBalance`, `%SIG_PreferredTinnitus` | Saved levels |
| `%SIG_RestoreTinnitus` | `1` enables saved tinnitus restoration; `0` skips it |

Result variables use `1` for success and `0` for failure. UI verification does not establish that a setting reached the connected hearing aids; compare the app and actual behavior during phone testing.

Ambient-noise monitoring is an optional feature requiring a phone profile and initialization. It can select the configured noisy/normal programs after repeated threshold readings. Leave it inactive during initial manual testing so it does not change programs while you test another task. The supplemental state engine is separate from the main control dispatcher, and its ApplyEQ task remains unfinished.

See [program mapping and reset](program-mapping-reset.md), [control implementation notes](signia-control-refactor.md), [XML validation results](tasker-xml-validation.md), and [device inspection status](android-runtime-validation.md) for technical details.
