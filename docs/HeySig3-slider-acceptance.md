# HeySig3 slider phone acceptance

Updated October 10, 2026. The measured Pixel 9a balance/tinnitus setup uses an explicitly selected Tasker gesture backend. The project-wide default remains native accessibility. [Completed and remaining tests](HeySig3-test-checklist.md) are the status record; [phone notes](HeySig3-verified-usb-drags.md) contain evidence.

## Verified gesture setup

Balance and tinnitus passed Tasker **0 → 1 → 0** in Universal. The path sends one continuous 650 ms gesture, waits for Android completion, and verifies fresh displayed readback after each step. Gesture coordinates come from native progress and measured track endpoints, rather than the label bounds. The calibrated bounds check stops if the layout changes.

The phone uses `SIG3_Pixel9aGestureSetup`, supplied as a [separate task](../tasks/SIG3_Pixel9aGestureSetup.tsk.xml). It sets `%SIG3_BalanceBackend` and `%SIG3_TinnitusBackend` to `legacy-gesture`, with the verified readback ID, StepPx=87, Direction=1, track Y endpoints 695/2000 and bounds `[501,652][580,2047]`. Use only for the measured portrait 1080×2424 Pixel 9a layout. It fills an unset audio stream with `media`, matching Signia's observed Media sound choice; it does not change Volume's backend or an existing stream setting.

## Next adjacent target checks

1. Open Signia Controls on an unlocked phone with Tasker accessibility enabled and no competing old slider profiles.
2. Record the current program and value. Use public BalanceSet or TinnitusSet with a small numbered target, then restore the start value.
3. Repeat the same target and confirm no new gesture. Check `%SIG3_CommandOK`, `%SIG3_Error`, `%SIG3_Result` and `%SIG3_Gesture`.
4. Verify actual aid response separately from the app label. Stop on unexpected readback or an error; do not retry blindly.

Balance displays −8–7, with native step 8 displaying 0. Tinnitus displays 0–15 when available. Start with the [ordered checklist](HeySig3-test-checklist.md#next-phone-tests-in-order) before long jumps or endpoints.

## Programs without tinnitus

Current and inspection check the visible enabled Tinnitus Signal Tab (including its selected variant) before selecting it. Missing tabs stop with **Tinnitus unavailable for this program**. Set, Up/Down and endpoints obtain current state through that checked path. The control guard also rejects a missing tinnitus control during readback.

TV's missing tab was verified on the phone: TinnitusUp stopped with the unavailable message and an empty gesture diagnostic. No automatic switch to a different program is made. Other entry points have simulated missing-tab coverage; their TV phone checks remain on the checklist. Check the actual UI in each program instead of assuming availability from its name.

## Read-only inspection

Run VolumeInspect, BalanceInspect or TinnitusInspect through the public SIG3 tasks. Inspection selects the available family tab and records `%SIG3_SliderDiagnostics`, `%SIG3_QueryData` and `%SIG3_Result`; it sends no progress action. VolumeInspect and BalanceInspect passed on the phone. TinnitusInspect in an available program still needs an explicit live check.

Diagnostics include node ID/class/bounds, actions, RangeInfo min/max/current and touch-exploration state. Set-progress action ID is 16908349. Direct ID lookup failed on this phone, so inspection uses bounded tree traversal to find the exact visible enabled slider.

## Native accessibility backend: separate unverified path

The general `accessibility` backend requests one absolute `ACTION_SET_PROGRESS`, waits 500 ms, and verifies fresh displayed readback. It does not fall back to gestures. Family-specific backends override the general setting, so changing `%SIG3_SliderBackend` alone does not override the Pixel setup's balance/tinnitus choices.

Before using native Set, confirm the displayed/native mapping for that family and only then set its `%SIG3_VolumeRangeConfirmed`, `%SIG3_BalanceRangeConfirmed` or `%SIG3_TinnitusRangeConfirmed` flag to 1. The native maximum can be 2147483647. Volume/tinnitus targets map 0–15; balance maps −8–7. Inspection alone does not certify that mapping.

Native Set also requires touch exploration. Captured inspection reported it **off**, so the code blocks that path before sending an action. Ordinary Tasker accessibility does not satisfy this gate. Any intentional TalkBack comparison changes phone interaction and must be separately chosen by the user; the code does not enable it.

When prerequisites are intentionally satisfied, test one adjacent target and record `%SIG3_ProgressAccepted`, `%SIG3_Observed`, `%SIG3_CommandOK`, `%SIG3_Error` and the native diagnostics. Repeat the target, reverse the move and check aid response. Android acceptance or a changed label alone does not prove acoustic commit. An unchanged/mismatched readback fails without retry.

## Distinguish the volume evidence

ADB pointer drags 7 → 8, 8 → 9 and 9 → 0 were user-confirmed. Their guarded replay script is [sig3_verified_usb_drag.py](../tools/sig3_verified_usb_drag.py). These tests do not establish Tasker's Volume Set backend. Tasker balance/tinnitus gestures run on the phone without an ongoing ADB connection, root, BLE or a helper app; ADB was used during inspection/import/testing only.

Repository simulations and static XML checks pass; their scope and pending phone checks are listed in the [checklist](HeySig3-test-checklist.md).
