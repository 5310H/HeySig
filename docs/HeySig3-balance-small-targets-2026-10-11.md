# Small balance-target acceptance

Verified October 11, 2026 on the Pixel 9a for item 3 of the [phone test checklist](HeySig3-test-checklist.md). The earlier 0 → −1 → 0 voice test remains accepted separately.

Fresh public BalanceCurrent readback captured **−3 in Universal**. The temporary `SIG3_TestBalanceSmallAcceptance` task derived targets one and two levels above and below that actual starting value. It called installed public BalanceSet tasks with one-step moves between intermediate levels, repeated targets, and restoration. No program names were hardcoded into the test guards.

The test stopped on a failed request, stale operation ID, unexpected readback, program change, or movement on a repeated target. Starting values outside −5–4 would stop before Set rather than introduce endpoint testing.

| Request | Fresh balance readback | Movement |
| --- | --- | --- |
| BalanceCurrent | −3 | none |
| BalanceSet −2 | −2 | one adjacent gesture |
| BalanceSet −1 | −1 | one adjacent gesture |
| Repeat −1 | −1 | none |
| BalanceSet −2 | −2 | one adjacent gesture |
| Restore −3 | −3 | one adjacent gesture |
| BalanceSet −4 | −4 | one adjacent gesture |
| BalanceSet −5 | −5 | one adjacent gesture |
| Repeat −5 | −5 | none |
| BalanceSet −4 | −4 | one adjacent gesture |
| Restore −3 | −3 | one adjacent gesture |
| Repeat restored −3 | −3 | none |

All 12 requests returned CommandOK=1, empty Error, stage `complete`, and distinct operation IDs. Every recorded program was Universal. Eight moves each recorded one 650 ms continuous gesture and TouchStage=`released`. The three repeated Set requests had empty Gesture, TouchStage=`not run`, and ProgressAccepted=`not run`.

The installed balance backend was `legacy-gesture`, StepPx=87, Direction=1. Gesture Y positions matched the tested levels: −1=1391, −2=1478, −3=1565, −4=1652, −5=1739, at X=540. Each move traversed one 87-pixel step. Production tasks and backend configuration were used without modification.

Independent final Signia screen readback confirmed **Universal Active**, **Selected Sound Sharpness Tab**, and `com.signia.rta:id/TA-SliderValue` text **−3** (ASCII `-3` in the accessibility tree). The actual starting setting was restored.

Local evidence: `/tmp/HeySig3-balance-small-acceptance-20261011.json` and `/tmp/HeySig3-balance-small-final-20261011.xml`. The temporary task and its test files are excluded from repository exports.

After preserving the evidence, deleted the imported temporary task and removed its XML and diagnostic JSON from the phone. Checklist item 3 is complete for these sampled small targets.

Small adjacent targets on both sides of the captured start, reverse movement, repeated-target no-ops, and restoration passed with fresh app readback. This accepts the sampled levels −5 through −1 in Universal; full-range targets, long jumps, endpoints, other programs, and native accessibility movement remain separate tests. The repository numeric simulation also passed its 768 transitions and failure cases.
