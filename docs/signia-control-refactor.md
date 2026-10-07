# Signia control refactor

Target installed version supplied by the user: **2.8.0.18214**. This is a logic refactor, not a claim of verified Android compatibility.

## Import

Back up the Tasker project and import `projects/HeySig.prj.xml`. It includes the new shared `SIG_AppClose` and `SIG_AppError` tasks. Individual imports must include both helpers, all six tasks in each control family, Dispatcher, ProgramSwitch, and VoiceRouter. Existing configured `%SIG_Program1` through `%SIG_Program6` must match the program names displayed in Signia.

## Behavior

- Volume and tinnitus use 0–15; balance uses the user-confirmed −8–7 range. Balance and tinnitus keep their own level and success variables; volume retains `%SIG_Level` for existing consumers.
- Set snapshots the requested target, validates and clamps it locally, shares one direction-selected loop, and verifies the final displayed value. The global requested target is preserved. Invalid input, plugin failure, ambiguous readings, and oversized moves report failure. An already-reached target reports success.
- Current selects the correct tab and reads its accessible number without tapping candidate values. Queries check the foreground package; failed tab clicks stop before a number can be used. Plugin errors are handled immediately with Continue Task After Error enabled, so they cannot silently continue into a gesture.
- Up/Down uses coordinates returned by the number click, verifies the resulting level, and permits at most 20 attempts. Negative gesture endpoints are rejected. Overshoots stop rather than being reversed. Display dimensions and pixel sensitivity still require device verification.
- Shared AppClose/AppError tasks keep exit behavior consistent. Normal completion returns to the home screen rather than attempting to kill Signia's process. `keep_open` is forwarded through endpoint wrappers and honored on success, no-op, and failure exits.
- Dispatcher snapshots the incoming action and routes volume, balance, tinnitus, battery, and program commands. VoiceRouter matches full commands and derives numeric targets from the command itself rather than depending on AutoVoice capture groups. Examples: `volume 15`, `set balance to -8`, `tinnitus down`, `program 2`. Out-of-range or unrecognized commands do not move a slider.
- ProgramSwitch clicks the configured program name instead of guessing screen rows or using a fixed x-coordinate. It updates `%SIG_CurrentProgram` only after a query finds the requested name on the returned screen. A name appearing elsewhere on that screen remains a possible false positive until its specific accessibility node is confirmed.

## Verification

Run all scripts in `tests/check_*.py`. They test simulated transitions, range boundaries, negative balance, request isolation, keep_open, plugin failures, wrong foreground packages, ambiguous readings, voice routing, configured program selection, and equality of standalone/project exports. These mocks do not execute Tasker, AutoInput, Signia, Bluetooth, or hearing aids.

Before claiming compatibility with 2.8.0.18214, obtain AutoInput UI Query text and element IDs on each tab and after selecting a program. Confirm the hard-coded English tab labels and activity class still exist, bind numeric controls to their actual node identities where available, and verify swipe direction and one-level movements near the center and endpoints. Test unavailable tinnitus, streaming, and separate left/right controls if enabled. Reading a displayed value verifies the app UI, not delivery of a setting to connected hearing aids.

Error handling follows [Tasker's Continue Task After Error documentation](https://tasker.joaoapps.com/userguide_summary.html). AutoInput requires accessibility support; its [FAQ](https://joaoapps.com/autoinput/faq/) describes cases where apps do not expose usable accessibility clicks.
