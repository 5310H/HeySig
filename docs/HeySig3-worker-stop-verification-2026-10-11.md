# Controlled worker Stop and recovery verification

Verified October 11, 2026 on the connected Pixel 9a. This tests manual Stop of the actual `SIG3_Worker` before dispatch, followed by recovery with a read-only program query.

## Procedure and evidence

Exported the installed worker to `/tmp/SIG3_Worker-before-stop-20261011.tsk.xml` before changing it. The installed export contains 350 actions and differs from the repository worker; restoration uses this phone backup, not a replacement from the repository.

The temporary version adds a Java diagnostic snapshot and a two-minute Wait after the worker's initial result resets and before request parsing or Signia control dispatch. No slider or program change is requested. The first import truncated at the diagnostic action because its XML attributes were serialized in a different order; that attempt did not produce the snapshot and is not accepted as a Stop test. The corrected temporary export uses Tasker's `sr`-then-`ve` action attribute order.

The successful run recorded:

| Check | Observed |
| --- | --- |
| Running worker before Stop | `%TRUN = ,SIG3_Worker,` |
| Command success before Stop | `%SIG3_CommandOK = 0` |
| Result before Stop | `pending: operation did not finish` |
| Error before Stop | empty |
| Stage before Stop | `start` |
| Stop timing | 7.77 seconds after Play, during the two-minute Wait |
| Visible control | square before Stop; triangle after Stop |

The original worker was reimported before the recovery probe. The probe first recorded the stopped state without issuing a worker command: `%TRUN` contained only `SIG3_TestStopRecovery`, `%SIG3_CommandOK` remained `0`, the result remained `pending: operation did not finish`, and stage remained `start`. This confirms that the worker was absent and its authoritative result did not claim success. Family-specific values such as `ProgramOK` and `Level` retained earlier values; those values alone must not be interpreted as completion of the interrupted operation.

The probe then requested `Program,Current,` through the restored worker. Fresh readback returned `Universal`, `%SIG3_CommandOK = 1`, an empty error, and stage `complete`. The result was `Program: Universal; program=Universal (app state; aid receipt unverified)`.

Evidence is saved locally in `/tmp/HeySig3-worker-stop-timing-20261011.json`, `/tmp/HeySig3-worker-stop-after-20261011.json`, `/tmp/HeySig3-worker-stop-recovery-20261011.json`, and the before/after screenshots `/tmp/heysig-worker-before-stop.png` and `/tmp/heysig-worker-after-stop.png`. Temporary tasks and pauses are excluded from repository exports.

After recovery, deleted the imported `SIG3_TestStopRecovery` task and removed the temporary test exports and diagnostic JSON files from the phone. Exported the restored worker again to `/tmp/SIG3_Worker-after-stop-20261011.tsk.xml`; its name and all 350 actions match the pre-test backup exactly after normalizing insignificant XML formatting. The temporary pause is removed.

## Acceptance limits

Manual Stop during the worker's controlled pre-dispatch Wait and subsequent read-only recovery passed. This does not establish interruption during a gesture, an in-flight plugin action, or a nested internal helper; collision/rejection of a second command while the worker runs also remains a separate live test. No hearing-aid settings were changed by this test.

Repository `tests/check_sig3_coordination.py` passed separately; its modeled recovery checks do not substitute for the phone evidence above.
