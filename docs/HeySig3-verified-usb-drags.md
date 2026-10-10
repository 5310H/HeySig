# Verified Signia slider control

October 10, 2026: Pixel 9a, portrait 1080x2424, Universal program, Signia Volume tab. The user confirmed these moves worked. Displayed values were read immediately before and after each drag.

| Move | Start | End | Duration |
| --- | --- | --- | --- |
| 7 → 8 | 540,1393 | 540,1306 | 650 ms |
| 8 → 9 | 540,1306 | 540,1219 | 650 ms |
| 9 → 0 | 540,1219 | 540,2000 | 1000 ms |

Exact working command form: `adb -s DEVICE_SERIAL shell input swipe START_X START_Y END_X END_Y DURATION_MS`.

Saved replay code: `tools/sig3_verified_usb_drag.py`. Example, only when Signia already displays 8:

```bash
python3 tools/sig3_verified_usb_drag.py --serial PHONE_SERIAL 8 9
```

The script verifies the starting value, slider layout, portrait orientation and screen size, sends one drag, then checks the displayed target. It stops on a mismatch without retries. Only the three tested transitions are supported. These are USB/ADB tests; this does not establish that Tasker's accessibility-dispatched gesture path works. The displayed result and user confirmation are recorded; the app supplies no separate aid-delivery acknowledgement.

Read-only VolumeInspect was also repaired and verified on the phone. Direct view-ID lookup returned zero nodes, but bounded traversal found the exact visible, enabled `com.signia.rta:id/VolumeSlider`. Inspection now reports CommandOK=1, MoveStage=complete and an empty Error. Touch exploration remains off. The inspection export is `tasks/SIG3_InternalVolumeInspect-Updated-2026-10-10.tsk.xml`.

Balance endpoint check on 2026-10-10: the actual `TA-SliderValue` label read `-8` after a drag from the observed zero thumb at (540,1306) to (540,2000). A reverse drag restored the label to `0`. This confirms the displayed lower endpoint is -8, rather than -1 or -7; center zero remains native step 8 of 15. These were ADB pointer drags, not a successful Tasker gesture test.

Tasker verification on 2026-10-10: `SIG3_BalanceUp` successfully moved displayed 0 to 1 with `SIG3_Error` empty and result `Balance: 1; program=Universal; target=1`. Its single 650 ms dispatched gesture used (540,1304) to (540,1217). Signia was on Controls; an earlier test from App settings failed at launch. The Pixel 9a setup now configures the observed Media sound channel only when the Tasker audio-stream setting is unset, and supplies calibrated track endpoints/bounds. Native progress locates the thumb because the numeric label bounds extend down the track.

Additional Tasker phone tests: Balance 1 to 0, Tinnitus 0 to 1, and Tinnitus 1 to 0 all reached the expected app labels. The final tinnitus result was `Tinnitus: 0; program=Universal; target=0`, with an empty error. These tests verify Tasker-dispatched movement and app readback, not acoustic aid receipt.

The TV program exposes Volume and Balance tabs but no Tinnitus tab. A live `SIG3_TinnitusUp` request returned `Tinnitus unavailable for this program` and left the gesture diagnostic empty. Universal was restored afterward. The availability check traverses the visible accessibility tree and requires exactly one enabled Tinnitus Signal Tab (including its selected variant); it does not switch programs or guess availability from a name. Current, up/down, set, endpoints, inspection, and voice paths have simulated coverage for the missing-tab case.

Signia changes the program label resource ID from `com.signia.rta:id/Universal` to `com.signia.rta:id/TV`. The slider program guard now accepts the uniquely visible accessibility header (`Hearing program Universal Active`, `Hearing program TV Active`) when the configured label ID is absent, and rejects disagreement or ambiguity.

Final live read-only checks with the active-header guard: Universal returned `Tinnitus: 0; program=Universal` with an empty error. TV returned `Balance: 0; program=TV` with an empty error despite the configured program label ID remaining Universal. Universal was restored afterward. Balance and tinnitus finished at 0 in Universal.
