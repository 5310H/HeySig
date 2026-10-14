# Phone noise sampling — October 14, 2026

The Pixel 9a's AutoVoice Current Noise sampler now passes through HeySig's normal worker. Five samples in the user-confirmed quiet room returned **−64, −63, −66, −65 and −65**, all with CommandOK=1 and no error. These are uncalibrated noise indices, not established environmental dB SPL or dBA.

Five subsequent samples with user-provided conversation/TV returned **−49, −53, −54, −65 and −53**, also all successful. Most readings increased toward zero with more sound; one overlapped the quiet range. This preliminary comparison supports preserving the raw sign rather than negating it, but does not establish calibrated units or final thresholds. Consecutive confirmation and stability checks remain necessary.

The original action requested five seconds of listening but set its plugin timeout to one second. A direct phone diagnostic displayed `Plugin did not respond before timing out`. The generator now gives the capture fifteen seconds to finish and return its result. The generated project and individual helper agree. The corrected direct diagnostic returned −56 with no error; the subsequent five public-worker samples above verify the complete capture/processing path.

The observation trial temporarily disabled automatic switching and selected the phone source, then restored its previous enabled/source settings. It sent no hearing-aid commands and did not record audio files. Numeric results are preserved in [the evidence JSON](evidence/HeySig3-phone-noise-2026-10-14.json). Diagnostic tasks on the phone are named `SIG3_NoiseObservationTrial` and `00_SIG3_NoisePluginTrial`; neither has a polling profile.

Tasker variable inspection after the quiet trial showed enabled/source unset, as restored by the trial; the defaults are disabled and phone. The same restoration actions finish the conversation/TV trial.

Generation checks now assert that the timeout exceeds the listening window with response overhead. Generation, parity, migration, worker coordination, numeric controls, audio guards, reporting and XML validation passed; XML validation checked 96 files and 6,871 actions with no failures.

Still pending: sustained and louder comparisons, measurement definition, selectable role configuration, polling, thresholds and stability, manual priority, foreground deferral and live program-switch acceptance. These short observation runs do not establish switching thresholds. Automation remains outside acceptance until those checks pass.
