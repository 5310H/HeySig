# HeySig3 voice commands

These phrases are supported by `SIG3_VoiceRouter`. Say them through a connected AutoVoice or AutoWear command event, or pass the text in Parameter 1 of the router. Recognition and event delivery still need phone verification; the command list describes the implemented routing.

## Everyday controls

| Action | Say | Accepted alternatives / range |
|---|---|---|
| Set hearing-aid volume | “volume ten” | “set volume to 10”, “change volume to ten”; 0–15 |
| Mute volume | “mute” | “volume mute”, “mute volume”; sets 0 |
| Maximum volume | “maximum volume” | “volume max”, “volume maximum”; sets 15 |
| Set sound balance | “balance minus three” | “change balance to negative three”, “balance -3”; −8–7 |
| Center balance | “balance zero” | “set balance to 0” |
| Softest balance | “balance soft” | “soft balance”; sets −8 |
| Sharpest balance | “balance sharp” | “sharp balance”; sets 7 |
| Set tinnitus level | “tinnitus one” | “change tinnitus to 1”; 0–15 |
| Mute tinnitus | “tinnitus mute” | “mute tinnitus”; sets 0 |
| Maximum tinnitus | “maximum tinnitus” | “tinnitus max”; sets 15 |
| Select a program | “program two” | “mode 2”, “change program to two”; slots 1–6 |
| Select by program name | “change program to <your program name>” | Use the exact name configured for an actual Signia program slot |
| Read selected program | “current program” | “current mode”, “what program”, “what mode”, “what is the current program?” |
| Check both batteries | “battery check” | “battery”, “check battery”, “battery listen”, “listen to battery” |

Numbers can be digits or English words. Numeric controls accept an optional “set” or “change”, and an optional “to”. Negative balance numbers accept “minus” or “negative”. An optional leading “sig” or “sig3” is removed; it is a command prefix, not an installed wake word.

Program names are **not hardcoded**. Configure `%SIG3_ProgramName1` through `%SIG3_ProgramName6` from the names actually shown in Signia; leave unused slots unset. Numbered requests also require a configured slot. “normal” and “conversation” use `%SIG3_ModeConversationProgram`; “noisy” uses `%SIG3_ModeNoisyProgram`; “very noisy”, “verynoisy”, and “vnoisy” use `%SIG3_ModeVeryNoisyProgram`. These aliases also accept a “program” or “mode” prefix and require an explicitly configured slot.

Tinnitus commands stop when the current program has no tinnitus tab. Repeating the current target reads it again and makes no movement. Out-of-range targets fail. Relative voice phrases such as “volume up” and “tinnitus down” are not supported by this router.

Battery check presses the top-right question-mark battery icon, requests left and right checks, acknowledges the prompts, then closes the battery page. Battery has no slider. The phone screen confirms the app sequence; hearing-aid indications require listening.

## Optional automation controls

| Action | Say | Behavior |
|---|---|---|
| Enable manual override | “override on” | “manual mode”; blocks automatic noise/sleep program changes |
| Release manual override | “override off” | “automatic mode”; releases the block but does not enable automation |
| Toggle override | “override toggle” | Toggles the current manual override |
| Sample noise | “noise sample” | “check noise”; plugin capture requires phone verification |
| Apply configured sleep program | “sleep” | Requires enabled sleep automation and configured program slots |
| Apply configured wake program | “wake” | “awake”; same setup requirements |

Noise and sleep automation default off. “sleep” selects the configured program; it does not infer sleep or promise muted microphones.

## Phone setup and results

Keep the phone unlocked, Tasker accessibility enabled, and Signia ready. If Do Not Disturb is on or the selected phone audio stream is too low, HeySig3 stops and tells you what to change. Turn DND off or raise volume with the phone slider, then retry. HeySig3 does not change those settings automatically. The default minimum is 50% (13/25 on the tested phone).

For a read-only phone audio check, run `SIG3_PhoneAudioCheck` in Tasker. There is currently no voice phrase for that task, slider current-value queries, or the page-only battery `open` option.

Successful results show the app state; they do not independently verify hearing-aid receipt. See the [user manual](HeySig3.md) for setup and the [test checklist](HeySig3-test-checklist.md) for remaining verification.
