# Signia-Tasker-Control
Numeric voice controls on branch HeySid3: see [HeySig3 user manual](docs/HeySig3.md) and import [the separate project](projects/HeySig3.prj.xml). Original HeySig exports are preserved.

Supported numeric-control import: HeySig3 only. Disable old slider-triggering profiles during testing; do not import the placeholder `tasks/sig.tasks.tsk.xml` or `xml/backup.xml` as current controls. All public SIG3 UI operations share a single worker.

Priority 3 adds configured program selection, battery checks, AutoVoice/watch adapters, initialization, and optional noise/sleep program automation. See [setup and event wiring](docs/HeySig3.md#priority-3-setup); automation defaults off and phone profiles require explicit connection.

Restored workflows and event wiring: [HeySig3 completion](docs/HeySig3-completion.md). Start phone volume testing with [slider acceptance](docs/HeySig3-slider-acceptance.md). SoundWear has been removed.

Prioritized work still needed: [HeySig3 remaining work](docs/HeySig3-remaining-work.md).

Phone noise sampling: [October 14 verification](docs/HeySig3-phone-noise-2026-10-14.md) corrected a plugin timeout and passed ten public-worker samples across quiet and conversation/TV surroundings. The later measured settings and automatic-loop evidence are recorded below.

[Selectable phone noise settings](docs/HeySig3-noise-settings.md) add three program roles, observation mode, hysteresis, confirmation, cooldown and guarded polling. Saving leaves switching off. Fixed-position Pixel measurements established −54.5 / −43 boundaries with 1.5 hysteresis, three confirmations and a 60-second cooldown; see [phone acceptance](docs/HeySig3-noise-settings-acceptance-2026-10-14.md).

October 14 acoustic investigation: [REA command and control-bit validation](docs/HeySig3-chirp-validation-2026-10-14.md) passed 131,072 comparisons against the installed Signia encoder. Active address/profile and full waveform comparison remain pending. Only battery checks give an audible aid response.

October 14: [slider acceptance passed](docs/HeySig3-slider-acceptance-2026-10-14.md) for occasional use on the configured Pixel 9a: 28 focused checks, all three controls restored, and exact saved-record verification. [Selectable sleep schedules also passed phone acceptance](docs/HeySig3-sleep-acceptance-2026-10-14.md) with Signia open; automation is left off for your own choices. Phone noise automation now has controlled dispatch, measured sampling and bounded background acceptance; broader overnight/reboot reliability remains pending.

October 13 work in progress: [slider endpoint findings and handoff](docs/HeySig3-verification-2026-10-13.md) and [selectable sleep settings](docs/HeySig3-sleep-settings.md). The revised activation/drag sequence now has the October 14 focused phone acceptance linked above; sleep schedule events now have the October 14 acceptance above; phone noise calibration now has the measured October 14 acceptance linked above.

Spoken phrases and supported alternatives: [HeySig3 voice commands](docs/HeySig3-voice-commands.md).

Planned phone/watch noise-based selection: [noise automation plan](docs/HeySig3-noise-automation-plan.md).

Phone verification updated October 12, 2026: direct Tasker volume, balance/tinnitus changes and restoration, unavailable-tinnitus guards, voice commands, automatic saved settings and voice restoration passed. Independent voice-prompt/result switches, spoken **cancel**, and **tin** shorthand are available. See [voice settings](docs/HeySig3-voice-settings.md) and [saved settings](docs/HeySig3-saved-settings.md).

Optional **Hey Sig** listening passed two consecutive tone-free commands and locked-phone unlock guidance, but **background wake still fails**. Listening was left off. See [wake setup and limitations](docs/HeySig3-wake-phrase.md). Full phone reboot, long-duration endurance and native accessibility movement remain untested.
Use the [completed and remaining test checklist](docs/HeySig3-test-checklist.md) to resume testing, and the [phone verification notes](docs/HeySig3-verified-usb-drags.md) for exact evidence. The [Pixel 9a setup task](tasks/SIG3_Pixel9aGestureSetup.tsk.xml) is imported separately from the project and applies only to the measured layout.

Opt-in [direct slider dragging](docs/HeySig3-direct-volume.md) moves to a requested level with one continuous stroke and verifies the final value. Volume 10 → 7 → 10 and balance −4 → −1 → −4 passed through normal Tasker commands. Tinnitus 0 → 3 → 0 also passed with a brief activation tap at zero; the existing one-level method remains selectable.
