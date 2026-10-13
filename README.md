# Signia-Tasker-Control
Numeric voice controls on branch HeySid3: see [HeySig3 user manual](docs/HeySig3.md) and import [the separate project](projects/HeySig3.prj.xml). Original HeySig exports are preserved.

Supported numeric-control import: HeySig3 only. Disable old slider-triggering profiles during testing; do not import the placeholder `tasks/sig.tasks.tsk.xml` or `xml/backup.xml` as current controls. All public SIG3 UI operations share a single worker.

Priority 3 adds configured program selection, battery checks, AutoVoice/watch adapters, initialization, and optional noise/sleep program automation. See [setup and event wiring](docs/HeySig3.md#priority-3-setup); automation defaults off and phone profiles require explicit connection.

Restored workflows and event wiring: [HeySig3 completion](docs/HeySig3-completion.md). Start phone volume testing with [slider acceptance](docs/HeySig3-slider-acceptance.md). SoundWear has been removed.

Prioritized work still needed: [HeySig3 remaining work](docs/HeySig3-remaining-work.md).

Spoken phrases and supported alternatives: [HeySig3 voice commands](docs/HeySig3-voice-commands.md).

Planned phone/watch noise-based selection: [noise automation plan](docs/HeySig3-noise-automation-plan.md).

Phone verification updated October 12, 2026: direct Tasker volume, balance/tinnitus changes and restoration, unavailable-tinnitus guards, voice commands, automatic saved settings and voice restoration passed. Independent voice-prompt/result switches, spoken **cancel**, and **tin** shorthand are available. See [voice settings](docs/HeySig3-voice-settings.md) and [saved settings](docs/HeySig3-saved-settings.md).

Optional **Hey Sig** listening passed two consecutive tone-free commands and locked-phone unlock guidance, but **background wake still fails**. Listening was left off. See [wake setup and limitations](docs/HeySig3-wake-phrase.md). Full phone reboot, long-duration endurance and native accessibility movement remain untested.
Use the [completed and remaining test checklist](docs/HeySig3-test-checklist.md) to resume testing, and the [phone verification notes](docs/HeySig3-verified-usb-drags.md) for exact evidence. The [Pixel 9a setup task](tasks/SIG3_Pixel9aGestureSetup.tsk.xml) is imported separately from the project and applies only to the measured layout.
