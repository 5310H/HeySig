# Public TinnitusSet acceptance

Verified October 11, 2026 on the Pixel 9a for item 2 of the [phone test checklist](HeySig3-test-checklist.md).

The temporary `SIG3_TestTinnitusAcceptance` task called the installed public `SIG3_TinnitusCurrent`, followed by public `SIG3_TinnitusSet` with Parameter 1 values `1`, `0`, `0`, and the captured starting value. It recorded each result and stopped on failed requests, stale operation IDs, unexpected values, a program change, or movement on the repeated target. Starting values outside 0/1 would stop before any Set request rather than introduce an unaccepted long jump.

Fresh starting readback was **tinnitus 0 in Universal**. All five requests completed with CommandOK=1, empty Error, stage `complete`, and distinct operation IDs. The actual starting program was captured and used for subsequent guards.

| Request | Fresh observed value | Movement evidence | Operation ID |
| --- | --- | --- | --- |
| TinnitusCurrent | 0 | no gesture | `1791744624081` |
| TinnitusSet 1 | 1 | one 650 ms gesture, `540,2000 → 540,1913`; touch released | `1791744628190` |
| TinnitusSet 0 | 0 | one 650 ms gesture, `540,1913 → 540,2000`; touch released | `1791744632146` |
| TinnitusSet 0 again | 0 | empty Gesture; TouchStage=`not run`; ProgressAccepted=`not run` | `1791744636116` |
| Restore captured starting value 0 | 0 | empty Gesture; TouchStage=`not run`; ProgressAccepted=`not run` | `1791744637985` |

Every recorded program was Universal. The installed tinnitus backend was `legacy-gesture`, StepPx=87, Direction=1. Movement preflight recorded media volume 17/25 against minimum 13/25, with interruptionFilter=1. No backend or phone audio settings were changed by this test.

Independent final Signia screen readback showed **Universal Active**, **Selected Tinnitus Signal Tab**, and `com.signia.rta:id/TA-SliderValue` text **0**. The starting setting was restored.

Evidence is preserved locally in `/tmp/HeySig3-tinnitus-acceptance-20261011.json` and `/tmp/HeySig3-tinnitus-acceptance-final-20261011.xml`. The temporary task and its phone test files are excluded from repository exports. Production tasks were used without modification.

After preserving the evidence, deleted the imported temporary task and removed its XML and diagnostic JSON from the phone. The checklist and remaining-work record now mark item 2 complete.

Direct public Set, reverse movement, repeated-target no-op, and final restoration passed using fresh app readback. This does not certify other programs, long jumps/endpoints, or native accessibility movement. The repository tinnitus-availability simulation passed separately.
