# HeySig3 noise-based program selection plan

Created October 10, 2026. Target devices: Pixel 9a phone and Google Pixel Watch 3. This is an implementation plan; automatic switching remains disabled until acceptance testing passes.

## Intended behavior

Measure environmental noise using one selected source, classify sustained noise into Quiet, Noisy, or Very noisy, and select the program assigned to that role. The initial user choices are Universal, Noisy, and Very Noisy. These are setup selections, never names embedded in the decision logic.

Show the measurement source, units, latest level, proposed role, assigned program, and switching status on the phone. Observation mode makes recommendations without changing programs. Manual override pauses automatic changes.

## 1. Capture programs and configure roles

- Read the actual Signia program picker using bounded accessibility-tree traversal. Capture visible program names and order; reject missing, duplicate, or ambiguous entries. Do not infer programs from remembered names.
- Present the captured choices for the user to assign Quiet, Noisy, and Very noisy. Display names in setup; store each role's slot plus the captured name and full picker snapshot.
- Reuse `%SIG3_ProgramName1` through `%SIG3_ProgramName6` and the existing role assignments: `%SIG3_NoiseQuietProgram`, `%SIG3_NoiseMiddleProgram`, and `%SIG3_NoiseLoudProgram`. In the interface, label those roles Quiet, Noisy, and Very noisy respectively.
- Require all three assignments before three-role automation can be enabled. Noise classification returns a role, then resolves its configured slot.
- Validate the picker snapshot before the first automatic switch in a session and before subsequent automatic switches. If names, order, or membership change, pause automation and request refreshed assignments. Never silently adopt a replacement at the same slot.
- Test with renamed and reordered synthetic programs so no logic depends on Universal, Noisy, or Very Noisy appearing in the picker.

## 2. Verify phone measurement first

- Inspect the actual AutoVoice Current Noise output already used by `SIG3_CurrentNoise`: units, sign, sample duration, update rate, and behavior when the microphone is unavailable.
- Collect samples in quiet, conversation, and noisy environments with timestamps and consistent phone placement. Store numeric summaries, not audio recordings.
- Keep an uncalibrated source labeled "noise index". A logarithmic microphone reading alone is not evidence of calibrated environmental dB SPL or dBA.
- If environmental dB is required, select a source with a verified measurement definition and compare it with a reference sound-level meter at several levels. Record device, microphone path, calibration method, weighting, and usable range. A single offset is insufficient if the source is nonlinear or applies changing gain.
- Establish source-specific thresholds from observed measurements. Do not assign arbitrary dB cutoffs before the units are verified.

## 3. Verify Pixel Watch 3 measurement

- Inspect installed watch apps and AutoWear capabilities to establish whether numeric microphone measurements can actually be obtained and delivered. The existing `SIG3_WatchNoise` adapter accepts a supplied number; it does not measure noise itself.
- If no usable capture capability exists, assess a small Wear OS measurement companion that processes microphone samples locally and sends numeric summaries to the phone. Verify microphone permissions, background operation, and battery impact before choosing this route.
- Send source identity, numeric value, units, measurement timestamp, sequence number, and calibration identifier. Validate the real event payload before building the phone wrapper.
- Calibrate the watch independently. Phone and watch readings must not share thresholds unless their measurement scales have been verified as comparable.
- Select exactly one source. Disconnection or stale watch samples pause decisions; switching to phone requires an explicit source choice and resets the observation history.

## 4. Add stable decisions and observation mode

Starting tuning values, subject to phone/watch measurements:

| Setting | Initial proposal |
|---|---|
| Sampling | Short measurement window every 10 seconds |
| Confirmation | Three consecutive valid windows proposing the same new role |
| Minimum time between successful switches | 60 seconds |
| Freshness limit | 30 seconds for the proposed sampling interval |
| Startup | Observation mode; no automatic program change |

- Smooth short peaks using an appropriate summary for the verified source. If computing average sound energy in dB, average in the energy domain before converting back to dB.
- Add separate entering and leaving thresholds at both role boundaries. This is hysteresis; the current code's consecutive-sample counter does not provide it for all three tiers.
- Define direct Quiet-to-Very-noisy and reverse transitions explicitly. Sustained readings may skip the middle role; a brief spike must not trigger a change.
- Reject nonnumeric, nonfinite, stale, duplicate, out-of-order, or incompatible-unit samples. Invalid input clears pending confirmation so separated samples cannot count as consecutive.
- Reset pending history after source/calibration/configuration changes, manual override, sleep suppression, cancellation, or restart. Start collecting fresh samples when resumed.
- Observation mode logs the proposed role and reason, without calling ProgramSwitch. Confirm thresholds and stability on the phone screen before enabling switching.

## 5. Connect verified switching

- Route automatic changes through the existing single SIG3 worker and ProgramSwitch readback checks. Verify the displayed current program before acting; an already selected target needs no switch.
- Preserve foreground deferral by default: if Signia is unavailable or the phone is locked, show a deferred status and wait for fresh measurements when usable. Watch sensing does not remove the phone's Signia UI requirements.
- Preserve read-only audio preflight. DND or insufficient phone volume stops with instructions; the user changes settings. Never adjust phone settings automatically.
- Require a fresh qualifying decision after a blocked or failed attempt. Do not replay an old pending switch or retry continuously while settings remain blocked.
- Start the successful-switch cooldown only after verified readback. Record failures separately and limit repeated attempts/notifications.
- Keep manual override, cancel/resume, and sleep suppression. Give direct manual program selections priority by pausing automation until the user resumes it, so automation cannot immediately undo the choice.

## 6. Acceptance tests and rollout

1. Test role capture/mapping with arbitrary names, reordered slots, missing roles, duplicate labels, and changed picker snapshots.
2. Test decision boundaries, hysteresis, sustained transitions, isolated peaks, cooldown, restart, and history resets with recorded and synthetic samples.
3. Test timestamps, disconnects, duplicate delivery, source changes, microphone denial, and incompatible units.
4. Run phone observation mode in the three real environments; assess proposed choices, lag, and battery cost.
5. Enable phone switching for a controlled screen test of all three roles and return transitions. Test DND, low volume, foreground deferral, failures, manual override, and unchanged targets.
6. Repeat observation and controlled switching with the verified watch source. Confirm app-selected programs separately from audible hearing-aid response.
7. Update the manual, voice-command reference if controls are added, test checklist, and actual exported phone profiles. Commit and publish the implementation only with its measured limitations documented.

## Deliverables and completion criteria

- Program capture and role-assignment setup with snapshot validation.
- Verified phone source; verified watch source or a documented measurement blocker.
- Source-specific units, calibration record where applicable, thresholds, and freshness rules.
- Observation display/log, hysteresis, confirmation, cooldown, and manual priority.
- Tested worker integration with existing audio and program guards.
- Evidence that sustained noise selects the assigned programs without rapid switching, stale commands, or hardcoded names.

First implementation step: build program capture and role assignment, then collect phone samples in observation mode. Existing noise automation remains off throughout these initial steps.
