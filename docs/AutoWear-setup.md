# HeySig on Pixel Watch 3 with AutoWear

The watch sends a command to the phone; Tasker and AutoInput operate Signia on the phone. AutoWear transport and Pixel Watch 3 execution have not yet been tested. The phone must be connected to the watch, unlocked, and able to operate Signia with the hearing aids connected. This does not add control while the phone is locked.

## Phone tasks

Sync `SIG_WatchCommand` and the updated `SIG_VoiceRouter` together with their controller dependencies using your GitHub-to-phone workflow. The project definition includes the new task.

WatchCommand accepts Parameter 1, or `%awcomm` from an AutoWear event when Parameter 1 is absent. It accepts either a complete command such as `heysig=:=volume up` or an already-extracted payload such as `volume up`. Other command namespaces and unsupported commands are rejected. VoiceRouter now gives Parameter 1 priority, with `%avcomm` as its existing AutoVoice fallback.

On completion, WatchCommand sets `%SIG_WatchOK` to `1` only if the underlying operation reported success. `%SIG_WatchMessage` contains feedback such as `Completed: volume up` or `Not completed: volume up. Check the phone.` These variables alone do not send anything to the watch; configure the feedback action below.

## Configure AutoWear on the phone and watch

1. Install/configure AutoWear on the phone and watch, select the connected watch in AutoWear, and grant the permissions it requests for command delivery and your chosen watch UI.
2. On the phone, create a Tasker **Event → Plugin → AutoWear → Command** profile for HeySig commands. Configure its filter for the `heysig=:=` namespace. Verify the actual filter/matching options in the installed plugin and ensure other AutoWear commands do not trigger this profile.
3. Link a small phone task with **Perform Task → SIG_WatchCommand**, at the current task priority, and Parameter 1 set to `%awcomm`. The adapter handles both a complete namespaced command and an extracted payload. Inspect `%awcomm` during the first test to verify what your plugin returns.
4. Configure the profile's linked task collision handling to abort a new instance while a previous command is running. Wait for completion before sending another command.
5. After Perform Task returns, add an **AutoWear notification or other feedback action** configured in your installed plugin UI, using title `HeySig` and text `%SIG_WatchMessage`. Target the connected watch. Test this notification separately before relying on it as confirmation.

The repository supplies the phone adapter, not an exported AutoWear event or notification bundle. Configure these plugin-specific entries in the installed AutoWear UI so its own version supplies the correct settings. Successful feedback preparation is not proof of watch delivery.

## Suggested watch buttons

Use AutoWear Tiles or a button screen. For a tile with Command Prefix `heysig`, use payloads in the table below. AutoWear documents that a tile command prefix produces `prefix=:=payload`. Its separate bottom button does not inherit that prefix; give that button a full namespaced command if you use it. [Official AutoWear tile documentation](https://joaoapps.com/AutoApps/Help/Info/com.joaomgcd.autowear/com.joaomgcd.autowear.activity.ActivityConfigTiles.html)

| Button label | Payload | Complete command |
| --- | --- | --- |
| Volume + | volume up | heysig=:=volume up |
| Volume − | volume down | heysig=:=volume down |
| Mute | volume mute | heysig=:=volume mute |
| Normal | program 1 | heysig=:=program 1 |
| Tinnitus only | program 2 | heysig=:=program 2 |
| Noisy | program 3 | heysig=:=program 3 |
| Outdoor | program 4 | heysig=:=program 4 |
| TV | program 5 | heysig=:=program 5 |
| Very Noisy | program 6 | heysig=:=program 6 |
| Restore | restore settings | heysig=:=restore settings |
| Save | save settings | heysig=:=save settings |

Start with Volume +, Volume −, and Restore. Add the other controls after the phone tasks work reliably. Avoid putting Save beside frequently tapped controls if accidental replacement of your preferred profile would be inconvenient.

Watch voice can use the same payloads if your AutoWear voice screen sends the recognized text through this profile. Forward the recognized command as text; a generic watch assistant request does not automatically reach this adapter. Validate buttons before adding voice.

## First test and troubleshooting

1. With the phone unlocked and Signia visible, test delivery of one HeySig command and inspect `%awcomm` before enabling slider execution.
2. Send Volume + from the watch. Verify the phone shows one level of increase, `%SIG_WatchOK` is `1`, and the watch receives the configured feedback.
3. Send Volume − and confirm the starting level returns.
4. Test one mapped program, then Restore after a saved profile exists.
5. Test a disconnected watch and locked phone; neither case should be mistaken for a completed hearing-aid adjustment. Recheck displayed values before retrying a command when feedback was lost.

If the profile never fires, check AutoWear connection, command permissions, namespace, and filter settings. If the profile fires but parsing fails, inspect the actual `%awcomm` text. If the phone operation fails, inspect Tasker's run log, AutoInput accessibility, the phone's lock state, Signia connection, and program-name mappings. If phone execution succeeds but the watch is silent, troubleshoot the separately configured AutoWear feedback action.

The adapter does not queue offline requests, automatically unlock the phone, or guarantee execution of multiple rapid taps. See the [user manual](HeySig-user-manual.md) for controls and reset behavior and the [AutoApps command documentation](https://joaoapps.com/autoapps-command-system/) for the command system.
