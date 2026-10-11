# HeySig3 voice commands

These phrases are supported by `SIG3_VoiceRouter`. Say them through a connected AutoVoice or AutoWear command event, or pass the text in Parameter 1 of the router. Recognition and event delivery still need phone verification; the command list describes the implemented routing.

Run `SIG3_VoiceCommand` in Tasker to open its built-in voice-recognition prompt for any command below. It sends recognized text directly to `SIG3_VoiceRouter` and does not require an AutoVoice event profile. Cancelled or empty recognition sends no command. The spoken **current program** query passed on the phone; see [voice verification](HeySig3-voice-verification-2026-10-11.md). Other spoken commands still need individual acceptance.

## Everyday controls

| Action | Say | Accepted alternatives / range |
|---|---|---|
| Set hearing-aid volume | “volume ten” | “set volume to 10”, “change volume to ten”; 0–15 |
| Read volume | “current volume” | “what is the volume?”; read-only |
| Mute volume | “mute” | “volume mute”, “mute volume”; sets 0 |
| Maximum volume | “maximum volume” | “volume max”, “volume maximum”; sets 15 |
| Set sound balance | “balance minus three” | “change balance to negative three”, “balance -3”; −8–7 |
| Read balance | “current balance” | “what is the current balance?”; read-only |
| Center balance | “balance zero” | “set balance to 0” |
| Softest balance | “balance soft” | “soft balance”; sets −8 |
| Sharpest balance | “balance sharp” | “sharp balance”; sets 7 |
| Set tinnitus level | “tinnitus one” | “change tinnitus to 1”; 0–15 |
| Read tinnitus | “current tinnitus” | “current tinnitus level”, “what is the tinnitus level?”; read-only when available |
| Mute tinnitus | “tinnitus mute” | “mute tinnitus”; sets 0 |
| Maximum tinnitus | “maximum tinnitus” | “tinnitus max”; sets 15 |
| Select a program | “program two” | “mode 2”, “change program to two”; slots 1–6 |
| Select by program name | “change program to <your program name>” | Use the exact name configured for an actual Signia program slot |
| Read selected program | “current program” | “current mode”, “what program”, “what mode”, “what is the current program?” |
| Check both batteries | “battery check” | “battery”, “check battery”, “battery listen”, “listen to battery” |

Numbers can be digits or English words. Numeric controls accept an optional “set” or “change”, and an optional “to”. Negative balance numbers accept “minus” or “negative”. An optional leading “sig” or “sig3” is removed; it is a command prefix, not an installed wake word.

Program slot 2 also accepts “program too” (or “mode too”) because speech recognition may transcribe “two” as “too”. This alternative applies to program selection.

`SIG3_VoiceCommand` offers **Try again / Cancel** when speech is missed or the phrase is unrecognized. Try again opens a fresh prompt; it does not resend the previous phrase. Cancel, Back, dismissal, or the dialog's 60-second timeout ends the session. A session allows up to 20 attempts, each retry requiring your choice. A phrase that reaches a real command ends the voice session whether that command succeeds or fails; correct any reported phone settings and start a new voice session yourself. Unknown speech clears the previous command-success flag.

The general voice task also speaks a short result after a fresh completed command: the actual selected program, verified volume/balance/tinnitus level, or the failure instruction. Unrecognized speech speaks the retry instruction before showing its buttons. Responses use the default phone text-to-speech engine and media stream, with a two-second settling gap; speech waits until finished before the task continues. They are skipped while the SIG3 worker is active. This gap is not a measured confirmation of hearing-aid acoustic completion.

Set `%SIG3_VoiceResponses=0` to disable spoken responses; an unset value or `1` enables them. Speech does not change phone volume or DND, and on-screen results remain available when those settings prevent hearing the message. AutoVoice/watch event adapters and the separate mode/battery prompts do not yet use this general-task speech path.

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

For a read-only phone audio check, run `SIG3_PhoneAudioCheck` in Tasker. There is currently no voice phrase for that task or the page-only battery `open` option.

Successful results show the app state; they do not independently verify hearing-aid receipt. See the [user manual](HeySig3.md) for setup and the [test checklist](HeySig3-test-checklist.md) for remaining verification.
