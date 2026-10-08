# Signia Android API and Tasker integration findings

Analysis date: **2026-10-07 (America/New_York)**. Package: **`com.signia.rta`**. Examined version: **2.8.0.18214**, version code **1821400000**, ARM64 bundle.

This is an **unofficial static analysis document**, not a supported Signia API specification. It describes the downloaded build; the phone's installed version and its runtime behavior were not verified. No app was installed or launched, no authentication was bypassed, no secrets were sought, and no Bluetooth commands or acoustic waveforms were generated or transmitted. Existing Tasker exports and code were not changed.

## Result

**The most viable integration under the stated constraints is Tasker 6.6.20 Java Code using Tasker's enabled accessibility service to perform one continuous thumb drag, followed by volume readback.** Code confirms that touch must begin on the thumb and that normal command execution occurs when tracking stops. No external microphone-volume intent, exported command service, or volume deep link was found in the inspected entry points.

`ACTION_SET_PROGRESS` is a conditional alternative, not an established reliable replacement: the underlying widget is a real Android `SeekBar`, but progress changes alone do not normally call the stop-tracking command. Signia's alternative commit path requires **both accessibility enabled and touch exploration enabled**. Enabling Tasker's accessibility service alone does not establish that condition.

## APK provenance and authenticity

- Public download source: [APKPure Signia download page](https://apkpure.net/signia-app/com.signia.rta/download).
- Retrieval endpoint: `https://d.apkpure.net/b/XAPK/com.signia.rta?version=latest`, downloaded October 7, 2026. It redirected to the public `data.winudf.com` CDN, with filename `Signia App_2.8.0.18214_APKPure.xapk`. The mutable `latest` endpoint is not a reproducible version pin; use the recorded hashes to identify this artifact.
- Contents: `com.signia.rta.apk`, `config.arm64_v8a.apk`, `config.en.apk`, `config.hdpi.apk`, and `manifest.json`.
- Package and version agree between the decoded Android manifest/resource metadata and bundle metadata. Minimum SDK **29**, target SDK **36**.
- `apksigner verify --verbose --print-certs` verifies the base APK using **APK Signature Scheme v3**. All four APKs independently pass signature verification and carry the same signing certificate.
- Signer subject: `CN=Code Signing Sivantos GmbH, OU=Unknown, O=Sivantos GmbH, L=Erlangen, ST=Bavaria, C=DE`; RSA, 2048 bits.
- Certificate SHA-256: `9b2eb7ce3b3b2cee3fe7b06d2d40da8ffae9c772d135eb887bd321cfe7be21ce`.
- Certificate SHA-1: `c24a9888aef54ce2070234e9763bfb59d2a4dab6`.
- This exactly matches [APKMirror's independently published Signia certificate fingerprint](https://www.apkmirror.com/apk/sivantos-pte-ltd/signia-app/signia-app-2-7-50-18047-release/signia-app-2-7-50-18047-android-apk-download/). The [official Google Play listing](https://play.google.com/store/apps/details?id=com.signia.rta) confirms the product/package. Together these establish package identity, valid signatures, and signer continuity with distributed Signia releases. The APK was obtained from a mirror, not directly from Google Play.
- Source-stamp metadata names Google; the verifier reports `Verified for SourceStamp: false` and an unknown stamp attribute. **No claim of verified Google source-stamp provenance is made.** This does not negate the separately successful APK signer verification.

| Artifact | SHA-256 |
|---|---|
| XAPK bundle | `c7c9157a2845ae3a55fee062cf394fe64e9f1792d02a942995807843deb59f70` |
| Base APK | `983d9cb4a999de61753d22d568644865b015dee9e0d91c83f0b49123f326bd88` |
| ARM64 split | `a3bcec0ba14a32b66b28c41c74812e168687bd17ed632d003fadcb0f544e8a5d` |
| English split | `7913aa575a1f271955910eb8e2bae4343e15f890653651cf7982be6191e74deb` |
| HDPI split | `2caa6b3731ec1fa8d03bf09fae39608485a28c47b978514c15fb98699b900aa1` |

## Inspection method and limits

Used **jadx 1.5.6** and **apktool 3.0.3**, downloaded from their official [jadx](https://github.com/skylot/jadx/releases/tag/v1.5.6) and [apktool](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3) releases. Apktool decoded the base manifest, resources, and three DEX files. Some drawable references were unresolved because resources live in configuration splits; manifest and relevant code inspection succeeded.

Signia uses **.NET MAUI**. Java wrappers forward into managed methods, so JADX alone does not expose the main control logic. The ARM64 split contains `lib/arm64-v8a/libassembly-store.so`; its `XABA` store has 423 entries, including localized assemblies. Managed PE assemblies were unpacked and inspected as metadata and CIL with `dnfile 0.18.0`, `dncil 1.0.2`, and LZ4 decompression, following the [official .NET Android assembly-store documentation](https://github.com/dotnet/android/blob/main/Documentation/project-docs/AssemblyStores.md).

A whole-app JADX run was terminated by the environment before completion. Relevant Java wrappers were available; a separate memory-limited single-class decompilation of `crc6485982da7db80fa79.ThumbOnlyTouchListener` completed successfully. Apktool smali and managed CIL supplement that partial Java output. The findings below are supported by those specific methods, not a claim of exhaustive native-code analysis.

APK files, tool downloads, disassembly, signature logs, and inspection scripts remain in `/tmp/signia-analysis/`; proprietary APKs and full decompiled sources are not added to the repository. RVAs below identify methods in the named managed DLLs and are build-specific.

## External Android entry points

Confirmed by `AndroidManifest.xml`:

| Exported component | Purpose/evidence | Volume integration finding |
|---|---|---|
| `crc6451513a1ba22eb348.MainActivity` | Launcher; managed `RTA.Maui.MainActivity`; `singleTask` | Can launch app; no volume-setting action found |
| `crc648316b0a9aa8cfd61.BrowserTabActivity` | Authentication browser activity | No microphone-volume handler identified |
| `microsoft.identity.client.AuthenticationActivity` | Authentication activity | No microphone-volume handler identified |
| `com.google.firebase.iid.FirebaseInstanceIdReceiver` | Cloud-messaging actions; requires `com.google.android.c2dm.permission.SEND` | Not an ordinary Tasker command receiver |
| `androidx.profileinstaller.ProfileInstallReceiver` | Profile-installation actions; requires `android.permission.DUMP` | Not a volume receiver |

No exported service is declared for remote volume commands. `ForegroundService.RtaForegroundService` explicitly has `exported=false`; the other managed foreground-service entry, `crc64548e9e1d57faeeff.RtaForegroundService`, has no exported attribute or intent filter and is not an external command endpoint. `KeepAliveService` likewise has no intent filter/exported declaration. Firebase messaging, activity-recognition, and media-session services are non-exported. Providers are non-exported. Other manifest receivers are non-exported connectivity, battery, energy-saver, notification/alarm, and transport receivers. App-defined dynamic-receiver permission `com.signia.rta.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` is signature-protected.

Deep links declared on MainActivity:

- `myeverything:` with `VIEW`, `DEFAULT`, and `BROWSABLE`.
- `https://go.wsa.com/fitting/Signia...`, with an auto-verified `VIEW` filter.

`RTA.Maui.MainActivity.OnNewIntent` (RVA `0xa447`) calls `HandleIntent` (`0xa4ac`), which handles foreground-service notification navigation, a wearing-time URI branch, app links, and notification/navigation work. `HandleAppLinkIntent` (`0xa9d4`) delegates to `RTA.Maui.AppLink.AppLinkService.HandleAppLinkRequest` (`0x17450`). That method's state machine checks a `go.wsa.com/fitting/<app-name>` URL and calls `NavigateToAsyncRemoteFittingPage` (`0x174d8`). **These are navigation/fitting entry points; no volume parameter handler was found.** Manifest `<queries>` entries for `wsamyupdater:`, `mailto:`, and `tel:` describe outbound visibility, not incoming control APIs.

Searches of relevant MAUI/RemoteControl entry code for volume intents, `IntentFilter`, `RegisterReceiver`, `volume_up`, `volume_down`, and volume broadcasts did not identify a supported external microphone-volume interface. Absence here is a scoped static finding, not proof about every future build or native module.

## Slider and accessibility implementation

| Confirmed class/method | Assembly; RVA | Evidence and implication |
|---|---|---|
| `Component.RemoteControl.MAUI.Views.VolumeView.InitializeComponent` | `Component.RemoteControl.MAUI.dll` | Builds left/right/common sliders and binds their value and command properties to `VolumeViewModel` |
| `Component.RemoteControl.MAUI.Views.CustomControls.VerticalSlider.InitializeComponent` | `Component.RemoteControl.MAUI.dll` | `TA-SliderValue` is assigned to `ValueLabel`; `SliderAutomationId` is bound to the actual `CustomVerticalSlider` |
| `Microsoft.Maui.Handlers.SliderHandler.CreatePlatformView` | `Microsoft.Maui.dll`; `0x3cb67` | Creates `Android.Widget.SeekBar`, initially with native max `2147483647` |
| `Component.RemoteControl.MAUI.Platforms.VerticalSliderHandler.ConnectHandler` | `Component.RemoteControl.MAUI.Platforms.dll`; `0x3ca8` | Installs `ThumbOnlyTouchListener` using `View.SetOnTouchListener` |
| `Component.RemoteControl.MAUI.Platforms.ThumbOnlyTouchListener.OnTouch` | Same; `0x3b40` | On DOWN, stores whether touch began on thumb; MOVE/UP/CANCEL are consumed when it did not |
| `ThumbOnlyTouchListener.IsTouchOnThumb` | Same; `0x3b9c` | Computes thumb position from native progress/max and padding, then tests a rectangle inset by 15% of thumb width |
| `VerticalSliderHandler.HandlerOnProgressChanged` | Same; `0x3da8` | Schedules native progress snapping and calls `VerticalCustomSlider.OnProgressChanged` |
| `VerticalSliderHandler.HandlerOnStopTrackingTouch` | Same; `0x3d9b` | Calls `VerticalCustomSlider.OnSliderStopTrackingTouch` |
| `Component.RemoteControl.MAUI.Views.CustomControls.VerticalCustomSlider.SliderValueChangeStopped` | `Component.RemoteControl.MAUI.dll`; `0x3d54e` | Calls `ValueChangedCommand.CanExecute` and then `Execute` with current value |
| `VerticalCustomSlider.OnSliderValueChanged` | Same; `0x3d58c` | Contains a separate accessibility-conditioned command-commit branch |
| `Component.RemoteControl.MAUI.Platforms.Helpers.AccessibilityHelper.IsAccessibilityEnabled` | Platform DLL; `0x3fc4` | Requires `AccessibilityManager.IsEnabled && IsTouchExplorationEnabled` |

`VerticalSliderHandler`'s progress callback rounds to an integer level and calls `Android.Widget.ProgressBar.set_Progress`; its scale derives from native max and MAUI maximum. The normal command is committed on stop tracking. Therefore a two-contact tap-then-swipe can fail even with correct distance: the swipe's new DOWN must independently pass the thumb hit test.

Actual slider automation IDs in `VolumeView.InitializeComponent` are `TA-VolumeSliderLeft`, `TA-VolumeSliderRight`, and **`VolumeSlider` for the common slider**. `TA-SliderValue` is useful for numbered-label readback but is not the seek node for `ACTION_SET_PROGRESS`. Android resource-ID exposure and live hierarchy must be checked on the installed build; MAUI automation IDs alone do not prove live node visibility or action availability. Semantic descriptions/hints are present, including localized volume-control descriptions and split/merge labels.

No custom `AccessibilityNodeInfo` or `performAccessibilityAction` override was found in these Signia slider classes. Bundled AndroidX/Material code contains accessibility actions, but that alone does not establish use by this slider. The native SeekBar inherits platform accessibility support:

- [Android `SeekBar.onInitializeAccessibilityNodeInfoInternal`](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/widget/SeekBar.java) advertises `ACTION_SET_PROGRESS` when enabled and determinate.
- [Android `AbsSeekBar.performAccessibilityActionInternal`](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/widget/AbsSeekBar.java) changes progress with `fromUser=true`; it does not call the touch stop-tracking callback. Scroll actions similarly change progress rather than perform a full touch gesture.
- [Android action documentation](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo.AccessibilityAction#ACTION_SET_PROGRESS) requires a progress argument in the node's `RangeInfo` domain. Do not assume that domain is displayed levels 0–15; the MAUI native scale here is much larger.

**Inference:** setting progress may move the UI without sending the microphone-volume command when touch exploration is off. The accessibility branch could commit under appropriate conditions, but it also depends on the slider's change/rounding logic. Neither successful action return nor changed label alone proves a hearing-aid update. No accessibility action was executed during this analysis.

## Microphone-volume command and communication path

Confirmed managed call chain:

1. `Component.RemoteControl.ViewModels.VolumeViewModel.LeftSliderValueChangedCommandExecute` (`0x8b95`) / `RightSliderValueChangedCommandExecute` (`0x8ba4`) / `CommonSliderValueChangedCommandExecute` (`0x8bb4`) enter the ordinary volume flow.
2. `VolumeViewModel.SetVolume` (`0x8bf8`; state-machine `MoveNext` `0x1e7f4`) uses an `isUpdating` guard and calls `IVolumeCommandsHandler.WriteVolumeAsync`.
3. `Component.RemoteControl.Handlers.Volume.VolumeCommandsHandler.WriteVolumeAsync` (`0xf158`) calls `IVolumeService.WriteAsync` through its asynchronous work.
4. `Component.RemoteControl.Services.VolumeService.WriteAsync` (`0xd80c`) converts the slider value using `IVolumeProvider.FromSlider`, evaluates available transports, and calls either `WSA.Foundation.Bluetooth.Abstractions.IVolumeExtension.WriteAsync` or `WSA.Foundation.Acoustic.Abstractions.IVolumeExtension.WriteAsync`. Its fallback defaults are volume **8**, maximum **15**; actual capability/max queries exist.

Bluetooth path: `WSA.Foundation.Bluetooth.Extensions.VolumeExtension.WriteAsync` (`0x108a8`, plus its internal overload `0x10ab0`) selects internal Basic, Advanced, or FAPI protocol handling. Relevant methods are `Communication.Protocols.BasicCommandProtocol.WriteVolumeAsync` (`0x192f4`), `AdvancedCommandProtocol.WriteVolumeAsync` (`0x190ec`), and `FapiCommandProtocol.WriteVolumeAsync` (`0x19e5e`). Lower transport methods include `WSA.Foundation.Bluetooth.Device.Device.WriteAsync` (`0x134e4`) and `GattAccess.CharacteristicAccess.WriteAsync` (`0x5888`), using internal device/characteristic abstractions. These are in-process .NET methods, not Android exported services Tasker can call.

Acoustic path: `WSA.Foundation.Acoustic.Extensions.VolumeExtension.WriteVolumeAsync` (`0x50ec`; state machine `0x127fc`) uses `IVolumeConverter.FromVolume` and `EnsureIsValid`, constructs an absolute-position sequence, and calls `IHearingSystemInternal.WriteTonesAsync`. `WSA.Foundation.Acoustic.HearingSystem.Device.WriteTonesAsync` (`0x2251`) forwards it with the full acoustic address to `IToneService.SendTonesAsync`.

`WSA.Foundation.Audio.ToneService.SendToneAsync` (`0x2d00`) / `SendTonesAsync` (`0x2d64`) generate command audio using `WSA.Foundation.Audio.AcousticTone.GenerateControlTone` (`0x216c`). Generation uses `Utilities.CalculateCrc8`, data construction, `PulseEncoder.EncodePulse`, and `ModulateEncodedPulse`. `WSA.Foundation.Audio.Droid.Internal.CommandPlayer.PlayToneAsync` (`0x3220`) is the playback path. **Command IDs are not frequencies or standalone WAV resources.** The addressed encoder and volume conversion matter.

`WSA.Foundation.Bluetooth.Extensions.StreamingExtension.WriteVolumeAsync`, tinnitus extensions, and phone `SoundPlayManager` volume methods are distinct paths. Changing Android media volume is not established as equivalent to changing hearing-aid microphone volume.

## Most viable Tasker integration

Recommended future implementation path; **not implemented or executed in this investigation**:

1. Launch Signia and open its normal microphone-volume screen. Use fresh accessibility data and require an unambiguous current knob/level, Signia foreground, and enabled controls.
2. Use Tasker 6.6.20's Java Code and `tasker.getAccessibilityService()` with Tasker accessibility enabled. The [Tasker Java Code documentation](https://tasker.joaoapps.com/userguide/en/help/ah_java_code.html) exposes the service and node traversal.
3. Begin one pointer at the current knob centre. Hold about **200 ms** with `GestureDescription.StrokeDescription(..., willContinue=true)`, then use `continueStroke(..., willContinue=false)` to move upward and release. [Android stroke continuation](https://developer.android.com/reference/android/accessibilityservice/GestureDescription.StrokeDescription#continueStroke(android.graphics.Path,%20long,%20long,%20boolean)) preserves that pointer across segments.
4. Retain the user's initial **40 px** step and **300 ms** movement. The user measured level 9 at Y=1621 and level 10 at Y=1581. Those coordinates and the 200 ms hold are device-specific operating inputs, **not values mandated or confirmed by this APK's code**.
5. Await actual gesture completion, then obtain fresh readback and require `new_level = old_level + 1`; unchanged or overshoot is failure. Do not retry with increasing distances. UI readback confirms app state, not an independent measurement of hearing-aid output.

This follows the confirmed thumb-only input and stop-tracking commit path, while letting Signia manage its own connections, conversions, and commands. It fits no root, no phone ADB, and no helper app. Reliability still requires a controlled phone test on the actual installed build; static analysis cannot certify it.

A read-only next diagnostic would inspect the live seek node's class, resource ID, bounds, `RangeInfo`, and supported actions. `ACTION_SET_PROGRESS` is worth considering only if its scaling and command-commit behavior are established. No public direct Bluetooth/acoustic Tasker API was found; adding the app's DLL to Tasker would not grant access to the running app's managed objects or hearing-aid session.

## Follow-up: Insio CIC / Silk acoustic control

The user identifies the aids as Insio CIC and describes control as the same as Silk. Exact generation and firmware remain unconfirmed. [Signia's official Insio IX / Silk Charge&Go IX guide](https://www.signia.net/ja-jp/blog/local/ja-jp/silk-charge-go-ix-app/) explicitly describes high-frequency acoustic control and acoustic pairing for these small aids without Bluetooth. This supports prioritizing the acoustic implementation if the user's model is Insio IX CIC; it does not establish support for every command in the catalogue.

### Addressing and setup — confirmed code

In `WSA.Foundation.Acoustic.dll`, `HearingSystem.Device` constructs the destination byte as `(brandIdentifier << 4) | ArcAddress`. `Brand.BrandParser.GetBrandIdentifier` (RVA `0x542c`) maps Signia to identifier zero. `HearingSystem.RandomArcAddressProvider.Create` (`0x3269`) uses `Random.Next(1,15)`, yielding addresses 1–14.

`HearingSystem.HearingSystemFactory.CreateDeviceInformationAsync` (`0x2e5c`, async body `0x748c`) selects a random address, excludes the other device's address, creates device information, and calls `SendMfaPairingTone`. It rejects the older D8/D9/D10 platform branch. `SendMfaPairingTone` (`0x31fc`, async body `0x7ee0`) constructs the full brand/address byte and passes a two-element sequence containing pairing ID 105 and that byte to `IToneService.SendBroadcastTonesAsync`. This is a setup-specific broadcast path; ordinary volume writes use the selected device's address. No setup tones were generated or sent.

`GetPersistedArcAddress` (`0x30f8`, async body `0x79c0`) accesses `HearingInstrumentParameterKeys.ConfiguredAcousticAddress`. A replacement app needs its own legitimate setup flow or an explicitly supplied known address. Access to Signia's private persisted state is not established under the no-root constraints. The complete onboarding conditions, hearing-aid pairing window, and platform identification remain to be traced; the factory alone is not a complete setup specification.

### Volume conversion — confirmed code, examples derived

In `WSA.Foundation.Shared.dll`, `Models.ExtendedVolume.FromSlider` (`0x28b4`), `ToPercent` (`0x29cc`), `ToPosition` (`0x2a54`), and `ToSliderValue` (`0x2aa5`) convert slider values through percentage and attenuation position, including floor operations. Increasing displayed volume generally decreases encoded attenuation position. For the ordinary maximum-15 branch, evaluating these formulas gives displayed level 9 → position 6 → command ID 22, and level 10 → position 5 → command ID 21. These are static arithmetic examples, not tested commands or evidence that the user's configured range is 15.

`Internal.VolumeConverter.GetMaxSteps` (`0x360c`) returns 15 normally, or 16 when `RequiresExplicitMuteChange` (`0x361d`) applies. That branch considers platform and firmware older than `6.2.3.0`; newer known platforms avoid this explicit-mute branch. The 16-step conversion handles zero volume through a separate mute state. A standalone implementation must preserve this conversion and receiver-state handling rather than encode `16 + displayedLevel`.

### Encoder and phone playback — confirmed static findings

In `WSA.Foundation.Audio.dll`:

| Method / evidence | Finding |
|---|---|
| `AcousticConstants.InitializeToneGeneration` (`0x2bd8`) and constant arrays | Default sample rate 44,100 Hz, bit length 0.0625 s, base frequency 15,360 Hz, band spacing 512 Hz, gain divisor 4, low-pass shaping, overlap factor 1.25 |
| `AcousticConstants.CreateFrequencyScheme` (`0x2b40`) | Four derived carriers: 14,592, 15,104, 15,616, 16,128 Hz |
| `AcousticTone.GenerateControlTone` (`0x216c`) | Calculates command CRC; with default XOR enabled combines it with destination address and `0xAA`; constructs two data arrays, encodes and modulates pulses, adds 12 pulse lengths to the sample array, moves the first two pulse lengths to the end of the original payload, and emits signed 16-bit little-endian PCM |
| `Utilities.GetBitByIndex` (`0x2fa2`) | Index zero is the most significant bit; indices outside 0–7 return zero |
| `PulseEncoder.EncodePulse` (`0x26d4`) | Maps the two constructed bit streams into a four-carrier pulse matrix |
| `ToneService.SendTonesAsync` (`0x2d64`) | Builds addressed command tones; supports an optional sniff-suspend tone |
| `Droid.Internal.CommandPlayer.SetSpeakerAsPreferredDevice` (`0x3324`) | Selects an output device and calls `AudioTrack.SetPreferredDevice` |
| `Droid.Internal.CommandPlayer.PlayToneAsync` (`0x3220`, async body `0x4428`) | Uses Android AudioTrack, PCM playback and a playback marker to complete the operation |

These constants describe this build's defaults; they are not a phone-independent acoustic calibration. The low-pass window, pulse overlap, complete framing/sample-count derivation, optional sniff handling, and audio-level/routing checks still need a faithful implementation review before claiming a complete compatible encoder. No waveform artifact was created.

**Receipt limitation:** the inspected acoustic write path completes on phone playback. No hearing-aid acknowledgement decoding was found in that path. Signia's guide describes an audible click from the aid after a setting change, but that does not prove the app receives machine-readable confirmation. App slider readback and AudioTrack completion cannot independently certify the aid's actual volume.

### Standalone-app feasibility

**There is enough information for an offline encoder and UI prototype, and a plausible standalone acoustic controller. A reliable replacement is not yet established.** The remaining work is to finish the ordinary onboarding/address lifecycle and framing analysis, identify the exact user's platform/range, and eventually validate playback and receipt with an explicitly authorized device test. Android speaker playback does not inherently require root, phone ADB, Tasker, or the Signia app. That architectural conclusion is an inference from the inspected AudioTrack implementation, not a tested replacement app.

## Acoustic command catalogue

The following is the exact named enumeration catalogue found in `WSA.Foundation.Acoustic.dll`, namespace **`WSA.Foundation.Acoustic.Extensions`**. IDs are decimal. Enum presence is confirmed; use/support of every member on the user's hearing aids is not. These include configuration and fitting-related features as well as everyday remote controls. They are documented as static findings, not tested invocation instructions.

For microphone volume, `VolumeCommand.Position00`–`Position15` are IDs **16–31**; `Increase=82`, `Decrease=83`. The absolute write method uses **16 + converted receiver position**, potentially preceded by `Receiver.Mute=90` or `Receiver.NotMute=91`. Displayed level and encoded receiver position should not be assumed identical for every device configuration.

### `AmbisoundControl`

`On = 101`; `Off = 102`

### `AutomaticBinauralConfiguration`

`SetMagneticInductionLinkAddress = 127`; `SetLeft = 130`; `SetRight = 131`; `ConfirmLeftSync = 134`; `ConfirmRightSync = 135`

### `BabyBoomerCommandId`

`Off = 214`; `Boost = 215`; `Relax = 216`

### `CrosVolumeCommand`

`BasePosition = 176`; `Position00 = 176`; `Position01 = 177`; `Position02 = 178`; `Position03 = 179`; `Position04 = 180`; `Position05 = 181`; `Position06 = 182`; `Position07 = 183`; `Position08 = 184`; `Position09 = 185`; `Position10 = 186`; `Position11 = 187`; `Position12 = 188`; `Position13 = 189`; `Position14 = 190`; `Position15 = 191`; `Increase = 92`; `Decrease = 93`

### `EasyFit`

`ResetToDefault = 70`; `FactoryReset = 106`; `SelectCluster01 = 208`; `SelectCluster02 = 209`; `SelectCluster03 = 210`; `SelectCluster04 = 211`; `SelectCluster05 = 212`; `SelectCluster06 = 213`; `MasterGainStep00 = 192`; `MasterGainStep01 = 193`; `MasterGainStep02 = 194`; `MasterGainStep03 = 195`; `MasterGainStep04 = 196`; `MasterGainStep05 = 197`; `MasterGainStep06 = 198`; `MasterGainStep07 = 199`; `MasterGainStep08 = 200`; `MasterGainStep09 = 201`; `MasterGainStep0A = 202`; `MasterGainStep0B = 203`; `MasterGainStep0C = 204`; `MasterGainStep0D = 205`; `MasterGainStep14 = 206`; `MasterGainStep15 = 207`; `CouplingTyp1 = 123`; `CouplingTyp2 = 124`; `CouplingTyp3 = 125`; `CouplingTyp4 = 126`

### `FlightMode`

`On = 103`; `Off = 104`

### `HearingLossAssessment`

`Enter = 72`; `Exit = 73`; `SetCoupling01 = 123`; `SetCoupling02 = 124`; `SetCoupling03 = 125`; `SetCoupling04 = 126`; `SequenceNumber00 = 224`; `SequenceNumber01 = 225`; `SequenceNumber02 = 226`; `SequenceNumber03 = 227`; `SequenceNumber04 = 228`; `SequenceNumber05 = 229`; `SequenceNumber06 = 230`; `SequenceNumber07 = 231`; `SequenceNumber08 = 232`; `SequenceNumber09 = 233`; `FrequencyLevel01 = 234`; `FrequencyLevel02 = 235`; `FrequencyLevel03 = 236`; `FrequencyLevel04 = 237`; `KeepAlive = 238`

### `IntelliZoomCommand`

`BasePosition = 112`; `Position00 = 112`; `Position01 = 113`; `Position02 = 114`; `Position03 = 115`; `Position04 = 116`; `Position05 = 117`; `Position06 = 118`; `Position07 = 119`; `Position08 = 120`; `Position09 = 121`; `Position10 = 122`; `Increase = 96`; `Decrease = 97`

### `Pairing`

`EnablePairing = 98`; `EnablePairingMfa = 105`

### `PowerManagement`

`BatteryBeepLeft = 128`; `BatteryBeepRight = 129`

### `Program`

`BasePosition = 64`; `Position00 = 64`; `Position01 = 65`; `Position02 = 66`; `Position03 = 67`; `Position04 = 68`; `Position05 = 69`; `Increase = 86`; `Decrease = 87`

### `Receiver`

`Mute = 90`; `NotMute = 91`

### `SideLookNarrowFocus`

`Off = 71`; `Front = 74`; `Back = 75`; `Left = 76`; `Right = 77`

### `SoundBalanceCommand`

`BasePosition = 32`; `Position00 = 32`; `Position01 = 33`; `Position02 = 34`; `Position03 = 35`; `Position04 = 36`; `Position05 = 37`; `Position06 = 38`; `Position07 = 39`; `Position08 = 40`; `Position09 = 41`; `Position10 = 42`; `Position11 = 43`; `Position12 = 44`; `Position13 = 45`; `Position14 = 46`; `Position15 = 47`; `Increase = 84`; `Decrease = 85`

### `StandBy`

`GoTo = 80`; `WakeUp = 81`

### `TeleAudiologyEqualizer`

`BaseBandPosition = 144`; `Band1Position0db = 144`; `Band1Position3db = 145`; `Band1Position6db = 146`; `Band1Position9db = 147`; `Band1PositionMinus12db = 148`; `Band1PositionMinus9db = 149`; `Band1PositionMinus6db = 150`; `Band1PositionMinus3db = 151`; `Band2Position0db = 152`; `Band2Position3db = 153`; `Band2Position6db = 154`; `Band2Position9db = 155`; `Band2PositionMinus12db = 156`; `Band2PositionMinus9db = 157`; `Band2PositionMinus6db = 158`; `Band2PositionMinus3db = 159`; `Band3Position0db = 160`; `Band3Position3db = 161`; `Band3Position6db = 162`; `Band3Position9db = 163`; `Band3PositionMinus12db = 164`; `Band3PositionMinus9db = 165`; `Band3PositionMinus6db = 166`; `Band3PositionMinus3db = 167`; `Band4Position0db = 168`; `Band4Position3db = 169`; `Band4Position6db = 170`; `Band4Position9db = 171`; `Band4PositionMinus12db = 172`; `Band4PositionMinus9db = 173`; `Band4PositionMinus6db = 174`; `Band4PositionMinus3db = 175`

### `TemporaryHearingInstrumentSettingsCommandId`

`Off = 107`; `SpeechFocus = 108`; `ActiveMode = 109`; `MusicMode = 110`; `OceanWave = 111`; `LeisureMode = 94`; `PanoramaEffect = 95`

### `TinnitusVolumeCommand`

`BasePosition = 48`; `Position00 = 48`; `Position01 = 49`; `Position02 = 50`; `Position03 = 51`; `Position04 = 52`; `Position05 = 53`; `Position06 = 54`; `Position07 = 55`; `Position08 = 56`; `Position09 = 57`; `Position10 = 58`; `Position11 = 59`; `Position12 = 60`; `Position13 = 61`; `Position14 = 62`; `Position15 = 63`; `Increase = 88`; `Decrease = 89`

### `VolumeCommand`

`BasePosition = 16`; `Position00 = 16`; `Position01 = 17`; `Position02 = 18`; `Position03 = 19`; `Position04 = 20`; `Position05 = 21`; `Position06 = 22`; `Position07 = 23`; `Position08 = 24`; `Position09 = 25`; `Position10 = 26`; `Position11 = 27`; `Position12 = 28`; `Position13 = 29`; `Position14 = 30`; `Position15 = 31`; `Increase = 82`; `Decrease = 83`

### `WindNoiseCanceler`

`On = 99`; `Off = 100`

## Evidence and reproducibility

Key local evidence from this investigation (temporary files may not survive environment cleanup):

- Manifest: `/tmp/signia-analysis/apktool-out/AndroidManifest.xml`; version/SDK metadata: `apktool.yml`.
- Signature logs: `/tmp/signia-analysis/*-signature.txt`; bundle: `signia.xapk`.
- Java wrapper: `/tmp/signia-analysis/ThumbOnlyTouchListener.java`; managed type mapping explicitly names `Component.RemoteControl.MAUI.Platforms.ThumbOnlyTouchListener`.
- Managed IL: `/tmp/signia-analysis/il/Component.RemoteControl.MAUI.Platforms.dll.txt`, `Component.RemoteControl.MAUI.dll.txt`, `Component.RemoteControl.dll.txt`, `Microsoft.Maui.dll.txt`, `RTA.Maui.Signia.dll.txt`, `WSA.Foundation.Bluetooth.dll.txt`, `WSA.Foundation.Acoustic.dll.txt`, and `WSA.Foundation.Audio.dll.txt`.
- Enum metadata: `/tmp/signia-analysis/acoustic-enums.txt`; extraction/inspection scripts: `inspect_il.py`, `inspect_entry.py`, `inspect_main.py`.

To reproduce, retrieve the artifact identified by the recorded hashes, verify all APK signatures, decode the base with apktool, inspect DEX wrappers with jadx, unpack the ARM64 assembly store using the documented format, and locate the listed methods/RVAs and enum constants. RVAs and MAUI Java wrapper names may change between app releases.

Web searching did not locate an authoritative complete numeric acoustic-command registry. A [Sivantos-authored article on acoustic wireless control](https://www.audiology.org/wp-content/uploads/at-archive-images/AT276_NovDec_15.pdf) discusses the technology; it does not establish this version's exact command IDs. The command catalogue above comes directly from this APK's metadata, not from that article or guessed tone mappings.
