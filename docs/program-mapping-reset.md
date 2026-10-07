# Program names and reset after charging

The six supplied names are mapped in the order given. Confirm this matches the phone's intended slot order:

| Slot | Stable key | Display-name variable | Initial display name |
| --- | --- | --- | --- |
| 1 | normal | %SIG_Program1 | Normal |
| 2 | tinnitus_only | %SIG_Program2 | Off just tinnitus |
| 3 | noisy | %SIG_Program3 | Noisy |
| 4 | outdoor | %SIG_Program4 | Outdoor |
| 5 | tv | %SIG_Program5 | TV |
| 6 | very_noisy | %SIG_Program6 | Very Noisy |

`SIG_ConfigurePrograms` supplies missing names without overwriting custom names. ProgramSwitch resolves the stable key through the mapping each time it runs. When renaming a program in Signia, update its corresponding `%SIG_ProgramN` variable to the exact new name. The saved preferred key remains valid. This does not automatically discover a rename or a reordered program list.

Select a mapped program using its slot or stable key, adjust the app as desired, then run **SIG_SaveSettings** or say **save settings**. Saving selects/verifies that program, reads volume and balance, and saves their values together only if both reads succeed. It saves tinnitus when that control is readable; otherwise restoration of tinnitus is disabled. Saved preferences are `%SIG_PreferredProgram`, `%SIG_PreferredVolume`, `%SIG_PreferredBalance`, and optional `%SIG_PreferredTinnitus`, with `%SIG_RestoreTinnitus` controlling whether tinnitus is restored. `%SIG_SaveOK` reports success.

After charging, open/unlock the phone and allow the aids to reconnect. Run **SIG_Reset**, or say **reset**, **restore settings**, or **restore my settings**. Reset snapshots the saved preferences, checks their validity, selects/verifies the mapped program with at most three attempts, then applies volume, balance, and enabled tinnitus preferences in that order. It stops on the first failure and sets `%SIG_ResetOK` to 1 only after all enabled steps succeed. Already-applied steps remain applied if a later step fails. Saved preferences survive a failed reset and are not overwritten by current startup readings. This restores app settings; it does not factory-reset the hearing aids.

Reset requires a previously saved profile and does not assume desired volume, balance, or tinnitus values. `keep_open` is supported. There is no automatic charger/Bluetooth trigger yet; reconnection and UI readiness must be verified on the phone before adding one.

The project contains the new ConfigurePrograms, SaveSettings, and Reset tasks and matching standalone files. Include their dependencies when moving the changes to the phone. Simulated regression coverage is in `tests/check_reset.py`; actual behavior on Signia 2.8.0.18214 remains unverified.
