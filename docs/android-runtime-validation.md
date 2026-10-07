# Android runtime validation status — 2026-10-06

ADB reached `emulator-5554` after it became available. Read-only device inspection confirmed:

| Dependency | Installed version | Result |
| --- | --- | --- |
| Tasker | 6.6.20 | Installed; matches control XML version metadata |
| AutoInput | 3.0.12 | Installed; accessibility service `ServiceAccessibilityV2` enabled |
| AutoVoice | 4.0.14 | Installed |
| Signia (`com.signia.rta`) | Not installed | Blocks Signia runtime tests |

All plugin configuration activities referenced by repository task actions appear in the installed package resolver information: AutoInput `ActivityConfigActionv2`, `ActivityConfigUIQuery`, `ActivityConfigGestures`, and AutoVoice `ActivityConfigGetCurrentAmbientNoise`.

This confirms dependency presence and component names, not execution of XML bundles. No task was loaded or executed, no plugin query/click/swipe was invoked, and no hearing-aid setting was changed. Runtime results and compatibility with Signia 2.8.0.18214 remain unverified.

To complete validation, use the planned GitHub-to-phone workflow with Signia installed and the current repository tasks available to Tasker. Begin with Current on each control and capture its AutoInput output/error. Then verify single-step Up/Down, Set in both directions, endpoints, keep_open, unavailable tinnitus, and configured program names. Tasker run logs and observed Signia values must agree before marking runtime validation passed. The reported XML failures have since been repaired; see `xml-repairs.md` and the refreshed static validation report.
