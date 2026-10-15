# Phone reliability checks: October 14, 2026

## Full reboot persistence: passed

The Pixel 9a was unplugged at 100% before testing. A read-only Tasker helper (`python3 tools/build_sig3_reliability_read.py`) captured durable noise/voice/sleep preferences, relevant globals and the SHA-256 of the private settings record. After an actual phone reboot, manual unlock and reconnection on the new wireless-debugging port, the same helper captured them again.

All captured values matched. Noise configuration retained the measured −54.5 / −43 boundaries, 1.5 margin, three confirmations and 60-second cooldown. Noise sampling, diagnostic logging, sleep automation and continuous wake listening stayed off. Spoken results and prompts remained on. The private settings hash remained `a604e86648ff071b79e3e800a660b2479783287b99e82c3b85772053b4cf9f89`. The empty sleep preference store remained empty; this does not accept persistence of a newly configured sleep schedule. Uptime fell from 786,102,936 ms to 210,814 ms, confirming a phone reboot rather than an application restart.

This accepts saved-value persistence; it does not claim automatic startup, post-reboot wake recognition or an unattended sleep transition.

## Eight-hour observation trial: interrupted by native Tasker crash

The user selected eight hours unplugged and mostly idle. The trial samples in **observation mode only**. Continuous Hey Sig listening stays off to avoid microphone contention. The test uses the production polling task with every production action retained; only its optional numeric logger adds a test-only aggregate summary and an automatic stop at the first polling tick after the deadline. No boot profile is installed.

Build the temporary exports with `python3 tools/build_sig3_endurance_trial.py`. Import the instrumented `SIG3_NoisePoll` and the three temporary start/stop/smoke tasks. Run `00_SIG3_EnduranceSmoke` first; it invokes the same start task with a 60-second duration. The on-phone smoke run passed five fresh samples with no failures, a maximum 15.917-second sample gap and an automatic stop 9.212 seconds after the requested one-minute deadline. After the smoke run completes, run `00_SIG3_EnduranceStart` without a parameter for eight hours. The recorder uses elapsed uptime for the stop deadline, so a wall-clock adjustment cannot shorten the run. Android suspension can delay the next tick; maximum tick gap and stop delay are recorded rather than assuming exact scheduling. A summary recording failure stops sampling and diagnostics. Explicit early stopping is available through `00_SIG3_EnduranceStop` or the public `SIG3_NoiseStop`.

The bounded summary is `/sdcard/Tasker/sig3-endurance-summary.json`. It retains first/last battery readings, elapsed uptime, fresh/error/skip counts, locked-screen counts, charging counts and the largest gap between fresh sample timestamps. The separate numeric log can roll over without losing aggregate counts. No audio is recorded. The previous summary is retained as one `.previous` file when another run starts.

After completion, inspect status, elapsed duration, sample gaps and failed/skipped counts before accepting endurance. Charging invalidates an unplugged battery comparison. Battery percentage and charge-counter changes describe total phone use during this instrumented run, including Android, wireless debugging and diagnostics; they do not isolate the cost of noise sampling. A separate comparable idle period is needed for that attribution. Unavailable charge counters must not be interpreted as measured capacity.

Collect the summary and reimport the release `tasks/SIG3_NoisePoll.tsk.xml` to remove the temporary instrumentation. Remove the temporary tasks after final evidence collection. Leave sampling and diagnostics off afterward. Do not overwrite the instrumented polling task during an active trial, because that removes its automatic stop.

Endurance and battery results remain pending until the full timed run is collected.

The full trial started October 14 at 7:21 p.m. EDT, with its deadline October 15 at 3:21 a.m. EDT (automatic stopping occurs at the next available polling tick). Initial screen-off samples passed, with no capture errors or charging detected. Final acceptance requires collecting the completed summary after that deadline. The temporary diagnostic polling task remains installed until collection and release-export restoration.

## October 15 collection: eight-hour acceptance failed

Collected the [phone summary](evidence/HeySig3-endurance-2026-10-15.json) at approximately 9:24 a.m. EDT. The final recorded tick was October 15 at 12:55:21.654 a.m. EDT, after 5 hours 34 minutes 15 seconds of recorded observation. The summary remains `running`; it never reached the eight-hour deadline or recorded an automatic stop.

Android `dumpsys activity exit-info net.dinglisch.android.taskerm` reports Tasker process 4083 exited at 12:55:44.692 a.m. EDT with reason 5, `APP CRASH(NATIVE)`, status 6. This closely follows the final sample and explains the interrupted recording; the native crash cause is not yet established. Phone uptime at collection was 51,361 seconds, so this was not a phone reboot.

Before interruption: 1,255 fresh samples, zero failed attempts, zero skipped ticks, 986 locked-screen ticks, zero charging ticks, maximum sample gap 17.099 seconds and maximum tick gap 17.155 seconds. Observation mode remained selected and the final sample reported no command error. Battery fell from 100% to 85% during the recorded interval (charge counter 4,740,000 to 4,022,500 microAh). This measures total phone consumption, not sampling alone. The phone was charging at collection, so its current battery cannot extend the unplugged comparison.

Eight-hour endurance and automatic-stop acceptance remain unmet. Temporary instrumentation has not been removed during this read-only result check.

## Native crash investigation

The preserved [native crash report](evidence/HeySig3-tasker-native-crash-2026-10-15.txt) identifies Tasker 6.6.20 on Android 17. The fatal thread is `RenderThread`, with abort message `mprotect(0x718aaad000, 393216, 1) failed: Out of memory`. Its backtrace passes through the Android dynamic linker and `libhwui` rendering hint-session initialization. The crash buffer timestamps the abort at 12:55:37.620 a.m., approximately 16 seconds after the last successful sample. The device was dozing and locked. The [full retained tombstone](evidence/HeySig3-tasker-tombstone-2026-10-15.txt) was also collected.

This establishes the immediate failure mechanism, but does not establish which component exhausted memory or mappings. Neither a HeySig leak nor a Tasker/Android rendering defect is proven. The restarted Tasker process measured approximately 36 MiB PSS at collection; this is not a measurement of the crashed process. The retained tombstone output is truncated by Android and provides no complete pre-crash memory history. Reading the kernel map-count limit was denied by Android.

Source review confirms that noise capture uses the exported AutoVoice action, and diagnostic storage is bounded. There is no demonstrated source change that fixes this native failure. Before another full endurance trial, use a shorter controlled observation with periodic external Tasker and AutoVoice memory/process measurements, then compare polling with diagnostics enabled and disabled. Retain process IDs to detect restarts and treat a stale summary as interrupted, never completed. No phone configuration or production code was changed during this investigation.

## October 15 short diagnostic: passed, crash not reproduced

The existing one-minute smoke task completed with five fresh samples, zero failures/skips and a maximum sample gap of 15.969 seconds. Automatic stop delay was 9.492 seconds. The phone started charging and was unplugged during the test (three charging ticks); no unplugged battery comparison is claimed. See [smoke summary](evidence/HeySig3-endurance-smoke-2026-10-15.json).

The new read-only `tools/observe_sig3_memory.py` collected seven external snapshots over approximately 180 seconds, recording Tasker/AutoVoice process IDs, `dumpsys meminfo`, phone uptime and trial summary. Neither process restarted. Tasker PSS ranged from 85,239 to 155,353 KiB; these fluctuating readings do not establish a leak or explain the overnight failure. Tasker UI activity during setup and final verification is included. See [memory observations](evidence/HeySig3-memory-smoke-2026-10-15.jsonl). This brief test cannot rule out accumulation over hours or locked-phone behavior.

The [post-test snapshot](evidence/HeySig3-post-smoke-settings-2026-10-15.json) confirms sampling, diagnostics, continuous wake listening and sleep automation are off. The recorder CLI and Python compilation passed. No production fix has been demonstrated and eight-hour endurance remains unaccepted.

## October 15 thirty-minute observation: completed; limited locked coverage

The [30-minute summary](evidence/HeySig3-endurance-30min-2026-10-15.json) reports 114 fresh samples, zero failed attempts, zero skipped ticks, zero charging ticks, maximum sample gap 16.241 seconds and automatic completion 4.367 seconds after the monotonic deadline. Battery fell from 100% to 98%; charge counter fell from 4,607,500 to 4,507,500 microAh. These are whole-phone measurements.

Only 13 of 114 ticks reported the keyguard locked. This accepts a 30-minute unplugged observation, but does not establish 30 minutes of locked-screen operation.

The [external memory observations](evidence/HeySig3-memory-30min-2026-10-15.jsonl) contain 20 snapshots with unchanged Tasker and AutoVoice process IDs. Tasker PSS ranged from 74,780 to 100,762 KiB; AutoVoice from 16,679 to 25,279 KiB. There is a roughly 2,529-second observer gap between elapsed 1,105 and 3,634 seconds, so memory coverage is incomplete during the latter part of the trial. The phone summary nevertheless records uninterrupted sample gaps below 16.3 seconds. No native crash was reproduced; this is not proof that the overnight failure is fixed.
