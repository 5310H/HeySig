# Selectable noise settings: October 14 acceptance

Implemented selectable Quiet/Noisy/Very noisy roles, editable noise-index boundaries, hysteresis, consecutive confirmation, cooldown, observation mode, guarded polling and manual-program priority. The [setup guide](HeySig3-noise-settings.md) describes the controls.

## Phone checks that passed

- The Pixel 9a opened the settings dialog with all three program selectors and tuning fields.
- Temporary role selections and boundaries saved successfully. Direction confirmation and a 60-second cooldown were stored; Save left switching disabled.
- A timed-out earlier dialog left saved configuration empty.
- Observation-only processing proposed the configured Very noisy role after three synthetic samples, without dispatching a program selection.
- Restoration cleared the temporary configuration and restored all previous noise settings. Fresh Program/Volume/Balance/Tinnitus reads matched the starting Universal / 10 / 0 / 0. The exact private saved-settings record matched its starting SHA-256.

The test boundaries −60/−40 were temporary synthetic-test choices. They are not final real-world thresholds.

## Repository checks

The actual BeanShell decision and persistence helpers passed hysteresis, direct role jumps, invalid/gapped/source-changed samples, override/cancel/sleep suppression, cooldown, successful/no-op/failed completion, atomic save, restart reload and changed program mapping. All four helpers parsed with BeanShell.

The 26-script regression run found an outdated routing allowlist. That check was corrected to permit the new polling wrappers to call the public noise command; it then passed. The remaining scripts passed, with updated cancellation/resume parity retested separately. Final XML validation checked 101 files and 7,109 actions, with zero failures.

## Still pending

The final controlled automatic-switch trial stopped on a harness assertion: observation state had carried into its deferral phase, and later collecting requests overwrote the final result the assertion expected. An external generic Signia launch intent also failed; the existing Tasker launcher and restoration worked. Neither event is claimed as successful automatic-switch acceptance.

Controlled automatic switching, manual priority in that live path, real polling/resource contention, final environment thresholds and background endurance still need phone acceptance. Automatic selection is left off, with test choices cleared. No watch sampler or acoustic acknowledgement requirement was added.

[Evidence JSON](evidence/HeySig3-noise-settings-2026-10-14.json) records the selected phone results and restoration proof; the proprietary/private saved record itself is not included.
