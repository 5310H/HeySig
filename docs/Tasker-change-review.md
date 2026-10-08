# Tasker changes needed after Signia analysis

Reviewed October 8, 2026, on branch `HeySid3`, based on `main` commit `91cd647`, including the uncommitted HeySig3 numeric-control implementation. This is a static review of repository exports, not a review of the phone's current Tasker configuration. No Tasker XML, Java, or generator code was changed during this review.

## Implementation update — Priority 1 and 2

The SIG3 generator now supplies numeric replacement paths, one collision-controlled worker for all public UI commands, higher-priority child execution, live worker-ownership checks for internal helpers, common-control/program validation on every readback and before gestures, read-only phone audio/screen checks, operation diagnostics, completion toast/log, and explicit read-only calibration tasks with direction. Original SIG exports remain unchanged; the supported import and profile migration are documented in [HeySig3 setup](HeySig3.md). Legacy placeholder/backup bundles are references, not current imports.

Priority 2 has been implemented in code where possible without the phone. **Device acceptance remains outstanding:** verify actual control/program IDs, numeric ranges, balance/tinnitus spacing/direction, import/BeanShell execution, collision behavior under real Tasker scheduling, audible confirmation, hidden-warning cases, and mute boundaries. The read-only calibration helper consumes a measured spacing; it does not invent one. Cleanup explicitly leaves Signia open. Exact configured Signia audio thresholds and all overlay behavior cannot be certified statically. The original review below records the findings that prompted the changes.

## Implementation update — Priority 3

Added serialized SIG3 program selection with exact configured names and displayed-program verification; battery page/read-only text and explicitly configured audible-request paths; non-overwriting initialization; AutoVoice/watch command adapters; noise sampling with explicit sign/scale configuration, dead band and consecutive-sample thresholds; manual override; and configured sleep/wake program selection. Noise/sleep default off. No left/right controls or inferred battery percentages were introduced. All standalone exports match the project.

See [setup and event wiring](HeySig3.md#priority-3-setup). Actual plugin profiles must be connected on the phone; no speculative event Profile bundles were fabricated. Phone confirmation of accessibility IDs, program names, battery request button, noise units/sign, plugin events, and Android execution remains outstanding. Legacy exports and backup scenes stay unchanged. The tables below are the original review findings, not a claim that these implemented migrations are still absent.

## Scope and working assumptions

Reviewed all standalone tasks in `tasks/`, both project exports, the multi-task `sig.tasks.tsk.xml`, `xml/Sig_init.tsk.xml`, `xml/backup.xml`, profile/setup notes, and the new SIG3 generator and continuous gesture implementation. HeySig2 and its Signia analysis document are on `codex`, not in this main-based checkout; their previously established findings provide context, but they are not assumed to be installed.

User-confirmed configuration: Insio CIC; **one common control for both aids, no independent left/right controls**. Volume/tinnitus targets use the reported range 0–15; balance uses −8–7. Tinnitus availability, actual configured maxima, direction, and balance/tinnitus pixel spacing still require phone validation.

Signia findings relevant to the review: a touch must begin on the current thumb; ordinary commands commit when tracking ends; progress changes alone do not establish a command commit; acoustic readback is cached per program; audio guards can block playback while warning presentation is suppressed; the app may skip requests while busy. These are findings from examined build 2.8.0.18214, not a guarantee for every installed version.

## Priority 1 — fix before using the affected paths

| Change needed | Exact evidence | Status / intended approach |
|---|---|---|
| Replace number-click probing with read-only knob selection | `SIG_VolumeCurrent`, `SIG_BalanceCurrent`, `SIG_TinnitusCurrent` loop over numbers, click them, and treat lack of plugin error as a reading. Endpoint labels can match. The Current tasks do not reliably select their tab first. | Implemented in SIG3: aligned UI Query text/ID/coordinate arrays, exact ID or calibrated region, exactly one match, explicit failure status. Validate the selectors on the phone. |
| Remove premature movement termination | Legacy Up/Down tasks place Stop inside the successful candidate-selection branch, before the swipe action. Example: `SIG_VolumeUp` act16 precedes swipe act20. | Replaced in SIG3; keep legacy exports as reference rather than route new commands to them. |
| Use one continuous thumb contact | Legacy movement tasks perform a number click and a separate AutoInput swipe, with guessed track geometry. | Implemented in SIG3: DOWN at queried knob, HOLD 200 ms, MOVE 300 ms, UP at the end through `continueStroke`. Balance/tinnitus compatibility remains a device-test requirement. |
| Stop treating calculated levels as actual readback | Legacy movement tasks assign `%SIG_Level +/- 1` after the swipe without querying the displayed result. | SIG3 verifies every one-stop move and stops on unchanged/overshot/unavailable results. |
| Repair wrong-family BalanceSet wiring | `SIG_BalanceSet` act4 calls `SIG_VolumeCurrent`; act19/23 call volume Down/Up; conditions and arithmetic use volume target/state. | Use `SIG3_BalanceSet` and family-specific state. Do not import the legacy BalanceSet as a replacement. |
| Repair tinnitus target and helper references | `SIG_TinnitusSet` checks `%SIG_TargetVolume` at act11/14/17, computes with `%SIG_TinnitusLevel` although Current writes `%SIG_Level`, and calls nonexistent `SIG_TinnitulsUp` at act29. | Replaced by family-specific SIG3 target/readback. |
| Correct balance endpoints and signed selection | Legacy Balance Up/Down scan 0–15; Sharp tests 15 and computes `15 - %SIG_Level`; BalanceSet writes incompatible limits −5/8. | SIG3 accepts −8–7; Soft/Sharp request −8/7. Confirm actual UI range before device use. |
| Eliminate ambiguous or repeated voice dispatch | Legacy router has unanchored matching, stores AutoVoice group values rather than extracting its own regex result, and does not stop after numeric volume/program branches. Broad `mute`/`max` matches can collide with other features. | SIG3 has anchored, feature-specific numeric routing and stops after a match. Test actual AutoVoice transcription and Parameter 1 passing. |
| Retire placeholder multi-task bundle from active imports | `sig.tasks.tsk.xml` contains a second `SIG_Dispatcher`, incomplete Variable Set arguments, code-6 pseudo-dispatch actions, and placeholder EQ text. IDs 20–31 overlap legacy task IDs. | Mark as design/reference only; provide one supported project import. Do not import it alongside the active project. |

## Priority 2 — harden the new SIG3 execution path

These are **remaining changes**, not features already proven by the numeric simulations.

1. **Serialize all Signia operations across families and entry points.** SIG3 has bounded loops but no project-wide queue or shared execution lock. A volume request can overlap balance/tinnitus, change the active tab, or overwrite shared diagnostics. Define Tasker collision policy and a single dispatcher/worker; release busy state on every failure and timeout. Avoid a lock implemented as an unchecked global boolean that can remain stuck. Acceptance: simultaneous commands never interleave gestures or UI queries, and a failed command does not block later commands.
2. **Make query-only readback prove the expected control is still visible.** Current selects a tab on initial reads; `query_only` trusts the current page. Numeric IDs may be reused across tabs. Confirm expected active tab and common slider identity before post-gesture readback, and reject dialogs/overlays. Do not reopen tabs in a way that changes state during verification.
3. **Add non-mutating audio diagnostics.** Record media/ringtone selection, relevant phone stream volume, route/headset state, and call/DND conditions where Tasker can read them. Surface visible Signia errors. Warning absence must not count as transmission success. Constructor thresholds 50%/90% are not universal calibration values and must not be blindly imposed.
4. **Preserve error context through helper calls.** SIG3 Current may replace pending gesture/readback messages and uses shared `%SIG3_QueryData`. Add operation ID, family, target, program, previous level, expected level, observed level, and touch stage to the final result. Distinguish app-displayed success from aid confirmation.
5. **Bind a target operation to the program it started in.** Acoustic values are cached per program, but SIG3 does not capture or verify the program during its loop. Abort if it changes; obtain fresh family state after any intentional program switch. Do not restore a cached level onto an unverified program.
6. **Finish calibration and runtime range validation.** Provide a setup task or clear configuration checklist for each common slider's ID/region, numeric range, signed labels, direction, and adjacent-stop spacing. Volume starts with measured 40 px; SIG3 requires explicit BalanceStepPx/TinnitusStepPx. A fixed distance need not work across font size, resolution, orientation, or app updates. Tinnitus disabled/unavailable must produce a clear failure.
7. **Gate execution on usable UI state.** Launch and package query do not prove that the display is unlocked, the requested screen has loaded, or an overlay is absent. Check prerequisites, use bounded waits for the actual expected nodes, and fail clearly. Do not assume a no-root task can unlock a secure phone automatically.
8. **Define completion/cleanup policy.** Leave Signia open through gesture completion and fresh readback; then optionally return to the previous app according to the user's preference. Avoid unconditional Back/App Close that can affect the wrong screen. SIG3 currently leaves Signia open.
9. **Expose useful voice feedback.** Report requested target and observed displayed target, or the actual failure. Never say “both aids confirmed” based only on a label. Keep retries explicit; repeating an absolute target is safe at the app-state level but does not prove receipt.
10. **Test zero/mute boundaries separately.** Signia's explicit mute branch sends only 90; explicit unmute sends 91 followed by position. Ordinary 9→10 success does not certify 0→1 or 1→0 behavior. Tinnitus zero is its displayed minimum and must not be described as microphone mute.

## Priority 3 — repair or migrate the other functionality

| Area | Needed change and evidence |
|---|---|
| Dispatcher / voice mode | Legacy `SIG_Dispatcher` routes volume and battery only; Balance/Tinnitus are absent. The router's `program_switch` action has no matching branch; program switching instead depends on `%SIG_ModeChanged`. Reconcile numeric and named program routing with explicit inputs and result flags. `SIG_Voice_Mode` standalone and project copies differ. |
| Program switching | `SIG_ProgramSwitch` uses fixed screen-height fractions and X=540; its click string is `click point(540,%click_y)`, unlike the other plugin action syntax. It immediately assigns `%SIG_CurrentProgram` without readback. Replace with queried program selection, configured actual program names/slots, syntax verified on the installed plugin, and current-program confirmation before declaring success. |
| Battery check | `SIG_BatteryCheck` uses separate Left/Right battery buttons; `SIG_Voice_Battery_Chk_Pgm` uses fixed coordinates. Inspect the actual acoustic battery screen before rebuilding it: both-aids volume coupling does not prove battery UI lacks per-aid buttons. Support the aid's audible battery indication without inventing a machine-readable percentage. |
| Ambient noise | `SIG_Current_dB` writes local `%noisePos` but compares global `%SIG_NoisePos`. Repair the variable mismatch, validate the plugin's units/sign, and do not call the result calibrated dB without evidence. Sampling must not interfere with acoustic playback. |
| Noise/sleep automation | Profile notes reference `SIG_NoiseMonitor`, which is absent from this checkout; the bundled Noise/Sleep engines are placeholders. Leave autonomous changes disabled until concrete tasks, manual override, hysteresis, and serialized routing exist. Do not add EQ/fitting control merely because APK enums exist. |
| Initialization | `xml/Sig_init.tsk.xml` has nonnumeric task ID `Sig_init`, repeated action identifier `act`, and supplies only old SIG globals. Its notes describe additional settings not actually exported. Create a valid SIG3 initialization/calibration export without overwriting user settings on every import. |
| Watch / recognition profiles | Neither project export contains Profile elements. `xml/profiles.md` discusses `%avcommnofilter`, `%avcomm`, `%awmessage`, and `%awcomm`, but these sources are not reconciled by a provided profile. Add one explicit adapter per actual event source, passing normalized text as Parameter 1 to SIG3. Test on installed plugin versions. |
| Backup / scenes / competing imports | `xml/backup.xml` has older duplicate names and additional tasks/scenes. Preserve as backup, document that it is not a current import, and avoid accidental overwrites. The legacy project has one scene; its interaction must be reviewed on-device before retaining it. |
| XML/export consistency | Verify canonical action numbering, explicit condition fields, correct plugin bundles, unique task IDs, complete task references, and standalone/project parity. Current SIG3 checks cover its exports; they do not certify the legacy bundle or Android import. |

## Complete task-family disposition

- **SIG3 AppLaunch; Volume/Balance/Tinnitus Current, Set, Up, Down, endpoint tasks; VoiceRouter (20 tasks):** keep as the numeric-control implementation; complete Priority 2 and phone testing. Endpoint wrappers already use Set, and repeated targets already avoid movement.
- **Legacy Volume Current/Up/Down/Set/Max/Mute; Balance Current/Up/Down/Set/Sharp/Soft; Tinnitus Current/Up/Down/Set/Max/Mute (18 tasks):** reference only; migrate active entry points to SIG3 instead of maintaining two movement engines.
- **Legacy BatteryCheck, Current_dB, ProgramSwitch, Dispatcher, VoiceRouter, Voice_Mode, Voice_Battery_Chk_Pgm:** repair/migrate as described above; do not assume these are covered by the SIG3 slider tests.
- **Multi-task bundle's Dispatcher, NoiseEngine, SleepEngine, WatchCommand, VoiceHandler, SetMode_Conversation/Noisy/VeryNoisy/Sleep, ExitSleep, OverrideToggle, ApplyEQ (12 tasks):** design placeholders or competing definitions; do not activate as current production tasks.
- **Sig_init and backup-only tasks/scenes:** preserve historical files, separate from supported import, and replace initialization with a valid SIG3 export.

## Recommended implementation order and acceptance

1. Keep the original project as backup; designate HeySig3 as the one active slider-control project.
2. Add operation serialization, expected-tab checks, and contextual diagnostics.
3. Calibrate volume first; test Current is read-only, 9→10, repeated 10, 10→9, endpoints, and blocked phone audio conditions.
4. Calibrate balance, then tinnitus if available; test signed targets, repeated targets, unavailable tinnitus, and boundaries.
5. Wire actual voice/watch adapters, then migrate programs and battery. Introduce noise/sleep automation only after manual controls are dependable.

The existing SIG3 simulation checks pass all 768 source/target transitions plus wrapper endpoints, invalid targets, repeated targets, missing calibration, unavailable UI, gesture failure, and overshoot. Its static validator reports 21 XML files / 2,068 actions without failures. Those tests model UI behavior; they do not verify Tasker import, BeanShell execution, phone routing, aid receipt, concurrency, or real screen captures. Each remaining change needs a focused check for its actual risk rather than more repetitions of the same numeric simulation.

Review outcome: **the core numeric workflow is a useful replacement, but the main-based legacy tasks contain definite bugs and the new project still needs execution coordination and device validation.** No direct volume intent, numeric API, or proven accessibility progress-commit shortcut has been established, so retain the continuous thumb gesture and Signia's acoustic command handling.
