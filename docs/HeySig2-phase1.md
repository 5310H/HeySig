# HeySig2: Phase 1 volume proof

HeySig2 is separate from HeySig. The original project and tasks remain the
backup/reference implementation. Phase 1 contains exactly four tasks:

- `SIG2_AppLaunch`: launch `com.signia.rta`, wait, query, and verify foreground package.
- `SIG2_VolumeCurrent`: open Volume Tab, query aligned accessibility data, select the knob, and publish level and coordinates. No volume gesture.
- `SIG2_VolumeUp`: read current state, tap the selected knob coordinates, swipe upward, and verify exactly one level of change.
- `SIG2_VolumeDown`: the corresponding downward operation.

Import `projects/HeySig2.prj.xml` into Tasker 6.6.20, or import the four
`tasks/SIG2_*.tsk.xml` exports individually. The project uses IDs 201–204,
with no profiles, scenes, or references to SIG_ tasks. Individual task imports
do not create the project container; create HeySig2 and move those four tasks
into it if using that route. Reimporting updates existing SIG2_ names, so retain
any phone-side edits before doing so. Keep HeySig installed as the reference.

## Why readback is different

On the real Volume screen, `15` and `0` are fixed endpoint labels, while a
third numeric element holds the current value (for example `7`). Current
therefore iterates indices into `%aitext()`, `%aicoordinates()`, and optionally
`%aiid()`. It accepts a 0–15 value only from the configured knob selector and
publishes that same element's coordinates. It never excludes 0 or 15 by value.
A matching ID or spatial region must identify exactly one numeric element.
Two endpoint labels alone cannot establish current volume.

**The selector requires phone calibration.** The current-value resource ID
confirmed on the phone is `com.signia.rta:id/TA-SliderValue`; a volume-7
capture reports its center as `541,1701`. Set `%SIG2_KnobId` to that exact
ID. Coordinates are read afresh from the aligned query, never hardcoded. There is no fabricated device-specific
coordinate or guessed default. Before calibration Current reports failure and
Up/Down makes no volume gesture. The included mock geometry is test data,
not a claim about Signia's actual layout.

Run Current once on the unlocked phone. It captures `%SIG2_QueryData` before
checking configuration: one line per query index, with `index | text | id |
x,y`. Examine the dump at current values 0, 7, and 15, then across the full
slider travel. Choose one selector:

1. Set `%SIG2_KnobId` to a resource ID shown on the current-value element, if
   that ID stays constant as the value moves and distinguishes it from both
   endpoint labels. The ID is compared exactly. An ID on a nonnumeric parent
   slider is insufficient.
2. If there is no distinct ID, clear `%SIG2_KnobId` and set all four integer
   globals `%SIG2_KnobXMin`, `%SIG2_KnobXMax`, `%SIG2_KnobYMin`, and
   `%SIG2_KnobYMax`. They define an inclusive region for the current-value
   element's center. It must contain the knob center at every level, including
   0 and 15, and exclude the fixed endpoint centers and unrelated numbers.

Use Tasker's Variables tab to set these globals; this phase adds no setup task.
If no stable ID or separating region exists, keep movement disabled and capture
bounds/other accessibility properties for a new selector. Do not widen the
region until ambiguity disappears by accident. Recalibrate after orientation,
resolution, display scaling, or layout changes. Region mode is not automatically
portable across devices. ID mode still requires aligned valid coordinates.

## Results and movement

`%SIG2_Level` is 0–15 on successful readback, otherwise -1.
`%SIG2_VolumeX` and `%SIG2_VolumeY` identify the selected element; they reset
to -1 before each read. `%SIG2_VolumeOK` is 1 for successful readback or a
verified move, otherwise 0. `%SIG2_AppOK` reports launch verification.
`%SIG2_Error` explains failure. Tasks leave Signia open for observation.

Only internal readbacks use parameter 1 `query_only`, which skips launching
and clicking the tab but still checks the foreground package. Normal Current
opens the app and Volume Tab. Up performs one point tap at the selected knob
and one 40 px upward swipe lasting 300 ms, then reads back and requires exactly
one level of increase. The distance comes from observed knob centers: level 7
at 541,1701 and level 8 at 541,1661. An Up from that level 8 sends the tap at
541,1661 and swipe to 541,1621. No tap result coordinates replace the selected
knob center. There are no upward retries or increasingly long swipes. Unchanged
and unexpected levels fail immediately, retaining the observed readback.

Down retains its previous adaptive 8–160 px, at-most-20-attempt implementation;
this Up repair does not establish Down's physical reliability. Up at 15 and
Down at 0 succeed without gestures. Run tasks one at a time.

Up sets `%SIG2_MoveStage` and a pending `%SIG2_Error` before tap, gesture,
and post-gesture readback. `%SIG2_Gesture` records actual start/end coordinates,
direction, distance, and duration. Explicit AutoInput failure messages include
stage, error code, plugin message, and gesture details. An action halt retains
a pending diagnostic. Only verified success clears the error. Current's
`query_only` entry preserves that pending error while its query runs, then
clears it on successful readback; normal Current still resets its error at entry.
The selector, index alignment, and literal ID comparison are unchanged.

## Phone gate before Phase 2

1. Import on Tasker 6.6.20 with HeySig still present. Confirm HeySig2 and all
   four SIG2_ tasks appear, with their complete final actions. Expected counts:
   AppLaunch 19, Current 139, Up 81, Down 76. Confirm no existing SIG_ task is
   replaced. Re-export HeySig2 from the phone and compare action/control-flow
   structure if Tasker reports any import problem.
2. Verify installed AutoInput configuration activities and accessibility
   permission, launch `com.signia.rta`, and confirm query package, Volume Tab
   navigation, index alignment, and valid coordinates. No Signia app exists on
   the available emulator; this step requires the actual phone.
3. Capture indexed dumps at 0, 7, and 15. Configure the selector as above.
   Confirm it chooses the current-value element at all 16 levels, excludes both
   fixed labels, and returns correct coordinates. Current must not change volume.
4. Test Up 7→8 and Down 8→7 while observing Signia. Confirm point taps target
   the knob, never labels, and swipe paths remain on the slider/screen. Check
   duration, direction, and retry distances on the phone. Mock tests do not prove
   physical gesture behavior or plugin interpretation of generated settings.
5. Test Up 0→1, Down 15→14, Up 14→15, and Down 1→0. Then Up at 15 and Down
   at 0 must make no gesture. Readback must remain correct when the knob and an
   endpoint label have identical text.
6. Test missing/invalid selector, non-Signia foreground during query-only
   readback, missing/ambiguous knob, plugin failure, and an unchanged gesture.
   Confirm no gesture after failed selection and a clear failure result. Confirm
   stale levels/coordinates are cleared on failed Current. Verify overshoot
   reports failure and does not continue dragging; use captured logs or a
   controlled test condition rather than deliberately changing hearing settings
   beyond the intended test.
7. Record phone versions, selector configuration, complete query dumps, observed
   transitions, retry count, and Tasker/AutoInput errors. Proceed to Phase 2 only
   after import, all endpoint readbacks, one-step moves, and failure behavior pass.

## Repository validation

`python3 tools/build_heysig2.py` reproducibly generates only the five new XML
files. Task control flow is new; only low-level argument envelopes for Launch
App and AutoInput plugins come from existing exported XML. No old controller
logic is copied. `python3 tests/check_heysig2.py` executes the generated actions
against aligned mock arrays and checks element ordering, nested control flow,
contiguous indices, isolated dependencies, and standalone/project parity. It
tests all 16 levels in both selector modes, duplicate endpoints, reordered
arrays, missing/invalid/ambiguous data, plugin errors, retry exhaustion, and
overshoot. `tests/validate_tasker_xml.py` supplies broader static checks.
Neither checker implements Android Tasker's importer or executes AutoInput.

## Resource-ID matching repair

The captured `7 | com.signia.rta:id/TA-SliderValue | 541,1701` exposed an
operator bug rather than an array-index mismatch. Tasker's simple Matches
operator treats `/` as OR, so comparing the ID with that operator did not
match the complete resource ID. Current now uses Matches Regex (op 4) with
`^\Q%SIG2_KnobId\E$`, quoting the ID literally and anchoring the full match.
See [Tasker's pattern matching rules](https://tasker.joaoapps.com/userguide/en/matching.html).

The same `%sig2_i` index still reads text, ID, and coordinates. Array length
checks, numeric validation, duplicate-selection rejection, and region mode
remain intact. No guessed coordinate is used. The previous simulator treated
simple Matches as equality and missed the slash behavior; it now models
Tasker's simple matching and Java quoted regex patterns. Regression checks
reproduce the old selector failure and verify the captured level 7 and center
541,1701, all array-order permutations, duplicate endpoint values 0 and 15,
and literal/partial-ID rejection. Other levels and endpoint coordinates in the
fixtures are synthetic; the real-device capture establishes level 7 only.

Reimport the updated Current task or HeySig2 project, preserve the configured
KnobId, and run Current on the captured screen. Expect `%SIG2_Level=7`,
`%SIG2_VolumeX=541`, `%SIG2_VolumeY=1701`, and `%SIG2_VolumeOK=1`. Then
repeat real-device Current at 0 and 15 before proceeding to movement tests.
Up/Down continue to consume Current's selected coordinates; their exports
require no action changes.

## Level-8 Up runtime repair

The phone now confirms Current returns 8,541,1661 with VolumeOK=1. The previous
Up returned unchanged level 8, VolumeOK=0, and an empty error. The new Up removes
the escalating swipe loop and records a measured 40 px upward gesture. Generated
AutoInput tap uses `click(point,%SIG2_VolumeX\,%SIG2_VolumeY)`; the escaped comma
keeps x,y together as the point argument. Gesture Type remains Swipe (0), with
`initialPoint="%sig2_x,%sig2_y"` and `endPoint="%sig2_x,%sig2_end_y"`
JSON values, duration 300, variable replacement of
`parameters`, matching plugin activities, and Continue After Error enabled.
Tests now inspect the expanded plugin JSON, rather than inferring motion solely
from Tasker math variables. Correct settings still require phone execution.

Reimport Current (diagnostic reset behavior only) and Up, or the whole HeySig2
project. Retain `%SIG2_KnobId`. At level 8, run Up once. Expected readback: 9,
541,approximately1621 and VolumeOK=1. On failure, copy `%SIG2_Error`,
`%SIG2_MoveStage`, `%SIG2_Gesture`, and AutoInput's error/run log. An unchanged
result must explicitly say unchanged and expected=9. Tap/gesture failures must
identify their stage even if the action halts before its error guard. A failed
post-gesture query must retain its pending diagnostic. The mock confirms generated
coordinates/configuration and error propagation; movement to level 9 still needs
real-device confirmation. No old HeySig project/task was modified.

## AutoInput gesture-format repair after c0cb180

The phone reached MoveStage=gesture with correct start/end coordinates but the
plugin did not complete. Inspection of **AutoInput 3.0.12 (version code 104)**
installed on the available emulator establishes the input syntax:
`OutputProviderSwipe.getGestureDescription` passes each point string to
`OutputProviderGestures.Point(String)`. That constructor splits on a comma,
requires exactly two components, and parses both as coordinates. Invalid points
cause the swipe provider to raise `Points are invalid`. The generated c0cb180
payload instead contained display-summary text such as
`Start X: 541\nStart Y: 1661`, with no comma. It cannot pass this parser.
The human-readable BLURB is separate and must not be used as the point input.

Up now supplies raw comma pairs: initialPoint `541,1661`, endPoint `541,1621`
after Tasker variable substitution. GestureType=0 maps to Swipe in the installed
enum; duration remains 300 ms, timeout 10 seconds, Continue After Error enabled,
JSON_ENCODED_KEYS includes parameters, and VARIABLE_REPLACE_KEYS includes
parameters. The configuration activity remains ActivityConfigGestures and the
plugin type remains IntentGestures. Distance stays **40 px**. Current and Down
exports and the old HeySig project/tasks are unchanged by this repair. Down's
legacy gesture format is outside this Up fix and is not certified by these tests.

Immediately after the tap and gesture actions, before guards/waits/readback,
Up copies the plugin-local native values into persistent globals:

- `%SIG2_TapErr` and `%SIG2_TapErrMsg` for the tap.
- `%SIG2_GestureErr` and `%SIG2_GestureErrMsg` for the swipe.

They reset to `not run` for a new Up request. Before each plugin they become
`not returned (action halted)` so a halt before the capture is distinguishable
from an actual native error. If a plugin returns without supplying an error
variable, Tasker's unresolved `%err`/`%errmsg` strings may appear in the raw
snapshots; they are not invented native errors. Failure messages use the captured
values. Subsequent Current queries cannot erase these separate snapshots.
The pending stage error remains when no plugin result is returned; no code can
capture a native result which AutoInput never delivers.

Reimport Up (81 actions) or HeySig2, keep the working KnobId, and retry once at
level 8. Expect the same 541,1661→541,1621 payload and readback 9 if the plugin
executes successfully. If it still fails, send the MoveStage, Gesture, Error,
GestureErr, GestureErrMsg, TapErr, and TapErrMsg globals plus the AutoInput log.
The captured phone failure did not include a native plugin message, so the parser
mismatch is established but the phone's exact native error remains unobserved.

Inspection provenance: APK SHA-256
`4f33f46c2a8b4ff7b4e7c54a93b0ae63fdfcc09f5b1654b185e2f6d2e4295b05`.
The APK and disassembly stayed in /tmp; no APK or proprietary code is committed.
Regression tests reject display-label point inputs, verify expanded comma-pair
payloads and unchanged distance, check immediate capture placement, and exercise
native failure snapshots and interrupted-action diagnostics. These checks do not
execute gestures against Signia on the emulator.
