# Selectable sleep settings

Run `SIG3_SleepSettings` to choose a sleep program, wake program, and both clock times. Program choices come from the six configured Signia slots. The time buttons open a 24-hour clock picker; times follow the phone's local clock. The initial time suggestions are 22:00 and 07:00, and neither program is selected automatically.

Save requires both program choices and different sleep/wake times. Cancel, Back, and timeout preserve the existing configuration. Settings are saved together in Tasker's private preferences and reloaded when the settings task opens. A changed program mapping disables sleep automation and requires fresh choices.

Saving leaves sleep automation off. The actual schedule profiles and their asleep/awake routing still need phone verification before enabling switching. SleepState continues to use the existing worker, audio checks, manual override, cancellation and foreground deferral. A schedule cannot unlock a secure phone.

Tasker supports global variables as Time-context inputs; changing a variable reevaluates the context. See [Tasker's Time-context guide](https://tasker.joaoapps.com/userguide/en/timecontext.html). Final profile exports must preserve the phone's tested Time-context configuration.

October 13 implementation status: repository preference tests passed for restart persistence, failed writes, invalid/equal times, invalid slots, duplicate names, and changed mappings. The settings dialog and actual scheduled events remain pending phone acceptance.
