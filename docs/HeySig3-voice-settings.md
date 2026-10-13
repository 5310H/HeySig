# Voice settings

Run **SIG3_VoiceSettings** in Tasker to open two independent on/off controls:

- **Spoken results**: command confirmations and failure replies.
- **Voice prompts**: “Sig here” and spoken retry instructions.

Select the options and tap **Save**. **Cancel**, Back, and dismissal leave the choices unchanged. Both options may be off; microphone capture, on-screen prompts, retry choices, and on-screen command results still work. These controls do not enable or disable **Hey Sig** listening.

Saved choices are written together to Tasker's private application preferences and mirrored to `%SIG3_VoiceResponses` and `%SIG3_VoicePrompts`. Voice capture and replies reload missing settings from that persistent storage. Existing valid Tasker values are preserved; if the new prompt setting has never been chosen, it initially follows the existing spoken-response preference.

Local executable checks cover all four combinations, loading after clearing globals, legacy settings, failed saves, invalid selections, and settings Save/Cancel. The actual readiness and result formatters are also tested independently. Installed-phone checks on October 12, 2026 passed saving and reopening all four combinations, Cancel, and Back without saving. Both settings were restored to on after these checks and the independent speech test. Durable reload and two Tasker application restarts passed; a full phone reboot remains untested. The user confirmed live capture and a spoken current-program reply with voice prompts off and spoken results on: no readiness cue played.

Say **cancel** in the general microphone prompt to end the session without sending a command or changing saved settings. Cancellation does not open the retry dialog or speak a stale command result; the wake wrapper can resume listening normally.

Installed-phone acceptance on October 12, 2026: the user said **cancel** in the general voice prompt and confirmed it closed cleanly without “not recognized” or Try again. Wake listening was disabled during this test.

**Tin** is a supported spoken shorthand for tinnitus in control commands: “tin 3,” “set tin to zero,” “current tin,” and “tin mute.” Program names containing tin are preserved. Installed-phone acceptance on October 12, 2026: the user said “current tin” and confirmed it was recognized, with tinnitus correctly reported unavailable in the current program.

Installed persistence acceptance: two full Tasker force-stop/restart cycles preserved mixed settings [spoken results on, prompts off] and [spoken results off, prompts on]. Original choices were restored afterward. This verifies application restart persistence; a full phone reboot is a separate check.
