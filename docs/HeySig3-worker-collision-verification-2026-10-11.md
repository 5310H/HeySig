# Busy-worker collision and recovery verification

Verified October 11, 2026 on the connected Pixel 9a for item 10 of the [phone test checklist](HeySig3-test-checklist.md).

## Method

Backed up the phone worker export to `/tmp/SIG3_Worker-before-collision-20261011.tsk.xml`. The temporary worker adds a diagnostic snapshot, a two-minute Wait after its initial result resets, and a Stop before dispatch. It retains the installed worker's collision policy and name. The first task therefore remains genuinely active without issuing Signia control actions.

Sent a read-only `Volume,Current,` request while that worker was active. Tasker visibly rejected it with:

> Not running task "SIG3_Worker": Already running and Collision Handling is set to Abort New Task.

This direct collision stopped the diagnostic caller at its Perform Task action, despite Continue After Error, so subsequent actions in that caller did not collect an after-snapshot. It is not treated as a completed volume query.

A second run tested the installed public `SIG3_VolumeCurrent` entry point through a separate temporary caller. This produced the same visible Tasker rejection. The outer caller continued and collected its after-snapshot. An independent observer collected another snapshot while the first worker remained active.

## Recorded results

| Check | Observed |
| --- | --- |
| First worker operation ID | `1791744019792` |
| Running tasks before second public request | `,SIG3_TestBusyPublic,SIG3_Worker,` |
| Running tasks after second public request | `,SIG3_TestBusyPublic,SIG3_Worker,` |
| Running tasks at independent observation | `,SIG3_TestBusyRecovery,SIG3_Worker,` |
| Authoritative success throughout the collision | `CommandOK=0` |
| Authoritative result throughout the collision | `pending: operation did not finish` |
| Stage throughout the collision | `start` |
| Gesture / touch / progress | empty gesture; `not run`; `not run` |

Compared every captured SIG3 result field between the first worker's initial snapshot and the independent observation: operation ID, command success, error, result, stage, gesture, touch stage, program, previous/expected/observed/target values, audio/slider diagnostics, progress acceptance, and family success flags were unchanged. Tasker did not start a new worker or overwrite the first operation's results. Family-specific flags retained earlier values; completion must use the authoritative success and fresh operation result rather than those flags alone.

The public request's before/after snapshots were about 129 ms apart while the first worker remained active. The request was rejected rather than deferred until the worker finished. The warning was captured on screen; this does not certify a spoken busy-command reply or the public wrapper's custom toast.

## Recovery

Reimported the exact backed-up worker. Before the recovery request, the running-task list contained only `SIG3_TestBusyRecovery`, with the prior operation still pending and CommandOK=0. A fresh read-only volume request then completed with a new operation ID `1791744192988`, CommandOK=1, empty error, stage `complete`, observed value `9`, and program `Universal`.

An independent Signia screen read confirmed **Universal Active**, **Selected Volume Tab**, and displayed volume **9**. The recovery query performed no gesture or progress action.

Local evidence: `/tmp/HeySig3-collision-direct-20261011.json`, `/tmp/HeySig3-collision-public-20261011.json`, `/tmp/HeySig3-collision-recovery-20261011.json`, `/tmp/heysig-collision-direct.png`, and `/tmp/heysig-collision-public.png`. Temporary tasks and worker instrumentation are excluded from repository exports.

Deleted the three imported temporary probes and their phone test files after preserving the evidence locally. Exported the restored worker to `/tmp/SIG3_Worker-after-collision-20261011.tsk.xml`; its name and all 350 actions match the pre-test backup exactly after normalizing insignificant XML formatting. The temporary pause and Stop are removed.

## Acceptance limits

Second-command rejection through a direct worker request and the public VolumeCurrent entry point, preservation of the first operation's result, and subsequent fresh read-only recovery passed. This test covers a controlled pre-dispatch Wait. It does not certify collision during a gesture/plugin action, interruption of nested internal helpers, every public entry point, or spoken busy responses. The repository coordination simulation passed separately.
