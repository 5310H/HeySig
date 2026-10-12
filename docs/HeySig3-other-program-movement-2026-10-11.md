# Direct Set and other-program movement — October 11, 2026

Checklist item 7 and direct Tasker VolumeSet acceptance passed in a guarded 24-request run. The target program was chosen from the actual successful availability results and its configured slot, then checked against fresh app readback: Noisy. No program names or slider coordinates were added to production controls.

| Public task | Captured starting value | Adjacent target | Restored value |
| --- | ---: | ---: | ---: |
| SIG3_VolumeSet | 8 | 7 | 8 |
| SIG3_BalanceSet | 0 | −1 | 0 |
| SIG3_TinnitusSet | 7 | 6 | 7 |

Each adjacent target and restoration succeeded with fresh operation IDs, CommandOK=1, empty Error, complete stage, and independent selected-tab/displayed-value agreement. Each target was repeated; all six repeated requests returned success with Gesture empty, TouchStage `not run` and ProgressAccepted `not run`.

Actual movement used the configured Tasker dispatchGesture backend with one pointer, a 650 ms DOWN-MOVE-UP path and verified readback. Volume and Balance used the observed path (540,1304) → (540,1391); Tinnitus used (540,1391) → (540,1478). These paths are evidence from this configured phone, not new selector constants. No automatic backend fallback or RangeConfirmed change was made.

After restoring all three Noisy values, the test restored captured Universal and verified Volume 9, Balance 0 and Tinnitus 0. All 24 operations passed. This establishes small adjacent movement, direct Set, repeated-target no-op and reverse movement; full-range, endpoint and native SetProgress acceptance remain separate checklist items.

Evidence: `/tmp/sig3-adjacent-final.json`, validated by `/tmp/sig3_validate_adjacent.py`.
