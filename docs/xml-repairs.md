# XML validation repairs

The reported Signia static findings are resolved. `python3 tests/validate_tasker_xml.py` checks all repository XML files with zero static failures. The unrelated legacy configuration was removed at the user's request. This remains a partial static validator, not Tasker's runtime parser.

- `tasks/sig.tasks.tsk.xml`: unsupported code 6 entries became explicit If/Else/Perform Task/Stop sequences. Empty variable declarations were removed rather than assigning guessed input values. Mode setters now have complete Variable Set arguments. Numeric thresholds route once, from highest priority to lowest; override exits immediately. Override Toggle initializes an invalid/unset value and toggles 0/1. The unfinished ApplyEQ task explicitly reports that no EQ actions are configured.
- The supplemental dispatcher is named `SIG_StateDispatcher` so it cannot overwrite `SIG_Dispatcher`. Supplemental IDs are 33–44, distinct from the main project. Existing callers of the supplemental state dispatcher must use its new name. These tasks consume upstream noise/state/voice/watch variables; they are not a replacement for the main controller and its Signia UI tasks.
- `xml/Sig_init.tsk.xml`: task ID 45, numbered actions and argument slots, and complete Variable Set arguments. Existing initialization values are preserved.
- `tasks/SIG_NoiseMonitor.tsk.xml`: unsupported task calls became Perform Task actions. Replaced regex threshold checks with numeric comparisons, repaired conditional branches, enabled counter arithmetic, checked failed/invalid noise samples, and increased the plugin timeout beyond its five-second listening period. High/low thresholds include equality; counters reset after a confirmed program switch.

`python3 tests/check_xml_repairs.py` verifies state dispatch, threshold precedence, override stop/toggle, and noisy/normal three-strike program selection in simulation. Run the other `check_*.py` scripts for control/routing regressions.

Changes are local. They have not been pushed to GitHub, and phone-side Tasker/AutoInput/Signia execution is still unverified.
