# Hey Sig wake phrase

Run `SIG3_WakeEnable` to opt into AutoVoice Continuous listening and `SIG3_WakeDisable` to turn it off. The generated project includes the continuous-source `SIG3_HeySigWake` event. Listening defaults off when its flag is unset. Keep the profile enabled when using the listener.

Say **Hey Sig**, pause until **Sig here** and the native microphone prompt, then speak a command. A wake phrase and command spoken together are not supported. Logs showed a missed attempt as “hey sig current volume”; another was recognized as “hey cig.” The generated event and wake handler now accept the narrow recognition alias **Hey Cig**, still matching only the whole wake phrase. The phone handler is installed, but the phone event’s regex option has not been verified enabled. Wake alias acceptance is therefore pending.

The listener pauses before readiness speech and microphone capture, then resumes after the session only while `%SIG3_WakeEnabled=1`. Cancellation and disabling during a session prevent inappropriate command dispatch or listener restart. Continuous speech does not directly enter the older command adapter while wake listening is enabled. Watch commands retain their own path.

`SIG3_VoiceSettings` independently controls spoken results and voice prompts. The readiness cue respects `%SIG3_VoicePrompts`, DND, media volume, and audio mode. Locked/screen-off, missing microphone permission, and busy-worker checks block capture. Locked cases currently provide a toast/status; spoken unlock guidance remains unfinished. HeySig does not unlock the phone.

## Accepted phone behavior

On October 12, 2026 the user confirmed a complete unlocked wake → readiness cue → microphone → spoken current-program reply, followed by a second successful command in the initial configuration. Continuous service restart after a command was observed. Later missed wake attempts and inconsistent repeated use mean sustained reliability has not passed.

Persistent notifications are now requested by both Continuous On actions. The installed listener was verified as a foreground service. In AutoVoice, **General Settings → AutoVoice Continuous → Stream to Mute → Media** stopped repeated tones and allowed the requested spoken flow. System suppression did not reliably stop tones. This app preference is device configuration, not part of Tasker project XML.

## Unfinished volume and wake reliability

Android audio events attributed media-volume changes, including zero, to AutoVoice. Media tone suppression temporarily mutes media while listening; restoration was inconsistent. The installed experimental media helper captures volume before first enable and each resume, then restores it after a successful listener stop. It preserves captured zero, does nothing without a snapshot, and stops with a status on invalid targets or restoration failure. Five actual BeanShell audio cases and wake lifecycle simulations pass, but the user’s repeated-command test still failed. Do not treat volume preservation as accepted.

A bounded wait for delayed media unmute has local readiness coverage but has not been installed in the phone voice session. Media inspection while continuous listening is active does not establish the volume during cue playback.

Locked-screen tests yielded tones/no spoken instruction; one successful post-unlock command was followed by a failed second attempt. Screen-off/locked recognition, background endurance, restart persistence, and reliable repeated wake commands remain pending. The user explicitly requested microphone listening off; AutoVoice was stopped and its continuous service was absent afterward. Keep listening off until further testing is requested.

The [AutoVoice FAQ](https://joaoapps.com/autovoice/faq/) recommends persistent notifications for continuous processes that stop and describes recognition-start sounds. Neither notification persistence nor tone suppression alone establishes reliable wake behavior.
