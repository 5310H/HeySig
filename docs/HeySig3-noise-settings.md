# Selectable phone noise settings

Run **SIG3_NoiseSettings** to choose the programs for Quiet, Noisy and Very noisy. Choices come from your configured Signia program names. Saving leaves sampling and automatic switching off. Cancel, Back and dialog timeout leave saved choices unchanged.

The phone readings are a **noise index**, not calibrated environmental decibels. On the tested Pixel, quiet-room readings were −66 to −63; conversation/TV readings were mostly −54 to −49, with one quiet-range reading. Higher, less-negative readings indicate more sound in that comparison. No final very-noisy threshold has been established.

Enter the two boundaries in those measured index units. The quiet/noisy boundary must be below the noisy/very-noisy boundary. The hysteresis margin creates different entry and exit boundaries to avoid repeated changes near a cutoff; twice the margin must be smaller than the gap between boundaries. The default margin is 3, confirmation is three consecutive samples, and cooldown is 60 seconds. These are editable tuning choices, not calibrated acoustic limits. Check the direction-confirmation box after comparing real measurements.

Use **SIG3_CurrentNoise** for individual raw samples before choosing boundaries. Start with **SIG3_NoiseObserve** once choices are saved. It samples for five seconds, waits ten seconds, and repeats, showing the proposed role and program without sending program commands. Use **SIG3_NoiseStop** to stop observation or automatic selection.

After observing stable choices in the intended environments, **SIG3_NoiseAuto** starts the same sampling loop with switching enabled. Signia must be foreground and the phone unlocked; existing DND, media-volume and audio-route checks still apply. The phone does not change those audio settings automatically. A deferred or failed attempt clears its pending confirmation; it needs fresh qualifying samples before another attempt. The cooldown starts only after successful program readback, and an already-selected program does not extend it.

A successful manual program selection pauses noise changes using Manual Override. Run **SIG3_Override** with Parameter 1 = **0** to resume after your manual choice, or keep it paused with **1**. Cancellation/resume clear pending observations too. Sleep suppresses noise changes. Sampling skips periods when the shared worker, voice prompt or continuous Hey Sig listener owns the relevant resources; keep continuous listening off during noise observation. No competing automatic profile is installed.

Settings are saved together, including their program-name mapping. A changed mapping or invalid saved configuration stops sampling and requires renewed setup. Saving different choices clears previous observations. After Tasker/phone restart, reopen settings and explicitly start observation; automatic startup after reboot has not been accepted. An existing polling task prevents a second start. Stopping takes effect after the current capture and wait finish.

The verified source for this setup is the phone. The existing watch-input adapter remains separate; no watch microphone measurement is implemented by these settings. Full background endurance, microphone contention and acoustic receipt remain outside the bounded phone checks. Only battery checks provide an audible aid response.
