# Selectable sleep settings

October 14: [Pixel acceptance passed](HeySig3-sleep-acceptance-2026-10-14.md) for selectable settings and clock-triggered sleep/wake programs with Signia open. Automation is left off with test choices cleared.

Run `SIG3_SleepSettings` to choose a sleep program, wake program, and both clock times. Program choices come from the six configured Signia slots. The time buttons open a 24-hour clock picker; times follow the phone's local clock. The initial time suggestions are 22:00 and 07:00, and neither program is selected automatically.

Save requires both program choices and different sleep/wake times. Cancel, Back, and timeout preserve the existing configuration. Settings are saved together in Tasker's private preferences and reloaded when the settings task opens. A changed program mapping disables sleep automation and requires fresh choices.

Saving leaves sleep automation off. Run `SIG3_SleepEnable` to arm the installed sleep/wake schedules, or `SIG3_SleepDisable` to stop future events. SleepState continues to use the existing worker, audio checks, manual override, cancellation and foreground deferral. A schedule cannot unlock a secure phone.

Tasker supports global variables as Time-context inputs; changing a variable reevaluates the context. See [Tasker's Time-context guide](https://tasker.joaoapps.com/userguide/en/timecontext.html). Final profile exports must preserve the phone's tested Time-context configuration.

October 13 historical implementation status: repository preference tests passed for restart persistence, failed writes, invalid/equal times, invalid slots, duplicate names, and changed mappings. The settings dialog and actual scheduled events remain pending phone acceptance.

October 14 schedule implementation: `SIG3_SleepSchedule` and `SIG3_WakeSchedule` use the corresponding global variable for both From and To, making each an instant event. `SIG3_ScheduledSleep` / `SIG3_ScheduledWake` reload and validate persisted choices, then submit explicit `asleep` / `awake` requests to the existing worker. Disabled schedules do not submit commands. Unchanged preference reloads do not rewrite time variables. Missing configuration, changed mappings, and load errors disable automation. Save and `SIG3_SleepDisable` also clear the sleep-active noise-suppression state.

Run `SIG3_SleepEnable` after saving choices to arm future scheduled events; it does not immediately select a program. Run `SIG3_SleepDisable` to stop future events. Scheduled switching retains the existing manual-override, cancellation, foreground and audio checks. A missed or deferred clock event is not retried automatically.

The project export includes both profiles and their entry tasks. Separate profile exports are in `profiles/`; their entry tasks still require the rest of HeySig3. Tasker imports a profile as a new entry, so delete its previous copy before updating a standalone profile export. Keep exactly one copy of each schedule. Updating a task by name replaces its existing body.
