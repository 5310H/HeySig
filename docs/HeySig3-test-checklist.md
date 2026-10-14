# HeySig3 completed work and test checklist

Updated October 14, 2026. Checked phone items below were actually observed on the Pixel 9a; repository checks are listed separately. Unchecked items remain to be tested. See the [user manual](HeySig3.md) and [recorded phone evidence](HeySig3-verified-usb-drags.md). The [October 13 handoff](HeySig3-verification-2026-10-13.md) records new endpoint failures, diagnostic successes, and the remaining acceptance for the revised gesture implementation.

## Completed implementation

- [x] Repair slider inspection when direct ID lookup returns no nodes; traverse the actual accessibility tree using exact IDs.
- [x] Use the actual Balance and Tinnitus tab descriptions.
- [x] Activate slider tabs with a double tap at their live label center (container center fallback) and verify actual selection; support both two- and three-tab layouts.
- [x] Locate calibrated gesture starts from native progress rather than the numeric label's oversized bounds.
- [x] Send one continuous 650 ms Tasker gesture and verify fresh displayed readback.
- [x] Select backends per family, preserving the Volume backend when configuring balance/tinnitus.
- [x] Avoid a second app launch when Up/Down has already read the current level.
- [x] Preserve Java errors and avoid self-referential `%SIG3_Error` failure messages.
- [x] Check for a visible enabled tinnitus tab before selecting it; stop cleanly if unavailable, including inspection and endpoint requests.
- [x] Read the active program header when a configured program label ID is absent; keep ambiguity and program-change guards.
- [x] Save the Pixel 9a setup task, generated exports, verified ADB volume replay code, and phone verification notes.
- [x] Publish the implementation to GitHub on `HeySid3` ([cc3fc3f](https://github.com/5310H/HeySig/commit/cc3fc3f)).

## Passed on the phone

- [x] VolumeInspect: success, empty Error, exact visible enabled VolumeSlider, native range and actions captured; no movement.
- [x] BalanceInspect: success and native center captured at displayed 0.
- [x] Balance bottom label: observed −8, then restored 0. Displayed range is −8–7; native step 8 is center 0.
- [x] ADB volume 7 → 8, 8 → 9, and 9 → 0; user confirmed these moves worked. These are separate from Tasker's Volume backend.
- [x] Tasker balance 0 → 1 → 0 in Universal, with expected app labels and successful result.
- [x] Tasker tinnitus 0 → 1 → 0 in Universal, with expected app labels and successful result.
- [x] Signia audio setting read as Media sound; Tasker configured to match, with an unmuted speaker stream.
- [x] TV inspected: Volume/Balance tabs present, tinnitus tab absent.
- [x] TinnitusUp in TV: `Tinnitus unavailable for this program`, empty gesture diagnostic, no slider gesture.
- [x] Updated TinnitusCurrent in Universal: displayed 0, program Universal, empty Error.
- [x] Public TinnitusInspect in Universal: CommandOK=1, MoveStage=complete, empty Error; exact visible enabled tinnitus slider captured. See the [subsequent verification run](HeySig3-verification-2026-10-10.md) for remaining result-message issues.
- [x] Updated BalanceCurrent in TV: displayed 0, program TV, empty Error despite the configured label ID being Universal.
- [x] Restore Universal after TV testing; balance and tinnitus finished at 0.

Successful app labels do not independently acknowledge acoustic receipt by the aids. Program and slider acceptance uses fresh Signia readback and command results, as agreed with the user; separate aid-response checks are not required. Battery indications already work.

## Passed in repository checks

- [x] Static validation: 92 XML files, 6,769 task actions, zero failures; all 23 repository checks passed on October 13.
- [x] Numeric simulation: 768 source/target transitions, invalid targets, repeated targets, endpoints and readback failures.
- [x] Backend simulation: native prerequisites, accepted-but-unchanged progress, and per-family backend isolation.
- [x] Missing tinnitus simulation: Current, Up, Down, Set, Max, Mute, Inspect, and voice request stop without movement.
- [x] Worker coordination, wrong control/program, calibration, generated-project parity, migration and restored workflows.
- [x] Shared slider-tab selector: 19 BeanShell cases resolve live X/Y centers and exercise activation guards for two- and three-tab layouts, selected-tab no-op, missing/ambiguous tabs, display bounds, Android version, rejected activation and layout/selection changes while settling; 5 cases check actual selection and fail on unchanged, hidden or ambiguous selection and foreground loss. Six additional cases validate icon-first tinnitus availability and unknown-icon fallback; known icons forbid reading tab descriptions. Phone verification is recorded separately.

The spoken-result formatter check executes its actual Java body in local BeanShell; the remaining simulations and static checks do not execute Android or phone plugin events. Run the repository checks with:

```bash
python3 tests/check_sig3_audio.py
python3 tests/check_sig3_reporting.py
python3 tests/check_sig3_numeric.py
python3 tests/check_sig3_progress.py
python3 tests/check_sig3_tinnitus_available.py
python3 tests/check_sig3_slider_tab.py
python3 tests/check_sig3_coordination.py
python3 tests/check_sig3_parity.py
python3 tests/check_sig3_migration.py
python3 tests/check_sig3_generation.py
python3 tests/check_sig3_voice_retry.py
python3 tests/check_sig3_voice_reply.py
python3 tests/validate_heysig3_xml.py
```

## Next phone tests, in order

Use an unlocked phone on Signia Controls. Keep competing legacy profiles disabled. Record starting program/value and restore them after each test. Stop on an error or unexpected readback; do not resend blindly.

1. [x] Public BalanceSet with Parameter 1 `1`, then `0`; repeated `0` returned success with no gesture. App readback passed; hearing-aid receipt remains unverified.
2. [x] Run public TinnitusSet with Parameter 1 `1`, then `0` in Universal; repeat `0` and confirm no additional gesture. All requests passed with fresh readback; the repeated target and final restore sent no gesture/progress action. Starting tinnitus 0 restored; see [direct acceptance](HeySig3-tinnitus-acceptance-2026-10-11.md).
3. [x] Test other small balance targets before endpoint/long-jump tests. Fresh starting balance −3 in Universal; adjacent targets −2, −1, −4, −5, reverse moves, repeated −1/−5/−3 without movement, and restoration to −3 passed. See [small-target acceptance](HeySig3-balance-small-targets-2026-10-11.md). Balance 0 → −1 → 0 already passed with fresh screen readback and speech; see [voice verification](HeySig3-voice-verification-2026-10-11.md).
4. [x] Acceptance clarified by the user: no aid confirmation is available for balance/tinnitus; use fresh app readback. Battery indications already work.
5. [x] In TV, TinnitusCurrent, Set 1, Mute, Max and Inspect returned the same unavailable message with no gesture/progress action or program change. Volume/Balance reads passed before and afterward; all 18 guarded requests passed and Universal's captured values 9/0/0 were restored. Known no-tinnitus icons skip the tinnitus tab search; see [acceptance](HeySig3-tv-unavailable-2026-10-11.md).
6. [x] Off just Tinnitus, Noisy, Outdoor and Very Noisy passed availability/readback. Each has U+E912 and tinnitus available on this phone; all 28 guarded requests, repeated-selection no-ops and starting-value restoration passed. See [program readback](HeySig3-program-readback-2026-10-11.md).
7. [x] Noisy passed Balance 0→−1→0 and Tinnitus 7→6→7, repeated targets without movement, and restoration. Direct VolumeSet 8→7→8 also passed; all 24 guarded requests succeeded. See [movement acceptance](HeySig3-other-program-movement-2026-10-11.md).
8. [ ] Numeric typed AutoVoice `volume 8` routing passed; working SIG3_VoiceCommand recognized spoken `volume 9`, restored the starting value and spoke the result, confirmed by the user. AutoVoice microphone shortcut still opens no prompt, so actual AutoVoice recognition remains unchecked. Previously tested cancellation and unrecognized speech still apply; see [voice verification](HeySig3-voice-verification-2026-10-11.md).
9. [ ] Test the configured AutoWear command event and its actual input variable. No watch is available for this test, as confirmed by the user on October 11.
10. [x] Test a second command while the worker runs, manual Stop before dispatch, and successful recovery afterward. Confirm no stale success or stuck lock.
    Manual Stop during a controlled pause in the actual worker before dispatch and subsequent fresh ProgramCurrent recovery passed on October 11; see [worker Stop verification](HeySig3-worker-stop-verification-2026-10-11.md). Direct worker and public VolumeCurrent collision rejection, unchanged first-operation results, and fresh VolumeCurrent recovery at 9 in Universal also passed; see [collision verification](HeySig3-worker-collision-verification-2026-10-11.md). Interruption/collision during plugin or internal-helper execution remains a separate live test.
11. [ ] Test locked screen, app left on settings, missing control/overlay, program change, muted selected stream and active call failures as appropriate. Opening Controls recovered the observed settings-page launch failure; automatic recovery is not implemented.

## Volume and native accessibility acceptance still pending

- [x] Direct public Tasker VolumeSet passed in Noisy: 8→7→8, repeated targets without movement, and fresh app readback. The configured dispatchGesture backend was used; see [acceptance](HeySig3-other-program-movement-2026-10-11.md).
- [x] Resolve the subsequent public VolumeCurrent failure: the corrected helper passed with a fresh 0 in Universal, CommandOK=1, stage=complete and empty Error. See the [verification report](HeySig3-verification-2026-10-10.md).
- [ ] Confirm native/display mapping at enough levels for each family before setting its RangeConfirmed flag.
- [ ] If intentionally testing native accessibility, verify touch exploration is enabled by the user. It was off in the captured inspection, and the code must stop before sending progress when off.
- [ ] Verify one native adjacent target, repeated target, reverse move and fresh app readback. Do not infer acoustic commit from Android acceptance or a changed label.
- [ ] Test mute/max and full-range targets only after ordinary adjacent moves work for the chosen backend.

See the [acceptance guide](HeySig3-slider-acceptance.md); no automatic backend fallback is used.

## Other workflows: implemented, phone verification pending

- [ ] SIG3 ProgramCurrent and ProgramSwitch, exact configured program names/slots, repeated-current no-op and failure cases. Manual program selection and the slider guard's TV read do not certify these tasks.
  ProgramCurrent initially failed; the repaired helper subsequently passed in Universal. ProgramSwitch passed between configured slots 1 and 2, including spoken changes and restoration on October 11. Other programs, failure and no-op cases remain pending; see the [verification report](HeySig3-verification-2026-10-10.md) and [voice verification](HeySig3-voice-verification-2026-10-11.md).
- [x] SIG3 battery listen sequence: corrected toolbar opener, requests/acknowledgements and close passed with CommandOK1, Error blank, complete stage; user confirmed screen behavior.
- [x] General prompted battery recognition and speech passed; user confirmed battery indications already work.
- [ ] Prompted mode recognition, aliases, empty/cancelled input and override toggle.
- [ ] Phone/watch noise capture, measured units/sign, thresholds, strike count and optional three-tier program selection.
- [ ] Sleep/wake events, foreground deferral, manual override, cancellation/resume and optional Home completion.
- [ ] Fresh project import and Pixel setup after export, plus configuration persistence after Tasker/phone restart.

Leave noise/sleep automation disabled until its configuration and event tests pass. See [event wiring](HeySig3-completion.md).

- [x] Phone audio policy: 20 actual Java cases for both streams, DND, silent/vibrate and configurable low-volume boundaries; no automatic phone-setting changes.
- [x] Live DND and low-volume guards: DND blocked at14/25; media10/25 blocked with instruction to raise to13/25.
Actual hearing-aid receipt is not independently observable for program/slider commands and is not a pending acceptance test.
- [x] Standalone phone audio check live: AudioReady=1, media 14/25, required 13/25, DND off, Error blank; no Signia launch.

- [x] ProgramSwitch with explicit gesture-tap backend: actual picker slots configured, Universal → Off just Tinnitus → Universal passed, CommandOK1, Error blank. Other programs and failure/no-op checks remain pending.
- [x] General phone voice prompt: current-program query and Try again after unrecognized speech passed.
- [x] Spoken current-program result matched the phone screen.
- [x] Spoken program selection and return: Off just Tinnitus → Universal → Off just Tinnitus; user confirmed both selected programs and spoken names, and final active header matched the captured starting program.
- [x] Spoken current-value queries: volume spoke 8; balance and tinnitus matched the screen (subsequent screen reads both 0 in Universal).
- [x] Spoken battery request: user confirmed battery prompts and spoken confirmation worked. User confirmed battery indications already work; battery percentages were not measured.
- [x] Spoken volume change and restoration: 8 → 7 → 8 in Universal; user confirmed both spoken levels, and final screen matched starting state.
- [x] Spoken balance change and restoration: 0 → -1 → 0 in Universal. User clarified using -1, confirmed speech and restoration; screen reads verified both levels.
- [x] Spoken tinnitus change and restoration: 0 → 1 → 0 in Universal; user confirmed both spoken levels, and screen reads verified change and restoration.
- [x] TV spoken volume change and restoration: 8 → 7 → 8; user confirmed both spoken levels and final screen verified TV at 8.
- [x] TV current-tinnitus query: spoken unavailable explanation passed; captured Error=Tinnitus unavailable for this program and CommandOK=0.
- [x] Live Cancel after banana: user confirmed closure without retry or control change; captured CommandOK=0 and Result=no command sent.
- [x] Live physical Back dismissal after banana: user confirmed immediate closure without reopening recognition or changing controls.
- [x] Live retry-dialog timeout: user confirmed automatic closure after leaving the dialog untouched, with no retry or control change.
- [x] Microphone-prompt Back cancellation ends quietly without retry, speech, or a control change. Empty recognition from silence/timeout also ends quietly.
- [x] Spoken DND block: check battery stopped and user heard instructions to turn DND off; phone zen_mode was 1.
- [x] Spoken low-phone-volume block: media 6/25, DND off; user confirmed check battery stopped and volume instruction was audible.
- [ ] Other blocked-command messages and TTS failure behavior.

- [x] Located Tasker Stop: running task shows a square at bottom-left in place of Play. User confirmed return to triangle; subsequent current-program display/speech passed. Wait-only test does not establish worker interruption.
- [x] Controlled Stop of the actual worker before dispatch: Stop at 7.77 seconds during a two-minute diagnostic Wait, square changed to triangle, worker absent afterward, authoritative result remained pending with CommandOK=0, and fresh ProgramCurrent recovery returned Universal with success. Original phone worker restored; see [verification](HeySig3-worker-stop-verification-2026-10-11.md).
- [x] Busy-worker rejection before dispatch: direct worker and public VolumeCurrent requests showed Tasker's Abort New Task warning, preserved the running worker's operation ID and captured result fields, and subsequent fresh VolumeCurrent recovery returned 9 in Universal with success and matching screen readback. See [collision verification](HeySig3-worker-collision-verification-2026-10-11.md).
- [ ] Verify collision/interruption during an in-flight plugin action or nested internal helper; the controlled pre-dispatch tests do not certify those paths.

- [x] Muted media write guard: user-muted 0/25 blocked public VolumeSet 9→8 at audio preflight, with no touch/progress dispatch and unchanged Universal value 9. Read-only Current remained usable. Captured media 17/25 was restored; see [guard verification](HeySig3-muted-stream-2026-10-11.md).

## October 12 voice additions

- [x] Independent Spoken results and Voice prompts controls: all four combinations saved/reopened; Cancel and Back preserved choices.
- [x] Voice prompts off, spoken results on: no readiness cue, microphone capture and spoken current-program reply accepted.
- [x] Spoken “cancel” closes the general voice session cleanly without an unrecognized reply or Try again.
- [x] “Current tin” shorthand recognized; current program correctly reported tinnitus unavailable.
- [x] Two Tasker application restarts preserved mixed speech-control choices; original on/on choices restored. Full phone reboot remains untested.
- [x] Two consecutive tone-free wake/cue/reply commands, verified regex-on/exact-off profile, locked spoken guidance and manual-unlock recovery, and media restoration to 22/25 after stopping listening. Long-duration endurance remains untested.

Additional executable checks: `check_sig3_voice_preferences.py`, `check_sig3_voice_ready.py`, `check_sig3_voice_retry.py`, `check_sig3_wake.py`, `check_sig3_wake_audio.py`, `check_sig3_settings_snapshot.py`, and `check_sig3_settings_flow.py`. These do not substitute for unfinished phone acceptance. See [voice settings](HeySig3-voice-settings.md) and [wake status](HeySig3-wake-phrase.md).

October 12 closeout: all 19 repository checks passed after the readiness and wake-profile corrections.

Background observation: after returning to Home, AutoVoice Continuous remained a foreground service for more than two minutes. The user reported the subsequent background wake command did not work. Background wake acceptance failed. Full phone reboot and long-duration battery/endurance checks remain untested.

## October 12 direct-volume trial

- [x] Actual BeanShell geometry: all 16 target endpoints and eight rejection guards.
- [x] All 256 direct start/target pairs in simulation, one stroke per changed target and stop after failed readback.
- [x] Normal Tasker VolumeSet 10 → 7 → 10 in the captured program Universal: user confirmed smooth movement and restoration; Tasker result and restore-success flag agreed.
- [x] Tasker accessibility enabled and Bluetooth audio disconnected to satisfy existing guards.
- [x] Direct-drag endpoints and representative long jumps passed for all three families on October 14; other layouts and endurance remain uncertified. See [focused acceptance](HeySig3-slider-acceptance-2026-10-14.md).

See [direct-volume setup and verification](HeySig3-direct-volume.md). All 20 repository checks passed; static validation checked 91 XML files and 6,725 actions.

October 12 direct-slider extension: normal Tasker BalanceSet passed Universal −4 → −1 → −4 with fresh final readback. TinnitusSet passed 0 → 3 → 0 after combining a brief minimum-thumb activation tap and continuous drag in one Android gesture request. Both moves recorded CommandOK=1 and fresh expected readback. Balance and tinnitus direct modes remain enabled, with starting levels restored. Tinnitus interior 3 → 4 → 3 and downward 3 → 0 also passed. Broader endpoints and other layouts remain untested.

## October 14 slider closeout

- [x] Final helpers imported and verified against the cleaned phone export.
- [x] 28 focused public commands passed: representative changes, known failing transitions, both endpoints, and six repeated-target no-ops.
- [x] Starting Universal/10/−4/0 restored; original saved record independently verified byte-for-byte.
- [x] Nine temporary slider callers removed; cleaned tested project exported on the phone and preserved locally.

Slider acceptance is complete for the configured Pixel 9a gesture backend and occasional-use scope selected by the user. Exhaustive phone transitions, endurance, other layouts, and native accessibility remain uncertified. See [exact evidence](HeySig3-slider-acceptance-2026-10-14.md).

## October 14 selectable sleep closeout

- [x] Program selectors, 24-hour clock edit, Save/reopen persistence and Cancel passed on Pixel 9a.
- [x] Native clock events selected Noisy for sleep and Universal for wake with verified worker results and visible app state.
- [x] Foreground blocking preserves its reason in the failed command result.
- [x] Starting Universal/10/−4/0 and exact saved record restored; test choices cleared; automation off.

Sleep acceptance covers an unlocked phone with Signia open and existing audio requirements satisfied. Overnight/endurance, restart recovery, locked-phone switching, and external sleep providers remain unverified. See [sleep evidence](HeySig3-sleep-acceptance-2026-10-14.md).
