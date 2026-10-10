# Signia reverse engineering: Tasker microphone volume

Reviewed October 9, 2026 (America/New_York). **User-confirmed configuration: acoustic control; BLE is not used.** Static analysis only. Existing Tasker projects, exports, generators and Java code were not changed. No APK was patched, signed, installed or run; no hearing-aid command was transmitted.

## 1. Executive Summary

**Can Tasker reliably change microphone volume without dragging? Not yet established. A concrete accessibility route exists and deserves the next test; there is no proven externally callable volume API.**

**PROVEN FROM CODE:** The microphone control is a .NET MAUI custom slider backed by `android.widget.SeekBar`. Normal commands commit on stop tracking. A separate accessibility commit branch requires `AccessibilityManager.IsEnabled && IsTouchExplorationEnabled`, plus a user-change flag and a value difference greater than 0.001. Tasker accessibility alone does not satisfy touch exploration.

**LIKELY:** Tasker Java Code can locate the real seek node and invoke `ACTION_SET_PROGRESS`. With touch exploration active, Signia can take its accessibility commit branch. Callback order and rounding still need a phone test. An action returning true or a changed number does not establish aid receipt.

**SPECULATIVE:** Direct addressed acoustic PCM playback could bypass Signia entirely for acoustic aids. Actual command encoding exists in the APK. Reproduction requires address/profile parameters, conversion, complete encoding and playback validation. BLE volume bytes also exist in this multi-device app, but are irrelevant to your confirmed acoustic configuration.

The earlier local analysis recommended a continuous gesture. That recommendation is superseded by your report that both continuous-gesture variants failed. This investigation does not recommend further distance tuning or treat static thumb-hit logic as proof that another drag will work.

## 2. APK/version analyzed

Reused the already downloaded public artifact in `/tmp/signia-analysis`; this turn rechecked all SHA-256 hashes, bundle metadata, base signature, relevant CIL and manifest. Retrieval details below are recorded by the earlier analysis, not a fresh download today. The public APKMirror listing checked today also lists build 2.8.0.18214; it establishes a recent public release, not necessarily the newest build or your installed version.

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

### Analysis tools and boundaries

Used **jadx 1.5.6** and **apktool 3.0.3**, downloaded from their official [jadx](https://github.com/skylot/jadx/releases/tag/v1.5.6) and [apktool](https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.3) releases. Apktool decoded the base manifest, resources, and three DEX files. Some drawable references were unresolved because resources live in configuration splits; manifest and relevant code inspection succeeded.

Signia uses **.NET MAUI**. Java wrappers forward into managed methods, so JADX alone does not expose the main control logic. The ARM64 split contains `lib/arm64-v8a/libassembly-store.so`; its `XABA` store has 423 entries, including localized assemblies. Managed PE assemblies were unpacked and inspected as metadata and CIL with `dnfile 0.18.0`, `dncil 1.0.2`, and LZ4 decompression, following the [official .NET Android assembly-store documentation](https://github.com/dotnet/android/blob/main/Documentation/project-docs/AssemblyStores.md).

A whole-app JADX run was terminated by the environment before completion. Relevant Java wrappers were available; a separate memory-limited single-class decompilation of `crc6485982da7db80fa79.ThumbOnlyTouchListener` completed successfully. Apktool smali and managed CIL supplement that partial Java output. The findings below are supported by those specific methods, not a claim of exhaustive native-code analysis.

APK files, tool downloads, disassembly, signature logs, and inspection scripts remain in `/tmp/signia-analysis/`; proprietary APKs and full decompiled sources are not added to the repository. RVAs below identify methods in the named managed DLLs and are build-specific.

## 3. Slider implementation

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



The host activity is `crc6451513a1ba22eb348.MainActivity` / managed `RTA.Maui.MainActivity`. The examined control is MAUI `VolumeView`, not a Compose screen. No dedicated Android volume Fragment was identified. Its common value/command bindings are `CommonSliderValue` and `CommonSliderValueChangedCommand`; independent controls bind corresponding Left/Right properties. These are managed view bindings, not externally accessible objects.

Automation IDs are build-time MAUI identifiers. A numeric Android resource ID or exact fully qualified ID string cannot be certified without the live hierarchy. Do not target the value label as if it were the SeekBar.

## 4. Accessibility capabilities

Android 16 reference implementation: [SeekBar](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-16.0.0_r1/core/java/android/widget/SeekBar.java), [AbsSeekBar](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-16.0.0_r1/core/java/android/widget/AbsSeekBar.java). No Signia slider override of node initialization or `performAccessibilityAction` was identified in inspected classes. Installed Android/OEM behavior and live actions remain unverified.

| Capability | Evidence / limitation |
|---|---|
| `ACTION_SET_PROGRESS` | Platform SeekBar advertises it when enabled and determinate. Expected on the real node; not proven by a phone dump. |
| Forward/backward scroll | Platform AbsSeekBar advertises them away from respective endpoints. Changes progress, without touch-stop callback. |
| `RangeInfo` | Expected from native ProgressBar; inspect actual min/max/current. |
| `ACTION_CLICK` | No traced Signia click-to-volume commit. If advertised, do not assume it sends the command. |
| SeekBar semantics | Native creation and accessibility class support it. |
| Compose SetProgress | Not the implementation of this control. |

### Exact action arguments

Use `AccessibilityNodeInfo.AccessibilityAction.ACTION_SET_PROGRESS.getId()` (16908349). Pass a Bundle containing `AccessibilityNodeInfo.ACTION_ARGUMENT_PROGRESS_VALUE` (string `android.view.accessibility.action.ARGUMENT_PROGRESS_VALUE`) using **putFloat**, in the node's native range. AOSP casts that float to int and changes progress with `fromUser=true`. It does not invoke stop tracking. Scroll forward/backward are 4096/8192, take no progress Bundle, and use approximately one twentieth of native range; Signia subsequently snaps to its integer level. They are not guaranteed one-level increment/decrement commands.

`SliderHandler.CreatePlatformView` sets native max to **2147483647**, not 15. `VerticalSliderHandler.<HandlerOnProgressChanged>b__0` computes:

```text
scale = Truncate((nativeMax / mauiMaximum) * 100) / 100
level = Round(nativeProgress / scale)
nativeProgress = Convert.ToInt32(level * scale)
VerticalCustomSlider.OnSliderValueChanged(level)
```

For a confirmed 0–15 display domain, a candidate mapping is native min + target/15 * native span. At target 13 with native 0..2147483647 this is approximately 1861152494, supplied as float. Float precision loses integer units at this scale; snap-to-level tolerates small native differences, but readback is required. Use fresh RangeInfo and confirmed display bounds, never blindly `putFloat(..., 13)`.

### Commit gate: exact managed logic

Readable reconstruction of CIL in `Component.RemoteControl.MAUI.dll.txt`, RVA 0x3d58c:

```csharp
// OnSliderValueChanged(value); reconstruction, not original source
if (!_isUserChange) return;
double rounded = Math.Round(value, 2);
if (Math.Abs(Value - rounded) > 0.001) {
    Value = rounded;
    _isUserChange = false;
    if (_accessibilityHelper.IsAccessibilityEnabled())
        SliderValueChangeStopped();
}
```

`OnProgressChanged` (0x3d53d) sets `_isUserChange=true`. `SliderValueChangeStopped` (0x3d54e) tests `ValueChangedCommand.CanExecute(Value)`, resets the flag true and executes the command. Helper CIL at 0x3fc4 returns the conjunction of accessibility enabled and touch exploration enabled.

**PROVEN FROM CODE:** There is an accessibility-specific commit path. **LIKELY:** a changed accessibility progress can reach it. **UNKNOWN:** whether inherited MAUI callbacks update `Value` before this comparison on your build, suppressing the branch; dispatcher ordering and snapping can matter. Therefore even enabling TalkBack does not yet establish success. Do not assume ACTION_CLICK or an accessibility focus action substitutes for stop tracking.

[Tasker Java Code documentation](https://tasker.joaoapps.com/userguide/en/help/ah_java_code.html) exposes `tasker.getAccessibilityService()`, active-window roots and node traversal. This permits node `performAction` from Tasker itself without root, ADB or a helper app. Availability in the installed 6.6.20 build still needs checking. Tasker cannot call Signia's private SeekBar Java object or its managed stop callback across processes.

## 5. Volume-change call chain

Confirmed managed call chain:

1. `Component.RemoteControl.ViewModels.VolumeViewModel.LeftSliderValueChangedCommandExecute` (`0x8b95`) / `RightSliderValueChangedCommandExecute` (`0x8ba4`) / `CommonSliderValueChangedCommandExecute` (`0x8bb4`) enter the ordinary volume flow.
2. `VolumeViewModel.SetVolume` (`0x8bf8`; state-machine `MoveNext` `0x1e7f4`) uses an `isUpdating` guard and calls `IVolumeCommandsHandler.WriteVolumeAsync`.
3. `Component.RemoteControl.Handlers.Volume.VolumeCommandsHandler.WriteVolumeAsync` (`0xf158`) calls `IVolumeService.WriteAsync` through its asynchronous work.
4. `Component.RemoteControl.Services.VolumeService.WriteAsync` (`0xd80c`) converts the slider value using `IVolumeProvider.FromSlider`, evaluates available transports, and calls either `WSA.Foundation.Bluetooth.Abstractions.IVolumeExtension.WriteAsync` or `WSA.Foundation.Acoustic.Abstractions.IVolumeExtension.WriteAsync`. Its fallback defaults are volume **8**, maximum **15**; actual capability/max queries exist.

Bluetooth path: `WSA.Foundation.Bluetooth.Extensions.VolumeExtension.WriteAsync` (`0x108a8`, plus its internal overload `0x10ab0`) selects internal Basic, Advanced, or FAPI protocol handling. Relevant methods are `Communication.Protocols.BasicCommandProtocol.WriteVolumeAsync` (`0x192f4`), `AdvancedCommandProtocol.WriteVolumeAsync` (`0x190ec`), and `FapiCommandProtocol.WriteVolumeAsync` (`0x19e5e`). Lower transport methods include `WSA.Foundation.Bluetooth.Device.Device.WriteAsync` (`0x134e4`) and `GattAccess.CharacteristicAccess.WriteAsync` (`0x5888`), using internal device/characteristic abstractions. These are in-process .NET methods, not Android exported services Tasker can call.

Acoustic path: `WSA.Foundation.Acoustic.Extensions.VolumeExtension.WriteVolumeAsync` (`0x50ec`; state machine `0x127fc`) uses `IVolumeConverter.FromVolume` and `EnsureIsValid`, constructs an absolute-position sequence, and calls `IHearingSystemInternal.WriteTonesAsync`. `WSA.Foundation.Acoustic.HearingSystem.Device.WriteTonesAsync` (`0x2251`) forwards it with the full acoustic address to `IToneService.SendTonesAsync`.

`WSA.Foundation.Audio.ToneService.SendToneAsync` (`0x2d00`) / `SendTonesAsync` (`0x2d64`) generate command audio using `WSA.Foundation.Audio.AcousticTone.GenerateControlTone` (`0x216c`). Generation uses `Utilities.CalculateCrc8`, data construction, `PulseEncoder.EncodePulse`, and `ModulateEncodedPulse`. `WSA.Foundation.Audio.Droid.Internal.CommandPlayer.PlayToneAsync` (`0x3220`) is the playback path. **Command IDs are not frequencies or standalone WAV resources.** The addressed encoder and volume conversion matter.

`WSA.Foundation.Bluetooth.Extensions.StreamingExtension.WriteVolumeAsync`, tinnitus extensions, and phone `SoundPlayManager` volume methods are distinct paths. Changing Android media volume is not established as equivalent to changing hearing-aid microphone volume.

UI prefix to that chain:

```text
native SeekBar progress -> VerticalSliderHandler.HandlerOnProgressChanged
 -> queued integer snapping -> VerticalCustomSlider.OnSliderValueChanged
release -> HandlerOnStopTrackingTouch -> OnSliderStopTrackingTouch
 -> SliderValueChangeStopped -> CommonSliderValueChangedCommand.Execute
 -> VolumeViewModel.CommonSliderValueChangedCommandExecute -> SetVolume
 -> VolumeCommandsHandler.WriteVolumeAsync -> VolumeService.WriteAsync
 -> selected Bluetooth or acoustic extension -> aid
```

Accessibility uses the progress path and can enter `SliderValueChangeStopped` through the gated branch above; it does not synthesize the release callback. `SetVolume`'s busy guard also means overlapping requests must not be treated as a queued reliable API.

## 6. Communication transport

**PROVEN FROM CODE:** Both proprietary BLE/GATT and generated acoustic audio command paths are implemented. The permissions alone were not used to infer transport. You confirmed that BLE is not used. For your Insio CIC/common-control setup, this report therefore follows the acoustic command path. The BLE findings below describe other app-supported configurations and are not automation candidates for your aids.

### BLE payload construction

In `WSA.Foundation.Bluetooth.dll.txt`:

- Basic protocol `<WriteVolumeAsync>d__4.MoveNext`, RVA **0x605b4**: sends `[0x04, convertedPosition]` to `HiService.BasicControlCommand.Characteristic` on the selected side's device.
- Advanced protocol `<WriteVolumeAsync>d__23.MoveNext`, RVA **0x5ffe0**: sends `[0x01, 0x03, 0x00, 0x00, convertedPosition & 0x0f]` to `HiService.AdvanceControlCommand.Characteristic`.
- FAPI uses `IUserConfigurableFeatures.WriteVolumeAsync` via `PerformRequestSafe`; a complete packet was not reconstructed.

Basic characteristic alternatives (`.cctor`, 0x4e84):
`8b8276e8-0f0c-40bb-b422-3770fa72a864`, `c8f747ac-21b2-45b8-87f8-bd49a13eff49`, `22e01397-43cb-45b6-a921-b28271e4e989`.

Advanced alternatives (`.cctor`, 0x4e17):
`c8f76c2c-21b2-45b8-87f8-bd49a13eff49`, `c8f74ffb-21b2-45b8-87f8-bd49a13eff49`.

`HiService.HiService..cctor` (0x501c) lists service alternatives:
`8b821572-0f0c-40bb-b422-3770fa72a864`, `c8f7d5ad-21b2-45b8-87f8-bd49a13eff49`, `62f7e35b-7763-4200-8688-f50ec96816ef`, `c8f777d0-21b2-45b8-87f8-bd49a13eff49`, `56772eaf-2153-4f74-acf3-4368d99fbf5a`, `62e84690-3757-4af3-95f5-269e0f7b7c0a`, `1540DCCF-1A7A-4574-8B50-5BF6D54BDA9A`.

These arrays are protocol/device alternatives, not instructions to write all UUIDs. Device discovery, pairing/bonding, characteristic selection, protocol selection, volume conversion and session requirements remain unresolved for your aids. BondingService and FAPI request/response abstractions exist. This analysis does not establish either that payloads require application encryption or that arbitrary unauthenticated writes are accepted. BLE bytes in code are not proof of a working Tasker command.

No microphone-command chain through Bluetooth Classic, Android ASHA or LE Audio was established. Streaming/headset support is separate; do not identify microphone gain with streaming volume or phone media volume.

### Acoustic encoding and playback

`WSA.Foundation.Acoustic.Extensions.VolumeCommand` defines Position00..15 = **16..31**, Increase=82, Decrease=83. The absolute write state machine (0x127fc) sends 90 alone for ReceiverState 3 (mute), otherwise optionally 91 for state 4 (unmute), followed by **16 + converted receiver position**. These are command IDs, not tones in Hz. Default/display position conversion must be verified.

`Device.WriteTonesAsync` supplies a **full acoustic address**. `AcousticTone.GenerateControlTone` (0x216c) computes CRC8, optionally XORs CRC with `address ^ 0xaa`, constructs DataA/DataB, pulse-encodes and modulates, then emits signed 16-bit little-endian PCM. `ModulateEncodedPulse` (0x245c) selects precomputed waveform rows from the encoded pulse.

`ToneGenerationParameters.InitializeToneGeneration` (0x2bd8) defaults to 44100 Hz sampling, overlap 1.25, gain table index 0 (=4), bit-length index 5 (=0.0625 s), base-frequency index 9 (=15360 Hz), band spacing index 0 (=512 Hz), and XOR-enabled CRC. These are constructor defaults; later profile configuration can override them. Extracted tables are in `/tmp/signia-analysis/audio-constants.json`: frequency choices 3840..23040 in 1280-Hz steps; spacing choices 512/1024/1536/2048; gain choices 4/2/1.2; bit-length choices 0.00625/0.0125/0.025/0.0375/0.05/0.0625/0.08125/0.1 seconds.

No fixed WAV file was identified as the implementation of microphone volume: this path generates addressed PCM. Complete CRC polynomial/bit ordering, shaping, address selection and active profile are not presented as a reproduced encoder. Tasker could theoretically generate/play equivalent PCM through Android audio APIs or files, but nothing was generated or played here. Playback routing/phone volume guards and acoustic reception affect success. Cached app state is not a receiver acknowledgement; bypassing Signia would also leave its displayed cache stale.

## 7. Exported/callable interfaces

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

No microphone-volume Binder/AIDL contract was identified in the inspected app entry points. Internal .NET interfaces named `IVolumeService` and `IVolumeExtension` are not Binder contracts. No volume shortcut or notification action was traced to a volume setter; the examined foreground-notification intent path navigates within the app. This is a scoped negative result, not a claim that every native library and dynamic receiver was exhaustively audited.

## 8. Tasker automation possibilities

Ranked by next useful investigation, not claimed working reliability:

| Rank | Approach | Assessment under constraints |
|---|---|---|
| 1 | A: node ACTION_SET_PROGRESS | Best bounded test. Direct numeric target; needs real seek node, range conversion and proven commit. Touch exploration gate is material. |
| 2 | B: forward/backward node action | Same commit limitation; platform step/snapping may differ from one level. Less precise than A. |
| 3 | E: direct acoustic command | Real encoder and command IDs found. Plausible for acoustic-compatible aids, substantial reproduction/validation required; no helper inherently needed. |
| Excluded | F: direct BLE | Not applicable: you confirmed BLE is not used. App-wide evidence is retained only for completeness. |
| — | C: intent/broadcast/service | No callable microphone-volume endpoint identified. |
| — | D: deep link/component | Existing links navigate/fitting; no numeric volume parameter found. |
| Last | G: touch gesture | Already failed in your tests. Thumb-only behavior explains a requirement but does not justify repeating distance tuning. |

No approach is currently **PROVEN TO WORK ON YOUR PHONE**. The confirmed pieces above are code findings only.

## 9. Recommended implementation

**Stop before implementation, as requested.** Proposed first step is a separate diagnostic/test task reviewed before changing the existing project:

1. Read-only inspection: obtain the common microphone SeekBar while Signia is foreground; record class, ID, bounds, enabled state, actions and RangeInfo. Read `AccessibilityManager.isEnabled()` and `isTouchExplorationEnabled()` from Tasker. Confirm displayed range and installed app version.
2. If the node exposes set-progress, use a confirmed current level (e.g. 12) and request one adjacent non-boundary target (13). Map displayed target to the native range. Avoid mute/maximum and overlapping tasks.
3. Invoke the action once, wait for fresh UI readback, and separately establish an audible aid-volume change. Record action return, displayed value and physical result separately.
4. If touch exploration is false, code predicts no accessibility-specific commit. Do not label a moved knob success. A user-enabled TalkBack comparison could test the gate, but it changes phone interaction and must be an explicit experiment; no settings are changed here.
5. If the callback does not commit even with touch exploration true, stop this route. Next investigate full acoustic encoder/address/profile extraction for the actual aids, before proposing PCM playback.

The core operation would be the following **proposal**, not an installed task. `node` and `nativeTarget` must come from the identity/range checks above:

```java
Bundle args = new Bundle();
args.putFloat(AccessibilityNodeInfo.ACTION_ARGUMENT_PROGRESS_VALUE,
              (float) nativeTarget);
boolean accepted = node.performAction(
    AccessibilityNodeInfo.AccessibilityAction.ACTION_SET_PROGRESS.getId(), args);
// accepted is NOT a hearing-aid receipt or even proof of command commit.
```

This uses Tasker's own accessibility service and needs no root, persistent ADB or helper application. It still needs Signia's usable volume UI. Reliable locked-screen/background control is not established by this proposal.

## 10. Evidence / class names / methods / resources

All relevant local disassembly paths are rooted at `/tmp/signia-analysis/il/`; append the following filenames. RVAs identify this build, not stable APIs:

| File | Evidence |
|---|---|
| `Component.RemoteControl.MAUI.dll.txt` | `VolumeView.InitializeComponent`, `VerticalSlider.InitializeComponent`; common/left/right IDs and bindings; `VerticalCustomSlider` RVAs 0x3d53d, 0x3d546, 0x3d54e, 0x3d58c |
| `Component.RemoteControl.MAUI.Platforms.dll.txt` | `ThumbOnlyTouchListener.OnTouch` 0x3b40 / `IsTouchOnThumb` 0x3b9c; `ConnectHandler` 0x3ca8; stop handler 0x3d9b; progress handler 0x3da8; dispatched snapping 0x46e0; accessibility helper 0x3fc4 |
| `Microsoft.Maui.dll.txt` | `SliderHandler.CreatePlatformView` 0x3cb67: SeekBar constructor and max 2147483647 |
| `Component.RemoteControl.dll.txt` | `VolumeViewModel` command/SetVolume and `VolumeCommandsHandler`, `VolumeService` listed in section 5 |
| `WSA.Foundation.Bluetooth.dll.txt` | Protocol write methods/state machines, characteristic/service static constructors and GATT access listed in sections 5–6 |
| `WSA.Foundation.Acoustic.dll.txt` | `VolumeExtension.WriteVolumeAsync`, state machine 0x127fc; addressed `Device.WriteTonesAsync` |
| `WSA.Foundation.Audio.dll.txt` | `AcousticTone.GenerateControlTone` 0x216c / modulation 0x245c / defaults 0x2bd8; `ToneService` |
| `RTA.Maui.Signia.dll.txt` | MainActivity intent/app-link handlers and AppLinkService listed in section 7 |

Manifest: `/tmp/signia-analysis/apktool-out/AndroidManifest.xml`. Java wrapper: `/tmp/signia-analysis/ThumbOnlyTouchListener.java` (native bridge, not full managed behavior). Managed DLLs: `/tmp/signia-analysis/assemblies/`. Decoder: `/tmp/signia-analysis/inspect_il.py`. Hashes were recomputed October 9; base `apksigner verify --verbose --print-certs` passed v3 today. A whole-app Java decompilation alone cannot establish this MAUI app's behavior.

Example literal CIL excerpts (offsets within their methods):

```text
// SliderHandler.CreatePlatformView, Microsoft.Maui.dll, RVA 0x3cb67
0007 newobj Android.Widget.SeekBar::.ctor
000d ldc.i4 2147483647
0013 callvirt Android.Widget.ProgressBar::set_Max

// AccessibilityHelper.IsAccessibilityEnabled, platform DLL, RVA 0x3fc4
0025 call Android.Views.Accessibility.AccessibilityManager::get_IsEnabled
002a brfalse.s 51
002d callvirt Android.Views.Accessibility.AccessibilityManager::get_IsTouchExplorationEnabled
0032 ret

// VerticalCustomSlider.OnSliderValueChanged, MAUI DLL, RVA 0x3d58c
0049 callvirt Component.RemoteControl.Helpers.IAccessibilityHelper::IsAccessibilityEnabled
004e brfalse.s 86
0051 call Component.RemoteControl.MAUI.Views.CustomControls.VerticalCustomSlider::SliderValueChangeStopped
```

The readable pseudocode snippets above are CIL reconstructions. Original methods can be located by the exact METHOD header and RVA in the named `.dll.txt` files. Temporary analysis artifacts may disappear; the APK hash/version and method locations identify the evidence, but this repository does not vendor proprietary binaries/disassembly.

## 11. Unknowns and next experiments

- Installed Signia build, Android/OEM version, live common seek-node ID/actions/RangeInfo and touch exploration state.
- Whether set-progress reaches the accessibility commit branch despite MAUI listener order and rounding; aid receipt under ordinary and touch-exploration conditions.
- Configured maximum/volume mapping and acoustic address/profile for your confirmed acoustic setup.
- Full acoustic waveform reproduction, including CRC, pulse ordering, shaping and playback route. Defaults are insufficient for a reliable transmitter.
- BLE implementation questions are outside your setup and are not proposed next experiments.
- Mute/unmute boundary behavior, busy-request handling and program-specific cached values.

**Decision:** pursue the read-only node inspection followed by a reviewed one-action accessibility experiment. No further drag tuning and no Tasker project changes have been made. A reliable non-drag solution remains an experimental claim until the command commits and the actual aids respond.
