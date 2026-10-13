# Direct volume dragging

The opt-in direct mode moves the volume slider to the requested position in one continuous 650 ms stroke, then checks fresh app readback. It shows/speaks the finished result rather than reporting intermediate levels. A wrong final value stops the command without an automatic retry. Existing worker, program, audio and saved-settings guards still apply.

Use the volume `legacy-gesture` backend and set `%SIG3_VolumeDragMode=direct`. Set it to `incremental` to use one-level steps again; an unset mode retains that existing behavior. Balance and tinnitus retain their existing movement. The separate native accessibility backend is unchanged.

Direct mode requires measured `%SIG3_VolumeTrackTopY`, `%SIG3_VolumeTrackBottomY` and `%SIG3_VolumeTrackBounds`. The guard checks current slider bounds before dispatch; the endpoint comes from the target's position along that calibrated track. Calibration belongs to the device/layout, not a program name. No automatic backend fallback is introduced.

Enable **Tasker** in Android Accessibility settings, even when AutoInput is already enabled. Keep Signia Controls foreground and the phone unlocked in portrait. Disconnect external audio outputs and satisfy the existing media-volume/DND checks. These checks run before a stroke is sent.

## October 12, 2026 verification

Local checks cover all 256 direct-volume start/target pairs, one stroke per changed target, unchanged-target no-op and stopping on unexpected readback. Actual BeanShell geometry checks cover all 16 endpoints and eight invalid-coordinate/configuration guards.

The ADB continuous-swipe demonstration moved Universal volume 10 → 7 → 10 with fresh displayed readback; the user confirmed this was the desired faster movement. This demonstration alone does not certify normal Tasker dispatch.

Initial Tasker trials stopped before movement because Tasker accessibility was disabled. After enabling it, audio preflight rejected a connected Bluetooth output; volume remained 10 and restoration reported success. After disconnection, the normal Tasker VolumeSet trial passed 10 → 7 → 10. The user confirmed smooth movement and restoration; Tasker recorded `Volume: 7; program=Universal; target=7` and restore success=1. Direct mode is enabled on the tested phone at the user’s request. Endpoints and other layouts remain separate phone acceptance.

All 20 repository checks passed after the direct-drag changes. XML validation checked 91 files and 6,713 actions with zero failures.
