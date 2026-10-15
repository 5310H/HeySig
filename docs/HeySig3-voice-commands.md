# HeySig3 voice commands

These phrases are supported by `SIG3_VoiceRouter`. Say them through a connected AutoVoice or AutoWear command event, or pass the text in Parameter 1 of the router. General phone voice commands have live acceptance; watch events remain untested because no watch was available. The list describes supported routing, including endpoints with separate live acceptance still pending.

Run `SIG3_VoiceCommand` in Tasker to open its built-in voice-recognition prompt for any command below. It sends recognized text directly to `SIG3_VoiceRouter` and does not require an AutoVoice event profile. Cancelled or empty recognition sends no command. The spoken **current program** query passed on the phone; see [voice verification](HeySig3-voice-verification-2026-10-11.md). Live program, volume, balance, tinnitus and battery commands also passed; see the [test checklist](HeySig3-test-checklist.md).

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
| Set tinnitus level | “tin one” | “tinnitus one”, “change tin to 1”; 0–15 when available |
| Read tinnitus | “current tin” | “current tinnitus”, “current tinnitus level”, “what is the tinnitus level?”; read-only when available |
| Mute tinnitus | “tin mute” | “tinnitus mute”, “mute tinnitus”; sets 0 |
| Maximum tinnitus | “maximum tinnitus” | “tinnitus max”; sets 15 |
| Select a program | “program two” | “mode 2”, “change program to two”; slots 1–6 |
| Select by program name | “change program to <your program name>” | Use the exact name configured for an actual Signia program slot |
| Read selected program | “current program” | “current mode”, “what program”, “what mode”, “what is the current program?” |
| Restore last saved settings | “restore settings” | Restores saved program, volume, balance and tinnitus when available |
| Refresh saved settings | “save settings” | Optional; successful HeySig3 changes save automatically |
| End microphone session | “cancel” | No command sent; no retry dialog |
| Check both batteries | “battery check” | “battery”, “check battery”, “battery listen”, “listen to battery” |

Supported phrases accept one trailing period, exclamation mark, or question mark from speech recognition (for example, “volume ten.”). Exact configured program names retain their own punctuation. Repeated punctuation and extra words remain unsupported. The updated router and mode task were installed October 15. A typed on-phone “current program.” request passed from Signia Controls and read Universal; the program-picker page failed conservatively until closed. See [phone result](evidence/HeySig3-voice-punctuation-2026-10-15.json). The user then confirmed that the live SIG3_VoiceCommand “current program” test worked. This accepts microphone capture and the spoken query flow after installation; it does not establish that recognition emitted trailing punctuation or certify every command family.

Numbers can be digits or English words. Numeric controls accept an optional “set” or “change”, and an optional “to”. Negative balance numbers accept “minus” or “negative”. An optional leading “sig” or “sig3” is removed; it is a command prefix, not an installed wake word.

Program slot 2 also accepts “program too” (or “mode too”) because speech recognition may transcribe “two” as “too”. This alternative applies to program selection.

`SIG3_VoiceCommand` offers **Try again / Cancel** when recognized text contains an unsupported phrase. Empty recognition ends quietly without speech or a retry dialog: native Get Voice returned empty error fields for Back cancellation, so silence/timeout producing the same empty result also ends quietly. Try again opens a fresh prompt; it does not resend the previous phrase. Cancel, Back, dismissal, or the dialog's 60-second timeout ends the session. A session allows up to 20 attempts, each retry requiring your choice. A phrase that reaches a real command ends the voice session whether that command succeeds or fails; correct any reported phone settings and start a new voice session yourself. Unknown speech clears the previous command-success flag.

The general voice task also speaks a short result after a fresh completed command: the actual selected program, verified volume/balance/tinnitus level, or the failure instruction. Unrecognized speech speaks the retry instruction before showing its buttons. Responses use the default phone text-to-speech engine and media stream, with a two-second settling gap; speech waits until finished before the task continues. They are skipped while the SIG3 worker is active. This gap is not a measured confirmation of hearing-aid acoustic completion.

Run **SIG3_VoiceSettings** to independently switch **Spoken results** and **Voice prompts** on/off and Save. Both may be off. Cancel/Back preserves choices. These switches do not control wake listening. See [voice settings](HeySig3-voice-settings.md). Result speech does not change phone volume or DND, and on-screen results remain available when those settings prevent hearing the message. AutoVoice/watch event adapters and the separate mode/battery prompts do not yet use this general-task speech path.

Program names are **not hardcoded**. Configure `%SIG3_ProgramName1` through `%SIG3_ProgramName6` from the names actually shown in Signia; leave unused slots unset. Numbered requests also require a configured slot. “normal” and “conversation” use `%SIG3_ModeConversationProgram`; “noisy” uses `%SIG3_ModeNoisyProgram`; “very noisy”, “verynoisy”, and “vnoisy” use `%SIG3_ModeVeryNoisyProgram`. These aliases also accept a “program” or “mode” prefix and require an explicitly configured slot.

Use **tin** as a shorthand for tinnitus in control phrases. Tinnitus commands use the program icon first; when it identifies unavailable tinnitus, they stop without looking for a tab. Unknown icons use visible-tab fallback. Repeating the current target reads it again and makes no movement. Out-of-range targets fail. Relative voice phrases such as “volume up” and “tinnitus down” are not supported by this router.

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

Keep the phone unlocked, Tasker accessibility enabled, and Signia ready. If Do Not Disturb is on or the selected phone audio stream is too low, HeySig3 stops and tells you what to change. Spoken warnings are shortened to “Turn off Do Not Disturb” or “Raise phone media volume to halfway” for the default 50% media minimum; full error details remain on screen. Turn DND off or raise volume with the phone slider, then retry. HeySig3 does not change those settings automatically. The default minimum is 50% (13/25 on the tested phone).

For a read-only phone audio check, run `SIG3_PhoneAudioCheck` in Tasker. There is currently no voice phrase for that task or the page-only battery `open` option.

Successful results show the app state; they do not independently verify hearing-aid receipt. See the [user manual](HeySig3.md) for setup and the [test checklist](HeySig3-test-checklist.md) for remaining verification.

## Optional wake phrase

Run `SIG3_WakeEnable`, say **Hey Sig**, pause until the cue and microphone, then say one command. **Hey Cig** is an accepted recognition alias. To turn listening off, run `SIG3_WakeDisable`. AutoVoice requires regex on/exact command off and Stream to Mute set to Media. Two consecutive commands and locked-phone unlock guidance passed; background wake still failed. Use `SIG3_VoiceCommand` for direct capture. See [wake setup](HeySig3-wake-phrase.md).

## October 15 user voice checks

After installing the punctuation update, the user reported that “current volume”, “current balance”, and “current tin” worked through SIG3_VoiceCommand, following the earlier successful “current program” check. This is user-reported live acceptance of these spoken read-only queries; no numeric values or recognition transcripts were collected.

## Pixel Watch 3 setup: October 15

AutoWear 3.2.20 on the phone detects the Pixel Watch 3, now explicitly selected. A Tasker AutoWear Command event with filter `sig3` is linked to SIG3_WatchCommand. The saved AutoWear Voice Screen is named `ScreenHeySigVoice`, with prefix `sig3 ` and Trigger Event enabled. The user initially reported no response.

The watch adapter now accepts the AutoApps `sig3=:=` envelope and whitespace prefixes, and uses the existing phone spoken-result path with saved speech preferences. Spoken cancellation skips replies. Seven actual Java input cases, migration/parity, voice retry, punctuation and 22 spoken-result checks passed; XML validation found zero failures. An installed-adapter typed `sig3=:=current program.` test read Universal successfully; see [adapter result](evidence/HeySig3-watch-adapter-2026-10-15.json). This is not yet end-to-end watch microphone/event acceptance. Replies are through the phone, not watch TTS.

### Live watch result

On October 15, after enabling watch logs and resending the saved voice screen with AutoWear open, the user reported that the watch “current program” test worked. This is user-reported live acceptance of that query only; no recognition transcript or fresh event capture accompanied the confirmation. The phone profile currently uses the temporary case-insensitive `current program` filter, not the earlier `sig3` filter. Other watch commands and independent reopening of the voice screen remain unaccepted. Watch logging was enabled for diagnosis; replies are configured through phone TTS, not watch TTS.

### Independent watch launcher configured

October 15: changed ScreenHeySigVoice Command to show from `&APPOPENED&` to `heysig_listen`. Created floating icon `HeySigMic` with visible text `HeySig` and Tap command `heysig_listen`; AutoWear reported successful creation on the selected watch. Restored the Tasker AutoWear Command filter to `sig3` with case-insensitive matching, replacing the diagnostic current-program filter. Independent button visibility, tap-to-microphone behavior and another command under this restored filter require user acceptance. The user confirmed command/voice response, but clarified that setup prompts were absent. No setup-wizard prompts are claimed.

### Watch button appearance

The user could not see the original floating button. Its saved settings had no image and a 50×50-pixel size. Assigned an image and increased Width/Height to 96 pixels, retaining the centered 50% Left/Top position. At the user’s request, the final image is the white ear on blue circle in `.icn/heysig-ear.png`, copied to `/sdcard/Download/heysig-ear.png` and selected in AutoWear. AutoWear reported the floating icon updated successfully. Actual watch visibility and tap acceptance remain pending.

### Dedicated HeySig tile

The user reported that the overlay was absent and tapping the watch face opened weather. Configured a separate AutoWear tile named `HeySigTile`, targeting `AutoWear Tile 1` with Buttons layout, HeySig text/top label, button command `heysig_listen`, and `/sdcard/Download/heysig-ear.png` as its button image. AutoWear reported “Tile Created on your watch”. The user must add AutoWear Tile 1 to the watch tile carousel; tile appearance, image loading and tap-to-voice behavior remain unverified. No success on the watch display is inferred from the phone confirmation.

Final saved-value verification: the voice screen initially still retained `&APPOPENED&`; replaced its editable field explicitly and confirmed the saved summary now reads `Command to show: heysig_listen`. The tile summary independently confirms AutoWear Tile 1, Buttons layout, HeySig labels, `Commands: heysig_listen` and the ear image path. Earlier overlay edits had appended values (image paths concatenated and dimensions 5096); the overlay was hidden and is superseded by the tile. Do not treat its earlier update confirmation as valid appearance acceptance.

User confirmed the dedicated tile opened voice input and the command worked, but saw only a circle in place of the ear. Replaced the button image with native `👂` text, retaining the HeySig heading and `heysig_listen` command. Removed the residual image-path field explicitly and verified it empty before saving. Watch rendering of the symbol still needs confirmation.

## Recreate the current Pixel Watch 3 setup

1. In phone AutoWear, select the paired Pixel Watch 3. On the watch, allow AutoWear to display over other apps and provide microphone access when requested.
2. Create a Voice Screen named `HeySigVoice` (saved as `ScreenHeySigVoice`), with Command to show `heysig_listen`, Command Prefix `sig3 `, and Trigger Events enabled.
3. In Tasker, create an AutoWear Command event with filter `sig3`, Case Insensitive on and Exact off. Link it to the public `SIG3_WatchCommand` task and apply the profile. This live event configuration is manual; it is not bundled into the generated project export.
4. Create AutoWear Tiles settings named `HeySigTile`, targeting AutoWear Tile 1 with Buttons layout. Set Texts to `👂`, Top Label to `HeySig`, Commands to `heysig_listen`, and leave Button Icons empty. Apply to the watch.
5. Add AutoWear Tile 1 to the watch carousel. Tap its ear button and speak a supported command. The user confirmed independent tile capture and a command response before the final ear-symbol appearance change. Replies use phone TTS and the saved Spoken results preference. Setup prompts and watch-speaker replies are not implemented by this setup.

For Signia control, the phone still needs the existing unlock, accessibility and audio requirements. The tile does not bypass those guards. Temporary diagnostic tasks and the unused hidden overlay are not part of the release exports.
