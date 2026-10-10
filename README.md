# Signia-Tasker-Control
Numeric voice controls on branch HeySid3: see [HeySig3 user manual](docs/HeySig3.md) and import [the separate project](projects/HeySig3.prj.xml). Original HeySig exports are preserved.

Supported numeric-control import: HeySig3 only. Disable old slider-triggering profiles during testing; do not import the placeholder `tasks/sig.tasks.tsk.xml` or `xml/backup.xml` as current controls. All public SIG3 UI operations share a single worker.

Priority 3 adds configured program selection, battery checks, AutoVoice/watch adapters, initialization, and optional noise/sleep program automation. See [setup and event wiring](docs/HeySig3.md#priority-3-setup); automation defaults off and phone profiles require explicit connection.

Restored workflows and event wiring: [HeySig3 completion](docs/HeySig3-completion.md). Start phone volume testing with [slider acceptance](docs/HeySig3-slider-acceptance.md). SoundWear has been removed.

Phone verification updated October 10, 2026: Tasker balance and tinnitus passed **0 → 1 → 0** in Universal using measured Pixel 9a gesture settings. Tinnitus requests stop cleanly when a program has no tinnitus tab, verified in TV. Native accessibility and Tasker's Volume backend still need separate acceptance.

Use the [completed and remaining test checklist](docs/HeySig3-test-checklist.md) to resume testing, and the [phone verification notes](docs/HeySig3-verified-usb-drags.md) for exact evidence. The [Pixel 9a setup task](tasks/SIG3_Pixel9aGestureSetup.tsk.xml) is imported separately from the project and applies only to the measured layout.
