# Last settings and voice restoration

HeySig3 automatically persists the last successful change sent through its worker. The record contains the selected program, volume, balance, and tinnitus level when that program supports it. Unavailable tinnitus is stored as `null`.

With a complete record for the same configured program, a verified volume change to 9 replaces just volume with 9; balance and tinnitus retain their last known values. The first change or a program change reads all available controls to establish a complete baseline. Read-only queries, failed changes, repeated targets that send no change, and restoration do not replace the saved record. Changes made directly in the Signia app are not tracked by this feature.

Say **“restore settings”** through the existing voice-command flow, or run `SIG3_RestoreSettings`. It validates the record and program mapping before changing the app, selects and verifies the saved program, then sets and rereads its available controls through the existing worker and audio guards. It skips tinnitus when absent. A saved tinnitus value that is no longer available produces a partial-restore report. Any failure retains the record for a retry.

**“Save settings”** / `SIG3_SaveSettings` provides an optional complete refresh. Normal HeySig3 changes save automatically. A save failure is reported separately from an already successful control change.

The record lives in Tasker's private files directory as `heysig3-settings-v1.json`, with format version, configuration names and timestamp. Replacement uses a synced temporary file in the same directory. Charging, reconnecting and app queries do not themselves write this file. There is no automatic restore trigger; restoration is requested by voice or task.

## Verification

Run `python3 tests/check_sig3_settings_flow.py` for generated worker/voice/restore flow checks. Run `python3 tests/check_sig3_settings_snapshot.py` for 33 actual BeanShell JSON and file cases, including restart persistence, invalid records, partial restoration, incremental updates and failed-save result preservation. The latter needs `/usr/share/java/bsh.jar` and an `org.json` runtime JAR; set `SIG3_JSON_JAR` to its path (the development fixture used `org.json:json:20240303`).

Acceptance tests cover persistent saved settings and Signia app readback. At the user’s direction, physical hearing-aid responses and a real charging cycle are outside this test scope; the aids do not provide a response to verify.

The installed phone passed [12 app-only checks](HeySig3-settings-verification-2026-10-11.md), including incremental updates, simulated defaults, restoration and unavailable tinnitus. Final saved state: Universal / volume 9 / balance 0 / tinnitus 0.
