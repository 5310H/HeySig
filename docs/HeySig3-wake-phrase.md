# Hey Sig wake phrase

Use `SIG3_WakeEnable` to opt into AutoVoice Continuous listening and `SIG3_WakeDisable` to turn it off. The generated project includes `SIG3_HeySigWake`, an exact **hey sig** AutoVoice Recognized event restricted to the `continuous` source. The listener defaults off when its flag is unset; importing the profile alone does not start it. Keep the wake profile enabled when using the listener.

Say **Hey Sig**, wait for **Sig here**, then speak a supported command. The listener pauses before readiness speech and Tasker's native microphone capture. It resumes after the command session, including cancellation and unrecognized-speech cancellation, only while `%SIG3_WakeEnabled=1`. Disabling listening during a prompt prevents its restart. Manual `SIG3_VoiceCommand` uses the same handoff. The older AutoVoice command adapter ignores continuous speech while wake listening is enabled, preventing commands from bypassing the wake prompt. Watch commands keep their existing path.

The cue respects `%SIG3_VoiceResponses`, media volume, DND, and audio mode. Screen-off, locked, missing microphone permission, and a busy worker block native capture. Those blocked cases currently show a toast/status; spoken unlock instructions and live screen-off/locked acceptance remain pending. Nothing bypasses the lock screen.

The start, stop, and event envelopes were exported from the installed AutoVoice 4.0.14 plugin. Listener state reported by a successful plugin call is a request result; live wake detection still needs acceptance. Always-on recognition and restart persistence have not yet been verified on this phone.

Local checks execute the actual wake predicate in BeanShell and simulate start/stop, pause/resume, capture cancellation, plugin failure, disabling during capture, repeated wake while busy, and blocking direct AutoVoice commands. The user confirmed the readiness cue, native microphone prompt, and full spoken current-program reply. Live wake-phrase acceptance is still pending.
