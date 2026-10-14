# Direct slider dragging

The opt-in direct mode moves the selected slider to the requested position in one continuous 650 ms stroke, then checks fresh app readback. It shows/speaks the finished result rather than reporting intermediate levels. A wrong final value stops the command without an automatic retry. The October 13 implementation first taps and releases the current thumb for 100 ms, waits 500 ms, then performs the continuous drag in the same Android gesture request. Existing worker, program, audio and saved-settings guards still apply. This revision's short volume diagnostic passed; full-family acceptance remains pending.

Use the family’s `legacy-gesture` backend and select its mode independently: `%SIG3_VolumeDragMode`, `%SIG3_BalanceDragMode`, or `%SIG3_TinnitusDragMode`. Set `direct` for a single stroke or `incremental` for one-level steps; unset modes retain the existing behavior. Tinnitus availability is checked before selecting its tab; a known unavailable program icon prevents any tinnitus tab search or movement. The separate native accessibility backend is unchanged.

Direct mode requires the family’s measured TrackTopY, TrackBottomY and TrackBounds settings, such as `%SIG3_BalanceTrackTopY`. Volume/tinnitus targets are 0–15; balance is −8–7, with zero at step 8. The guard checks current slider bounds before dispatch; the endpoint comes from the target's position along that calibrated track. Calibration belongs to the device/layout, not a program name. No automatic backend fallback is introduced.

Optional paired `ThumbTopY`/`ThumbBottomY` settings separately calibrate the current thumb position from native progress. The measured Pixel setup uses thumb endpoints 748/1959 and retains target endpoints 695/2000. Unset thumb settings retain the prior start calculation; partial or invalid settings stop the command. See the [October 13 findings and handoff](HeySig3-verification-2026-10-13.md) before importing this revision.

Enable **Tasker** in Android Accessibility settings, even when AutoInput is already enabled. Keep Signia Controls foreground and the phone unlocked in portrait. Disconnect external audio outputs and satisfy the existing media-volume/DND checks. These checks run before a stroke is sent.

## October 12, 2026 verification

Local checks cover all 768 direct-slider start/target pairs, one stroke per changed target, unchanged-target no-op and stopping on unexpected readback. Actual BeanShell geometry checks cover all 48 family/target endpoints and 12 invalid-coordinate/configuration guards. Actual stroke-construction checks cover 12 family/mode/start cases, including minimum activation timing and isolation from other sliders.

The ADB continuous-swipe demonstration moved Universal volume 10 → 7 → 10 with fresh displayed readback; the user confirmed this was the desired faster movement. This demonstration alone does not certify normal Tasker dispatch.

Initial Tasker trials stopped before movement because Tasker accessibility was disabled. After enabling it, audio preflight rejected a connected Bluetooth output; volume remained 10 and restoration reported success. After disconnection, the normal Tasker VolumeSet trial passed 10 → 7 → 10. The user confirmed smooth movement and restoration; Tasker recorded `Volume: 7; program=Universal; target=7` and restore success=1. Direct mode is enabled on the tested phone at the user’s request. Endpoints and other layouts remain separate phone acceptance.

All 20 repository checks passed after the direct-drag changes. XML validation checked 91 files and 6,725 actions with zero failures.

Balance passed normal Tasker −4 → −1 → −4 in Universal; direct mode is enabled and the starting level restored. Tinnitus passed 3 → 4 → 3 and 3 → 0, but ordinary direct drags starting at 0 failed. The activation tap and drag in a single Android gesture request then passed normal Tasker 0 → 3 → 0, with CommandOK=1 and fresh readback for both moves. Tinnitus direct mode is enabled and its starting level of 0 restored. Separate tap/drag requests did not complete the command and are not in the final export.
