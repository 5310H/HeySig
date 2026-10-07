# Balance and tinnitus slider fixes

The user confirmed Balance −8–7 and Tinnitus 0–15. Each task family now uses its own level and success variables: `%SIG_BalanceLevel` / `%SIG_BalanceOK` and `%SIG_TinnitusLevel` / `%SIG_TinnitusOK`. Set uses the matching target variable.

Current selects the matching tab and queries accessibility text without clicking candidate numbers. It accepts exactly one in-range numeric value and leaves a failure sentinel below the minimum if no unambiguous value is found. Up/Down reads fresh state, checks its own endpoints, taps the displayed value, splits the returned coordinates, and then drags. The premature Stop and screen-percentage track calculation are removed.

Each movement is verified by querying the displayed value. Unchanged results retry with increasing vertical distances of 8–160 pixels, at most 20 attempts. A change other than exactly one level stops with failure; an overshoot is reported and not reversed. Set shares a direction-selected loop, clamps to the confirmed range, rejects nonintegers, and stops on helper failure. Sharp/Soft and Max/Mute call their matching Set task. All exits honor `keep_open`, and no-op Set reports success.

All twelve standalone exports match the HeySig project export. Import the project or update all six tasks in each affected family together. Consumers of the old shared `%SIG_Level` must use the corresponding family level variable.

Validation: `python3 tests/check_sliders.py`, `python3 tests/check_balance_routing.py`, and `python3 tests/check_volume.py`. Slider simulations cover all 512 Set transitions across the two ranges, single-step endpoints, extreme targets, invalid input, unavailable readings, unchanged gestures, overshoots, independent state, and keep_open behavior.

Device verification remains necessary. The gestures retain the existing assumption that upward increases the value. Exact English tab labels, numeric accessibility identity, coordinates, plugin behavior, and connection state have not been verified on Android. Start near the middle and confirm Current leaves the control unchanged, Up moves one level, Down restores it, and Set works in both directions. Test unavailable tinnitus, negative balance, endpoints, and keep_open. If upward decreases either control or a swipe skips levels, record the UI behavior before changing gesture mapping. Passing simulations does not establish installed-app compatibility.

For the current import requirements, shared helpers, and additional routing/error changes, see [signia-control-refactor.md](signia-control-refactor.md).
