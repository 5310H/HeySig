# Tasker Profiles: HeySig

Because your project uses a "Dispatcher/Router" architecture, your Profiles are incredibly simple. Instead of having 20 different Voice Profiles for 20 different commands, you only need **one or two main profiles** that capture the raw voice text and pass it to your router task (`SIG_VoiceRouter`).

Here is how to set up the necessary profiles to interface your voice plugins with your tasks.

---

## 1. AutoVoice Integration (Main Voice Profile)

This profile listens for any command captured by AutoVoice (via Google Assistant, a home screen widget, etc.) and forwards the text to your router.

1.  Go to the **Profiles** tab in Tasker.
2.  Tap the `+` button -> **Event** -> **Plugin** -> **AutoVoice** -> **Recognized**.
3.  Tap the pencil icon to configure the AutoVoice plugin:
    *   **Command Filter:** Leave this blank (or set it to capture everything if required by your specific AutoVoice version). 
    *   *Note: If you want to require a wake word like "Hearing Aids", you can set the filter to `hearing aids (?<command>.+)` and use regex.*
    *   Tap the checkmark to save and exit the plugin config.
4.  Tasker will ask you to link a Task. Choose **`SIG_VoiceRouter`**.
5.  **Crucial Step:** We need to pass the spoken text into the router. 
    *   Open the `SIG_VoiceRouter` task.
    *   If you don't already have one, ensure the first action looks at the built-in AutoVoice variable: **`%avcommnofilter`** (which contains the exact words you spoke). 
    *   *Alternatively*, if you linked it using `Perform Task` from another intermediate task, you would set `%par1` to `%avcommnofilter`.

---

## 2. AutoWear Integration (Smartwatch Voice)

If you are using AutoWear to trigger commands from your wrist, the setup is nearly identical.

1.  Go to the **Profiles** tab.
2.  Tap `+` -> **Event** -> **Plugin** -> **AutoWear** -> **Command**.
3.  Tap the pencil icon to configure:
    *   **Command Filter:** This depends on how you set up your AutoWear Voice Screen. Usually, it passes a specific prefix like `&AP&` followed by the text.
    *   Tap the checkmark to save.
4.  Link the task: **`SIG_VoiceRouter`**.
5.  Inside your `SIG_VoiceRouter`, you will need to parse the AutoWear variable (usually **`%awmessage`** or **`%awcomm`**) to figure out what was spoken.

---

## 3. The Noise Smoothing Automation (Background Monitor)

*(As discussed in the Noise Smoothing document)*

This profile runs silently in the background to handle your automatic environment switching.

1.  Go to the **Profiles** tab.
2.  Tap `+` -> **Time**.
3.  Uncheck "From" and "To" (so it runs 24/7).
4.  Check **Repeat** and set it to: **`%SIG_MonitorFreq`** Minutes.
5.  Link the task: **`SIG_NoiseMonitor`**.

---

### How it all comes together:

By keeping your Profiles this simple, all of the "brainpower" is kept inside `SIG_VoiceRouter`. 

When you say *"Turn volume up"*:
1. The **AutoVoice Profile** triggers.
2. It sends the text *"Turn volume up"* to **`SIG_VoiceRouter`**.
3. `SIG_VoiceRouter` looks at the text, sees the word "volume" and "up", and uses a `Perform Task` action to run **`SIG_VolumeUp`**.
4. `SIG_VolumeUp` runs your AutoInput clicks.
