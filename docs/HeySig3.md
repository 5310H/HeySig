# HeySig: setup and everyday use

For the configured Pixel phone and Pixel Watch 3 · Updated October 15, 2026

HeySig lets you speak commands to operate Signia on your phone. You can choose a hearing program, change volume, balance or tinnitus level, and request battery checks. The phone must be available to operate Signia even when you speak into the watch.

**Already using HeySig on this phone? Start with Everyday use. You do not need to reinstall it.** For a new installation, follow Set up the phone, then Set up the watch.

[Print this manual (PDF)](HeySig-user-manual.pdf) · [Browser print version](HeySig-user-manual-print.html)

[Printable command sheet](HeySig-voice-cheat-sheet.html) · [Command sheet in text](HeySig-voice-cheat-sheet.md)

## Everyday use

### Get the phone ready

1. Unlock the phone.
2. Open Signia and go to **Controls**, where the program and volume are shown.
3. Keep the phone available while the command runs. If HeySig asks you to turn off Do Not Disturb or raise phone volume, do that before trying again.

Phone sound volume and hearing-aid volume are different controls. **“Volume ten”** changes the hearing-aid setting. A message about **phone media volume** means use the phone's own volume buttons or slider.

### Speak using the phone

1. Open **Tasker**.
2. Select the **HeySig3** project at the bottom, then **TASKS** at the top.
3. Tap **SIG3_VoiceCommand** to open it.
4. Tap the triangular **Play** button.
5. Wait for the microphone. With Voice prompts on, you first hear **“Sig here.”**
6. Say one command, such as **“current program.”** Wait for the result before giving another command.

**How to run a task:** Whenever this guide says “run” a task, use TASKS → the task name → Play. Press Back to return from the task editor. Use the public tasks named here, not tasks containing **Internal**. See [Tasker's guide](https://tasker.joaoapps.com/userguide_summary.html) for its project and task controls.

### Speak using the watch

1. Wake the Pixel Watch 3.
2. Swipe sideways from the clock face to the **HeySig** tile. Its name in the tile picker is **AutoWear Tile 1**.
3. Tap the command button. It is configured as **👂**, with **HeySig** above it.
4. When **“AutoWear Listening…”** or the microphone appears, say one command.
5. Listen for the result from the **phone**. Watch-speaker replies are not configured.

The HeySig control is on a separate tile. Tapping a weather shortcut on the clock face opens weather. If the tile is missing, follow Add the watch tile below.

### First commands to try

| What you want | Say |
|---|---|
| Hear the active program | **current program** |
| Hear the volume | **current volume** |
| Hear the balance | **current balance** |
| Hear the tinnitus level | **current tin** |
| Select Sleep | **set program to Sleep** |
| Return to Universal | **set program to Universal** |
| Set hearing-aid volume | **volume ten** |
| Center the balance | **balance zero** |
| Set tinnitus to 1 | **tin one** |
| Request battery indications | **battery check** |
| End voice capture | **cancel** |

“Tin” means tinnitus. If the hearing program does not provide tinnitus control, HeySig reports that it is unavailable. Battery checks request indications from both aids; listen to the aids. HeySig does not invent a battery percentage.

## Choose programs and levels

Your current program list is:

| Number | Program | Spoken example |
|---|---|---|
| 1 | Universal | **program one** |
| 2 | Sleep | **program two** |
| 3 | Noisy | **program three** |
| 4 | Outdoor | **program four** |
| 5 | TV | **program five** |
| 6 | Very Noisy | **program six** |

You can use a number or say **“set program to”** followed by the exact name. Slot 2 was previously Off just Tinnitus. Its rename to Sleep has already been updated in this phone's HeySig mappings.

**For the Sleep program, say “program two” or “set program to Sleep.”** Saying **“sleep”** alone invokes separate sleep automation, which needs configuration and must be enabled.

| Control | Allowed values | Examples |
|---|---|---|
| Volume | 0–15 | **volume eight**, **mute**, **maximum volume** |
| Balance | −8 to +7; 0 is center | **balance minus three**, **balance zero**, **balance soft**, **balance sharp** |
| Tinnitus | 0–15, when available | **tin three**, **tin mute**, **maximum tinnitus** |

**Mute / maximum volume** set volume to 0 / 15. **Tin mute / maximum tinnitus** set tinnitus to 0 / 15. **Balance soft / balance sharp** select −8 / +7.

Spoken **“volume up/down”** and **“tin up/down”** are not supported. Say the target number instead. Up/Down tasks exist in Tasker, separately from the spoken command list. See [all supported phrases](HeySig3-voice-commands.md) for alternatives.

## Change spoken prompts and results

1. Run **SIG3_VoiceSettings** in Tasker.
2. Set the two choices independently:

| Choice | What it controls |
|---|---|
| **Voice prompts** | The phone's “Sig here” readiness cue and retry instructions |
| **Spoken results** | Command confirmations and failure messages |

3. Tap **Save**. Cancel or Back keeps the previous choices.

Both may be on, both off, or either one on by itself. These settings do not start or stop listening. The watch uses its AutoWear listening screen; a spoken watch setup wizard and the phone's readiness cue are not part of that tile-launch flow.

**Cancel or retry:** Say **“cancel”** in the phone voice prompt to end without a control command. Unsupported speech offers **Try again / Cancel**; Try again opens a fresh microphone prompt. On the watch, reopen the tile's microphone to try again. The phone's retry dialog is not implemented on the watch.

## Save and restore settings

Successful changes through HeySig save automatically. **“Restore settings”** returns to the last saved program and its saved volume, balance and available tinnitus value.

If you adjust settings **directly in Signia**, say **“save settings”** afterward if you want those values to become your restore point. Direct Signia edits are not automatically tracked.

There is one last-saved record, not a library of named presets. Restoration can change both the program and its control levels. If it reports a failure, inspect the phone before retrying; earlier steps may already have completed.

## Set up the phone

This section is for a new installation or recovery after reinstalling. The existing Pixel setup is already configured.

### 1. Install the apps and permissions

You need **Signia**, **Tasker**, and **AutoInput** on the phone. Add **AutoWear** on both devices for watch use. **AutoVoice** is needed for optional continuous Hey Sig listening and phone-noise sampling; the general phone voice task uses Tasker's recognition prompt.

1. Set up Signia with your aids and confirm its own controls work.
2. Open the installed plugins once and complete their requested initial setup.
3. In Android Settings, find **Accessibility**, then installed/downloaded app services. Enable **Tasker** and **AutoInput**. Menu wording varies by Android version.
4. Allow microphone access when the voice app requests it. Allow AutoWear notifications when requested for its watch connection.

The tested phone uses Tasker 6.6.20. This project needs Tasker's **Java Code** action; older Tasker versions without it cannot run these tasks.

### 2. Import HeySig3

1. Download [HeySig3.prj.xml](../projects/HeySig3.prj.xml) to the phone. Keep the **.prj.xml** ending.
2. Open Tasker. Long-press a **project tab at the bottom** → **Import Project**. Choose the file.
3. Select the new **HeySig3** project.
4. Disable old HeySig or SoundWear profiles that also control the aids, so they do not compete.
5. If Tasker shows an **Apply/checkmark** after editing, tap it to apply changes.
6. In TASKS, run **SIG3_Init** to fill missing defaults. Existing settings are preserved.

Keep a Tasker backup before replacing a working configuration. Do not use the old `xml/backup.xml` or `tasks/sig.tasks.tsk.xml` as this installation. Importing the project does not create the separate AutoWear screen/tile automatically.

### 3. Enter the exact program names

Skip this on the configured phone unless you rename or reorder Signia programs. For a new setup, use the actual names and order shown by Signia.

You can enter them through a one-time setup task without editing the control tasks:

1. Tasker → **TASKS** → **+**. Name it **My HeySig setup** and confirm.
2. In the task, tap **+** → **Variables** → **Variable Set**.
3. Enter `%SIG3_ProgramName1` in **Name**, and your first program's exact name in **To**. Press Back to keep the action.
4. Repeat for each actual slot:

| Variable Set: Name | To, for the current phone |
|---|---|
| `%SIG3_ProgramName1` | `Universal` |
| `%SIG3_ProgramName2` | `Sleep` |
| `%SIG3_ProgramName3` | `Noisy` |
| `%SIG3_ProgramName4` | `Outdoor` |
| `%SIG3_ProgramName5` | `TV` |
| `%SIG3_ProgramName6` | `Very Noisy` |

5. Add a Variable Set action for `%SIG3_AudioStream`: use `media` if Signia uses **Media sound**, or `ring` if it uses **Ring sound**.
6. For the tested Pixel setup, add a Variable Set action for `%SIG3_ProgramBackend` with `gesture-tap`. This makes program selection use a tap on the visible program button.
7. Play **My HeySig setup** once. Update its values before rerunning it after a rename.

Leave unused slots unset; optional noise settings currently require six configured names. A rename also affects saved noise, sleep and restore mappings. Stop automation and update those mappings before relying on them. This phone's Sleep rename has already been migrated with saved values preserved.

### 4. Configure sliders for the measured Pixel 9a layout

The supplied calibration belongs to the measured Pixel 9a portrait layout. **A different phone, screen size, font scale or Signia layout needs its own calibration.** Entering program names alone does not configure sliders on another phone.

For the matching measured layout:

1. Download [SIG3_Pixel9aGestureSetup.tsk.xml](../tasks/SIG3_Pixel9aGestureSetup.tsk.xml) and [SIG3_Pixel9aVolumeGestureSetup.tsk.xml](../tasks/SIG3_Pixel9aVolumeGestureSetup.tsk.xml).
2. In Tasker, long-press **TASKS** → **Import Task**. Import each file.
3. Run **SIG3_Pixel9aGestureSetup** for balance/tinnitus.
4. Run **SIG3_Pixel9aVolumeGestureSetup** for volume.
5. Open Signia Controls. First check **“current program”** and **“current volume.”** Then test a small change from a known starting value and confirm the displayed result.

These tasks overwrite the corresponding calibration. Do not rerun them on a changed layout to force a failed slider to work. For a calibration/bounds failure, use Signia manually until the layout is measured again. Calibration details are in the [technical reference](HeySig3-technical-reference.md).

### 5. Verify the phone before adding the watch

Unlock the phone, open Signia Controls, and run **SIG3_VoiceCommand**. Say **“current program”** and check it matches Signia. Repeat with **“current volume.”** If both work, set your speech choices in **SIG3_VoiceSettings** and continue with watch setup.

An ongoing computer or ADB connection is not required for everyday use after setup.

## Set up the watch

AutoWear's voice screen and tile are configured in **AutoWear on the phone**, then added to the Pixel Watch 3.

### 1. Connect AutoWear

1. Install and open **AutoWear** on both devices.
2. On the watch, allow **Display over other apps** and microphone access when requested. Return to AutoWear afterward.
3. In phone AutoWear, tap **Wear Device** and select **Pixel Watch 3**. If it is absent, check the watch's phone connection first.

### 2. Create the microphone screen

Phone AutoWear → **Screens** → **+** → **Voice Screen**. Close introductory help if it appears.

| Field | Enter / select |
|---|---|
| Screen Name | `HeySigVoice` |
| Command to show | Choose **No** to predefined events; enter `heysig_listen` |
| Prompt | `AutoWear Listening...` |
| Choices | Leave empty |
| Command Prefix | `sig3` followed by one space |
| Trigger Events | On |

Tap **Accept/checkmark**. The stored screen is **ScreenHeySigVoice**. A phone “created/shown” message confirms a request was sent; check that the watch actually displays its microphone.

When editing, remove the entire old value before entering its replacement. Reopen the saved item to verify it. Appending text to an old trigger or image path can break it.

### 3. Connect watch commands to Tasker

1. Phone Tasker → **HeySig3** → **PROFILES** → **+** → **Event** → **Plugin** → **AutoWear**.
2. Tap **Edit/pencil** beside Configuration.
3. Enter `sig3` in **Command Filter**.
4. Turn **Case Insensitive** on and leave **Exact** off.
5. Accept, then press Back from Event Edit.
6. Choose the existing **SIG3_WatchCommand** task as the entry task.
7. Leave the profile enabled and apply changes.

Keep one copy of this profile. A troubleshooting filter of `current program` accepts only that phrase; normal use needs `sig3`.

### 4. Create the tile

Phone AutoWear → **Tiles** → **+**. Enter:

| Field | Enter / select |
|---|---|
| Tiles Name | `HeySigTile` |
| Tile To Update | **AutoWear Tile 1** |
| Tile Type | **Buttons** |
| Texts | `👂` — copy this ear symbol |
| Top Label | `HeySig` |
| Buttons → Commands | `heysig_listen` |
| Buttons → Command Prefix | Leave empty |
| Buttons → Button Icons | Leave empty; use the ear text |
| Apply Now | On |

Accept. The stored item is **TilesHeySigTile**. The native ear symbol replaced a file-based image that showed only a circle. Its final appearance still needs confirmation; the tile command flow worked before that appearance change.

### Add the watch tile

1. Show the normal watch face.
2. Swipe sideways through tiles until **Add tile (+)** appears.
3. Choose **AutoWear Tile 1**.
4. Open it, tap its button, and say **“current program.”**

These are AutoWear's [documented tile-addition steps](https://joaoapps.com/AutoApps/Help/Info/com.joaomgcd.autowear/com.joaomgcd.autowear.activity.ActivityConfigTiles.html). Use the tile, not the unused floating-overlay button.

## Optional sleep and wake schedule

You do not need scheduling to choose the Sleep program by voice.

1. Run **SIG3_SleepSettings**.
2. Choose a **sleep program**, such as Sleep, and **wake program**, such as Universal.
3. Choose different sleep/wake times using the 24-hour clock pickers.
4. Tap **Save**. Saving leaves scheduling off.
5. Run **SIG3_SleepEnable** for future events. Run **SIG3_SleepDisable** to stop future events.

With sleep automation enabled, **“sleep”** and **“wake”** request those configured programs. **“Override on”** blocks automatic changes; **“override off”** releases the block without enabling a schedule.

The schedule cannot unlock the phone. Signia and normal audio conditions must be available. Blocked/missed events are not automatically retried. Overnight locked-phone switching is unverified; do not rely on it for an unattended overnight change. No schedule was saved on this phone after the Sleep rename.

## Optional noise-based selection

Leave this off if you only want manual voice commands. It samples the **phone** microphone, not watch noise.

1. Run **SIG3_CurrentNoise** in your intended quiet, normal and loud environments, with the phone in a consistent position.
2. Run **SIG3_NoiseSettings**.
3. Choose **Quiet program**, **Noisy program**, and **Very noisy program**.
4. Enter boundaries based on those samples. Higher, less-negative readings mean more sound on this phone. They are a noise index, not calibrated decibels.
5. Set the remaining fields. This phone's measured choices are examples, not universal defaults:

| Field | Current measured value |
|---|---|
| Quiet/noisy boundary | −54.5 |
| Noisy/very-noisy boundary | −43 |
| Hysteresis margin | 1.5 |
| Consecutive samples | 3 |
| Cooldown seconds | 60 |

6. Check **I checked that louder sound gives a higher noise index** only after comparing samples. Tap **Save**.
7. Run **SIG3_NoiseObserve** first. It proposes choices without switching programs.
8. If the proposals suit you, run **SIG3_NoiseStop**, then **SIG3_NoiseAuto** to allow switching.
9. Run **SIG3_NoiseStop** to stop either mode. The current capture/wait may finish first.

Saving leaves automation off. Manual program choices block noise switching until **“override off.”** Sleep can suppress noise changes. Keep continuous Hey Sig listening off during sampling.

The eight-hour trial crashed in Tasker after about 5 hours 34 minutes. A later 30-minute unplugged run completed, but overnight reliability is unresolved. Noise sampling does not start automatically after reboot; explicitly start the desired mode.

## Optional “Hey Sig” wake phrase

Use the phone task or watch tile as your normal entry point. Background wake recognition has failed in testing.

If the AutoVoice wake profile is configured, run **SIG3_WakeEnable** to listen or **SIG3_WakeDisable** to stop. Say **“Hey Sig,”** wait for the readiness cue and microphone, then speak the command. Do not combine wake phrase and command in one utterance.

Silencing Voice prompts does not stop listening. For a fresh wake-profile installation, follow the separate [wake setup guide](HeySig3-wake-phrase.md). Locked/background recognition is not a dependable entry method.

## Troubleshooting

| What happens | What to do |
|---|---|
| Tapping opens weather | Swipe to **HeySig / AutoWear Tile 1**. Do not tap the weather shortcut on the clock face. |
| No HeySig tile | Use the watch's **Add tile** control and choose **AutoWear Tile 1**. |
| Button shows only a circle | In phone AutoWear, use Texts `👂` and clear Button Icons completely. Apply, then swipe away and back. |
| No watch microphone | Open watch AutoWear; check connection and display-over-apps permission. Verify both voice screen and tile use `heysig_listen`. |
| Speech but no phone reply | Unlock the phone. Check the Tasker AutoWear profile is enabled, filter `sig3`, Exact off. Check **Spoken results** in **SIG3_VoiceSettings**. |
| “Unlock the phone” | Unlock manually, open Signia Controls and retry. |
| Audio/DND instruction | Change the specified **phone** audio setting and retry. HeySig does not change it for you. |
| Tinnitus unavailable | Choose a program that provides tinnitus, or use another control. |
| Command still running | Wait for completion; give one command at a time. |
| Signia is on Programs or battery page | Updated current-program/switch tasks recover to Controls. If recovery fails, return manually and retry. Other settings pages are not automatically navigated. |
| Slider calibration/bounds error | Stop retrying movement. Restore the measured layout or get fresh calibration. Use Signia manually meanwhile. |
| Program mapping changed | Match names to Signia and update saved mappings. Do not overwrite a wanted restore point merely to dismiss the error. |
| Tasker stopped or phone rebooted | Check permissions and try **current program**. Start optional listeners/automation explicitly if wanted. |

When reporting a bug, include **the exact phrase**, **phone or watch**, **the Signia page**, and **the full error**. Keep the failed state available if possible rather than repeatedly sending the command.

## Technical information and verification

The former manual is preserved as the [technical reference](HeySig3-technical-reference.md). For implementation and test records, see the [checklist](HeySig3-test-checklist.md), [page-recovery tests](HeySig3-program-page-recovery-2026-10-15.md), and [reliability record](HeySig3-reliability-2026-10-14.md).
