# TV unavailable-control acceptance — October 11, 2026

Checklist item 5 passed in a guarded 18-request phone run with fresh operation IDs and independent app readback. Starting Universal values were Volume 9, Balance 0 and Tinnitus 0. The test selected the configured TV slot, captured Volume 8 and Balance 0, and restored Universal with all three starting values unchanged.

TinnitusCurrent, Set 1, Mute, Max and Inspect each returned CommandOK=0 and `Tinnitus unavailable for this program`. Every blocked request preserved TV, Selected Sound Sharpness Tab and displayed 0. Gesture remained empty; TouchStage and ProgressAccepted remained `not run`. The availability helper reads the active program's U+E909 icon and returns immediately without searching for a tinnitus tab. The acceptance caller also used the actual icon, without a tinnitus-tab search.

Public VolumeCurrent and BalanceCurrent succeeded both before and after the five blocked requests. Subsequent ProgramSwitch restoration and all three Current reads succeeded with CommandOK=1, empty Error and complete stage. No slider values were written.

Earlier runs exposed unreliable selection at the center of the outer Volume tab. Selecting the visible Volume label's dynamically resolved center passed the complete sequence. Production selection verifies the requested selected-tab description before numeric readback; the coordinates come from live bounds, not constants. TV's observed label center was (278, 2255).

Evidence: `/tmp/sig3-tv-label-final.json`, validated by `/tmp/sig3_validate_tv.py`. The separate Volume/Balance-only run also passed all four Current/Inspect checks with unchanged TV values 8 and 0: `/tmp/sig3-tv-only-resume.json`.
