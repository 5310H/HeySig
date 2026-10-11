# TV unavailable-control test attempt — October 11, 2026

Checklist item 5 remains unchecked. The guarded public-entrypoint test stopped during its starting-state capture, before selecting TV or sending any tinnitus Set, Mute, Max or Inspect request.

Fresh ProgramCurrent succeeded: CommandOK=1, stage=complete, Error empty, and the independent active header read Universal. Configured slots read directly from Tasker were Universal, Off just Tinnitus, Noisy, Outdoor, TV and Very Noisy (slots 1–6).

The subsequent public VolumeCurrent failed with CommandOK=0, stage=start, and `Knob selector matched zero or multiple numeric elements; inspect aligned UI Query data`. Its operation ID was fresh. Gesture was empty; TouchStage and ProgressAccepted were `not run`. Independent accessibility readback still showed Universal, Selected Sound Sharpness Tab and balance −3. This failure occurred with Balance selected; the installed volume path did not leave the app displaying Volume. The cause needs investigation before rerunning this sequence.

The test stopped on the unexpected result as required by the checklist. No program switch or slider gesture was sent. The temporary test task and its phone-side diagnostic files were removed after saving evidence locally at `/tmp/HeySig3-tv-unavailable-20261011.json`. Production tasks were unchanged.

Next: investigate the public VolumeCurrent failure from a different selected tab, then resume the TV unavailable-control test with fresh starting-state capture.
