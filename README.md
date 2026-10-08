# Signia-Tasker-Control
Numeric voice controls on branch HeySid3: see [HeySig3 setup and calibration](docs/HeySig3.md) and import [the separate project](projects/HeySig3.prj.xml). Original HeySig exports are preserved.

Supported numeric-control import: HeySig3 only. Disable old slider-triggering profiles during testing; do not import the placeholder `tasks/sig.tasks.tsk.xml` or `xml/backup.xml` as current controls. All public SIG3 UI operations share a single worker.

Priority 3 adds configured program selection, battery checks, AutoVoice/watch adapters, initialization, and optional noise/sleep program automation. See [setup and event wiring](docs/HeySig3.md#priority-3-setup); automation defaults off and phone profiles require explicit connection.
