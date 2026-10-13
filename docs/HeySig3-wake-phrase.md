# Hey Sig wake phrase

Run `SIG3_WakeEnable` to opt into AutoVoice Continuous listening and `SIG3_WakeDisable` to turn it off. Listening defaults off when its flag is unset. Keep `SIG3_HeySigWake` enabled when using the listener.

Say **Hey Sig**, pause until **Sig here** and the microphone prompt, then speak a command. The whole-phrase filter also accepts **Hey Cig**, a recognition alias. A wake phrase and command spoken together are unsupported. AutoVoice must have **Use Regex enabled** and **Exact Command disabled**: selecting Exact Command disables regex. Both settings were verified in the installed phone export.

Configure AutoVoice **General Settings → AutoVoice Continuous → Stream to Mute → Media** separately; this preference is not in the Tasker project XML. Both listener starts request persistent notifications. Media suppression prevents repeated recognition tones but temporarily mutes media while continuous listening is active. The listener pauses before cue/capture and restores captured media volume after a successful stop. The readiness helper waits up to two seconds for delayed unmute before speech. It resumes listening after a session only while `%SIG3_WakeEnabled=1`.

`SIG3_VoiceSettings` independently controls spoken results and prompts. Readiness respects prompts, DND, media volume and audio mode. Locked/screen-off, missing permission and busy-worker checks block capture. When speech is allowed, locked operation says **Unlock the phone, then say Hey Sig again** before stopping. Unlock manually; HeySig does not bypass the lock screen.

## Accepted on the phone, October 12, 2026

- Two consecutive wake → cue → microphone → current-program reply flows worked without repeated tones after the corrected regex and readiness setup.
- The user heard the locked-phone unlock instruction; the command worked after manual unlock.
- Media started at 22/25, unmuted, and returned to 22/25, unmuted, after the commands, locked recovery and Wake Disable.
- Two full Tasker application restarts preserved both mixed speech-preference combinations. Original choices were restored to on/on.

All 19 repository checks pass, including 16 executable readiness cases. Phone evidence comprises the verified regex project export and the subsequently installed voice-session export preserving its native capture action.

Full phone reboot and long-duration background/battery endurance remain untested. The Continuous foreground service remained active after more than two minutes at Home; the user reported the subsequent background wake command did not work. Background wake acceptance failed. Leave listening off after testing unless the user requests it enabled.
