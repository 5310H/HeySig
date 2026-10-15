# HeySig voice command cheat sheet

Updated October 15, 2026 · Pixel phone + Pixel Watch 3

**Start:** On the watch, open the **HeySig tile** and tap its button. On the phone, run **SIG3_VoiceCommand** in Tasker. Wait for the microphone, then say one command. Replies play through the phone when Spoken results is on.

## Read current settings

| Say | Result |
|---|---|
| **current program** | Selected hearing program |
| **current volume** | Hearing-aid volume |
| **current balance** | Sound balance |
| **current tin** | Tinnitus level, when available |
| **battery check** | Requests both hearing-aid battery indications; listen to the aids |

## Choose a program

| Program | Say |
|---|---|
| Universal | **program one** |
| Sleep | **program two** |
| Noisy | **program three** |
| Outdoor | **program four** |
| TV | **program five** |
| Very Noisy | **program six** |

You can also say **set program to Universal**, **set program to Sleep**, or another exact program name.

**Use “program two” or “set program to Sleep” for the renamed Sleep program.** Saying **sleep** alone invokes separate sleep automation, which needs configuration and must be enabled.

## Change settings

| Say | Range / action |
|---|---|
| **volume ten** | Set volume: **zero–fifteen** |
| **mute** / **maximum volume** | Volume 0 / 15 |
| **balance minus three** | Set balance: **minus eight–seven** |
| **balance zero** | Center balance |
| **balance soft** / **balance sharp** | Balance −8 / 7 |
| **tin one** | Set tinnitus: **zero–fifteen**, when available |
| **tin mute** / **maximum tinnitus** | Tinnitus 0 / 15 |

## Save, restore, cancel

| Say | Action |
|---|---|
| **save settings** | Save the current program and its control values |
| **restore settings** | Restore the last saved settings |
| **cancel** | End the microphone session without a control command |

Successful HeySig changes save automatically. Numbers may be spoken as words. **Volume up/down** and **tin up/down** are not supported; say a target number instead.

## Optional automation

**override on** blocks automatic noise/sleep program changes. **override off** releases that block without enabling automation. **override toggle** switches the block. **noise sample** takes a phone noise sample. **sleep** / **wake** apply configured sleep/wake programs only when sleep automation is enabled.

**Phone ready:** Keep it unlocked, with Signia available and Tasker accessibility enabled. If prompted, turn off Do Not Disturb or raise phone audio volume, then try again. Hearing-aid tinnitus controls depend on the selected program.
