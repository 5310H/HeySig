# Volume control fix and audit

Signia volume has 16 levels, 0–15. The user confirmed that only the current number is visible and that manual adjustment starts by tapping that number, then dragging up or down.

## Fixed

- Current-level detection uses AutoInput UI Query without tapping candidate numbers. It checks the foreground package and accepts exactly one standalone integer in 0–15. Missing or ambiguous readings leave `%SIG_Level` at -1.
- Up/Down reads fresh state before checking boundaries, taps the displayed number, splits AutoInput's returned `x,y` coordinates, and drags vertically from that position. It no longer estimates a track from screen dimensions or stops before the drag.
- Each move reads the displayed level again. If unchanged, the task retries with a longer drag: 8, 16, …, 160 pixels, with at most 20 attempts. It stops dragging as soon as any change is observed. Only a change of exactly one level counts as success; a skipped level or unchanged control produces an error and preserves the observed level. The procedure detects an overshoot; it does not automatically reverse it.
- Set/Max/Mute use the verified Up/Down path and stop their loops on failure. Set rejects noninteger targets and retains the existing 0–15 clamping.
- Enabled arithmetic for `%steps * -1` in VolumeSet, TinnitusSet, and BalanceSet.
- Corrected the nonexistent SIG_TinnitulsUp reference to SIG_TinnitusUp.
- Standalone task exports and the HeySig project export are synchronized.

## Import and device checks

Back up your current Tasker project. Import `projects/HeySig.prj.xml`, or update all six `tasks/SIG_Volume*.tsk.xml` tasks together. Update the standalone BalanceSet and TinnitusSet tasks too if you import tasks individually.

AutoInput accessibility must be enabled and Signia must be available on an unlocked screen. Start with volume around 7 and test Current, Up (7→8), and Down (8→7). Confirm Current does not change volume. Change volume manually before another test to confirm the task reads fresh state. Then check the endpoints, Set in both directions, Max, and Mute.

The Android device and hearing aids are not connected to this workspace. Runtime plugin compatibility, numeric accessibility text, and physical gesture behavior still need these device checks. The adaptive drag assumes the app exposes the current number as a tappable accessibility text element. It cannot guarantee that a gesture will move exactly one level on every device, but it verifies the result and reports a mismatch.

## Validation

`python3 tests/check_volume.py` parses repository XML and simulates the Tasker actions with a mock Signia control: all 32 Up/Down boundary cases, 256 Set transitions, 32 Max/Mute cases, and unchanged, overshoot, and unreadable failures. This verifies task logic, not Android plugin execution.

## Other audit findings

Balance and tinnitus now use separate level variables, the user-confirmed ranges, and verified slider control flow. See [balance-tinnitus-fix.md](balance-tinnitus-fix.md). Actual Android gesture and accessibility compatibility still require device checks.

For the current import requirements, shared helpers, and additional routing/error changes, see [signia-control-refactor.md](signia-control-refactor.md).
