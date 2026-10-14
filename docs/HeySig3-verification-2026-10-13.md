# October 13 phone verification and handoff

Scope: Signia app readback and Tasker results. Starting configuration was captured from the phone: Universal, volume 10, balance −4, tinnitus 0; all three backends were `legacy-gesture` with direct mode enabled. The six configured program names matched the captured program list. The saved record held the same controls.

## Slider findings

The original direct volume implementation moved 10→0 and repeated 0 without a gesture, but 0→15 failed with unchanged readback. A guarded recovery request also failed; manual ADB recovery restored 10. Testing stopped on failures.

The measured thumb positions differ from the target track positions. Volume thumb centers were approximately Y=748 at 15, Y=1959 at 0, and Y=1152 at 10. Balance and tinnitus independently showed the same endpoint centers. Their captured starting values were restored after the ADB measurements. See [measurement evidence](evidence/HeySig3-thumb-centers-2026-10-13.json).

Separate optional `ThumbTopY`/`ThumbBottomY` settings now position the gesture start from native progress. `TrackTopY`/`TrackBottomY` still position the target. Pixel 9a setup exports retain target endpoints 695/2000 and bounds 501,652,580,2047, and add measured thumb endpoints 748/1959. Partial or invalid thumb calibration is rejected.

A volume-only prototype using a separate activation tap before every changed target passed 20 public Tasker operations: every level 0–15, endpoint repeats without movement, long jumps, and restoration to 10. The caller then ran its original-record restoration action; an independent post-test file read remains to be done. See [prototype evidence](evidence/HeySig3-volume-range-prototype-2026-10-13.json). A later combined-family run stopped at volume 5→6 with unchanged readback; guarded recovery failed, and ADB restored 10. This prototype is not certified as reliable full-range acceptance.

The final implementation submits a 100 ms activation tap, a 500 ms gap, and one continuous 650 ms drag in a single Android gesture request. Its volume diagnostic passed nine guarded operations: 10→5→6→5→6→0→15→0→15→10. Both visible readback and command results passed; volume returned to 10, followed by the original-record restoration action. Its file contents still need an independent post-test read. The final all-family acceptance run did not start: wireless debugging disconnected and USB was not visible to Linux. Full-range and repeated-run acceptance remains unchecked.

## Selectable sleep settings

`SIG3_SleepSettings` was added to source and generated exports. It offers configured program choices and two clock pickers, persists settings together, preserves choices on cancellation, and disables switching when saved or when program mappings change. Preference tests passed. The phone dialog and actual schedule profiles have not been verified or installed as a completed workflow. See [sleep settings](HeySig3-sleep-settings.md).

## Resume here

Repository closeout: all 23 checks passed, including 92 XML files and 6,769 actions with zero static failures. Actual BeanShell checks cover 32 native-progress positions, six thumb-calibration rejection guards, 24 stroke-construction cases, and persistent sleep-setting validation. These do not certify the pending Android dialog, profile delivery, or final full-family movements.

1. Connect the Pixel over USB shared with Linux, or use its current wireless debugging address if authorized. Port 38715 stopped accepting connections. USB discovery showed only root hubs; ADB showed only the Chromebook Android emulator.
2. Export and preserve the current configured phone project before further imports. Phone task IDs differ from repository IDs; updates during this session preserved the installed IDs.
3. Import the final three Set tasks and updated calibration, then rerun all-family targets, endpoints, repeated targets and restoration. The phone contains diagnostic task variants; do not assume it matches the final repository project.
4. Verify the sleep settings dialog and wire/export actual sleep/wake Time profiles. User wants selectable times and programs.
5. Measure phone noise in observation mode before choosing thresholds or enabling automatic changes. User chose the phone source. No noise samples were collected tonight.
6. Continue program failure/no-op cases, profile migration, in-flight interruption/collision, restart, and operation without ADB. Watch events, native accessibility, and background wake remain separate open items.

Temporary baseline and range callers remain on the phone. Their baseline JSON and saved snapshot are preserved under `/sdcard/Tasker`; local diagnostic scripts stayed in `/tmp`. Remove temporary callers after completing verification and preserve the final tested exports. Last successful phone check restored Universal volume 10; balance −4 and tinnitus 0 had also been restored. No reboot or automation enablement was performed.
