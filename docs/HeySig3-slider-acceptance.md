wha# HeySig3 numeric slider phone acceptance

October 9, 2026. The new default Set path uses one `ACTION_SET_PROGRESS` for Volume, Balance and Tinnitus. Acoustic communication remains inside Signia. No BLE, root, ADB or helper app is used.

## First: inspect volume without changing it

1. Import the updated `projects/HeySig3.prj.xml`, preserving phone-side settings. Enable Tasker accessibility and use an unlocked phone.
2. Keep the existing readback selector `%SIG3_KnobId=com.signia.rta:id/TA-SliderValue`. Common control and program IDs must match your actual UI; the defaults remain APK-derived.
3. Clear `%SIG3_SliderBackend` or set it to `accessibility`. `legacy-gesture` is an explicit compatibility option only; it is never an automatic fallback.
4. Run `SIG3_VolumeInspect`. This opens/reads the volume screen but sends no progress action. Record `%SIG3_SliderDiagnostics`, `%SIG3_QueryData` and `%SIG3_Result`.

The diagnostics include the actual node ID/class/bounds, action IDs, RangeInfo min/max/current and touch-exploration state. Expected set-progress action ID is 16908349. Do not confuse the numeric label with the actual slider node.

## Then: one adjacent numeric target

The APK accessibility commit branch requires touch exploration. If diagnostics report false, Set stops without sending an action. Enabling ordinary Tasker accessibility alone does not satisfy this. A user-enabled TalkBack comparison can test the branch, but it changes phone interaction; this implementation does not enable it or alter accessibility settings.

Before setting `%SIG3_VolumeRangeConfirmed=1`, confirm the displayed endpoints are 0 and 15 and that the actual slider uses an ascending linear native domain between its RangeInfo endpoints. Check native current versus displayed current at several manually selected levels. The code maps displayed target to that native range; native max can be 2147483647. Missing confirmation prevents transmission. Inspection does not automatically certify the mapping.

At displayed level 9, run `SIG3_VolumeSet` with Parameter 1 `10`, or route `change volume to 10`. Record:

- `%SIG3_ProgressAccepted`: whether Android accepted the action.
- `%SIG3_Observed` and `%SIG3_CommandOK`: fresh displayed readback result.
- `%SIG3_SliderDiagnostics` and `%SIG3_Error`: native target and prerequisites/errors.
- Whether the actual aid volume audibly changed.

There is exactly one action, then a 500 ms wait and fresh readback. An unchanged/mismatched readback fails without retries or gestures. A changed label can still be cached app state: acceptance/display success cannot prove acoustic command commit. Repeat the same target to confirm no additional action, then test 10→9. Leave mute/max boundaries until ordinary volume works.

If the label changes but aids do not, stop: Signia's rounding/listener order may suppress its accessibility commit. Capture diagnostics and pursue the acoustic encoder investigation; do not tune drags.

## Reuse for balance and tinnitus

After volume works, run `SIG3_BalanceInspect` / `SIG3_TinnitusInspect`. Configure their actual readback/control IDs. Confirm the domain separately: Balance −8..7, Tinnitus 0..15, ascending linear native mapping. Set the corresponding `%SIG3_BalanceRangeConfirmed=1` / `%SIG3_TinnitusRangeConfirmed=1` only after checking. Then test one adjacent target through the corresponding Set task. Volume success alone does not certify another slider's mapping or commit behavior.

## Repository validation

`tests/check_sig3_progress.py` models inspection, missing range confirmation, touch exploration off, unsupported progress, an accepted action without displayed change, target success, repeated-target no-op and invalid targets for all three families. It does not run Android/BeanShell or verify acoustic reception. Older gesture simulations explicitly select `legacy-gesture` in their modeled Phone fixture; they do not validate the new backend.
