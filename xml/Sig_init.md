# Tasker Task: `SIG_init`

This initialization task sets up all the Global Variables required for your HeySig project. Running this task once will populate everything your other tasks need, acting like a central configuration file.

To build this in Tasker, simply create a new task named `SIG_init` and add a **Variable Set** action for each item below.

---

### Core Noise Variables (From your existing setup)

*   `Variable Set` Name: **`%SIG_NoiseRaw`** To: `0`
*   `Variable Set` Name: **`%SIG_Noise`** To: `0`
*   `Variable Set` Name: **`%SIG_NoiseTier`** To: `quiet`
*   `Variable Set` Name: **`%SIG_Mode`** To: `quiet`
*   `Variable Set` Name: **`%SIG_LastMode`** To: `quiet`
*   `Variable Set` Name: **`%SIG_LastTier`** To: `quiet`
*   `Variable Set` Name: **`%SIG_LastNoise`** To: `0`
*   `Variable Set` Name: **`%SIG_NoiseTrend`** To: `stable`
*   `Variable Set` Name: **`%SIG_NoiseDelta`** To: `0`

### Program & Override States

*   `Variable Set` Name: **`%SIG_Freeze`** To: `0`
*   `Variable Set` Name: **`%SIG_OverrideTimer`** To: `0`
*   `Variable Set` Name: **`%SIG_OverrideMode`** To: `none`
*   `Variable Set` Name: **`%SIG_ChangeCount`** To: `0`
*   `Variable Set` Name: **`%SIG_Debug`** To: `0`
*   `Variable Set` Name: **`%SIG_Log`** To: `0`

### Program Name Configs

*   `Variable Set` Name: **`%SIG_ProgramQuiet`** To: `0` *(Change '0' to your quiet program name/id)*
*   `Variable Set` Name: **`%SIG_ProgramMedium`** To: `0` *(Change '0' to your medium program name/id)*
*   `Variable Set` Name: **`%SIG_ProgramLoud`** To: `0` *(Change '0' to your loud program name/id)*

---

### NEW: Noise Smoothing Configs

These handle the "Strike System" automation.

*   `Variable Set` Name: **`%SIG_NoiseHigh`** To: `75` *(dB threshold to trigger noisy mode)*
*   `Variable Set` Name: **`%SIG_NoiseLow`** To: `60` *(dB threshold to trigger quiet mode)*
*   `Variable Set` Name: **`%SIG_StrikeLimit`** To: `3` *(Consecutive readings required to change)*
*   `Variable Set` Name: **`%SIG_MonitorFreq`** To: `2` *(How often to poll the noise in minutes)*

---

### NEW: UI & AutoInput Configs

These will prevent your project from breaking if the Signia app updates or if you change phones.

**Tab Labels:**
*   `Variable Set` Name: **`%SIG_UITabTinnitus`** To: `Tinnitus`
*   `Variable Set` Name: **`%SIG_UITabVolume`** To: `Volume`
*   `Variable Set` Name: **`%SIG_UITabBalance`** To: `Balance`

**Timing & Limits:**
*   `Variable Set` Name: **`%SIG_WaitAppLoad`** To: `2` *(Seconds to wait for the app to open)*
*   `Variable Set` Name: **`%SIG_WaitUI`** To: `500` *(Milliseconds to wait between clicks)*
*   `Variable Set` Name: **`%SIG_MaxVolume`** To: `15` *(Maximum steps in the volume loop)*
*   `Variable Set` Name: **`%SIG_MaxTinnitus`** To: `15` *(Maximum steps in the tinnitus loop)*
*   `Variable Set` Name: **`%SIG_MaxBalance`** To: `15` *(Maximum steps in the balance loop)*

**App Details:**
*   `Variable Set` Name: **`%SIG_AppPackage`** To: `com.signia.rta` *(The Android package name for the Signia app)*
