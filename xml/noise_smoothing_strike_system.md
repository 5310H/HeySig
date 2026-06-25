# Tasker Noise Smoothing: The Strike System

This document outlines how to build a "Strike System" in Tasker. This logic uses hysteresis to prevent your hearing aids from rapidly switching programs when the ambient noise level fluctuates near your threshold.

## The Concept

Instead of changing the hearing aid program immediately when a loud noise is detected, Tasker will require **multiple consecutive loud readings** over a period of time before it decides the environment has actually changed. 

*   A sudden loud noise (e.g., dropping a pan) = Ignored.
*   Sustained loud noise (e.g., entering a busy restaurant) = Switches to Noisy Program.

---

## Step 0: Initialize Your Configuration Variables

To make it easy to tweak your system from a central location, we will use Tasker Global Variables for everything you might want to adjust.

Run a one-time task (or add to your existing `SIG_init` task) with the following actions:

**Thresholds & Smoothing:**
*   `Variable Set` Name: `%SIG_NoiseHigh` To: `75` *(dB required to trigger noisy mode)*
*   `Variable Set` Name: `%SIG_NoiseLow` To: `60` *(dB required to trigger quiet mode)*
*   `Variable Set` Name: `%SIG_StrikeLimit` To: `3` *(Consecutive readings required to change)*
*   `Variable Set` Name: `%SIG_MonitorFreq` To: `2` *(How often to check in minutes)*

**Program Names:**
*   `Variable Set` Name: `%SIG_ProgNoisy` To: `Noisy Environment` *(Whatever text your app expects)*
*   `Variable Set` Name: `%SIG_ProgNormal` To: `Universal` *(Whatever text your app expects)*

---

## Step 1: Create the Noise Checking Task

Create a new Task named: `SIG_NoiseMonitor`

1.  **Action: Read Noise Level**
    *   *Add your chosen plugin action here to read the current dB level. This guide assumes the plugin outputs the level to a variable called `%noise_db`.*

2.  **Action: If (High Noise Detected)**
    *   Task -> `If`
    *   Condition: `%noise_db > %SIG_NoiseHigh` *(uses your preset variable)*

3.  **Action: Add High Noise Strike**
    *   Variables -> `Variable Add`
    *   Name: `%SIG_HighStrikes`
    *   Value: `1`

4.  **Action: Reset Low Noise Strikes**
    *   Variables -> `Variable Set`
    *   Name: `%SIG_LowStrikes`
    *   To: `0`

5.  **Action: Else If (Low Noise Detected)**
    *   Task -> `Else` *(Check the "If" box inside the Else action)*
    *   Condition: `%noise_db < %SIG_NoiseLow` *(uses your preset variable)*

6.  **Action: Add Low Noise Strike**
    *   Variables -> `Variable Add`
    *   Name: `%SIG_LowStrikes`
    *   Value: `1`

7.  **Action: Reset High Noise Strikes**
    *   Variables -> `Variable Set`
    *   Name: `%SIG_HighStrikes`
    *   To: `0`

8.  **Action: Else (Noise is fluctuating in the middle)**
    *   Task -> `Else` *(Do not check the "If" box this time)*

9.  **Action: Reset Both Strikes**
    *   Variables -> `Variable Set` `%SIG_HighStrikes` to `0`
    *   Variables -> `Variable Set` `%SIG_LowStrikes` to `0`

10. **Action: End If**
    *   Task -> `End If`

---

## Step 2: Trigger the Program Changes

Append these actions to the *same task* (`SIG_NoiseMonitor`). These actions evaluate the strikes and trigger your existing prototype tasks if the limit is reached.

11. **Action: If (High Strikes Reached)**
    *   Task -> `If`
    *   Condition: `%SIG_HighStrikes >= %SIG_StrikeLimit` *(This means it has been loud for your set consecutive checks)*

12. **Action: Switch to Noisy Program**
    *   Task -> `Perform Task`
    *   Name: `SIG_ProgramSwitch`
    *   Parameter 1 (`%par1`): `%SIG_ProgNoisy`

13. **Action: Reset High Strikes**
    *   Variables -> `Variable Set` `%SIG_HighStrikes` to `0` *(So it doesn't trigger again immediately on the next run)*

14. **Action: End If**
    *   Task -> `End If`

15. **Action: If (Low Strikes Reached)**
    *   Task -> `If`
    *   Condition: `%SIG_LowStrikes >= %SIG_StrikeLimit`

16. **Action: Switch to Normal Program**
    *   Task -> `Perform Task`
    *   Name: `SIG_ProgramSwitch`
    *   Parameter 1 (`%par1`): `%SIG_ProgNormal`

17. **Action: Reset Low Strikes**
    *   Variables -> `Variable Set` `%SIG_LowStrikes` to `0`

18. **Action: End If**
    *   Task -> `End If`

---

## Step 3: Create the Trigger Profile

Finally, create the automation profile that runs the monitor in the background.

1.  Go to the **Profiles** tab and create a new Profile.
2.  Select **Time**.
3.  Uncheck "From" and "To" so it can run all day (or set specific hours if you prefer to save battery at night).
4.  Check **Repeat** and set the time to your variable: `%SIG_MonitorFreq` Minutes.
5.  Link this profile to your new `SIG_NoiseMonitor` task.

> [!TIP]
> **Tuning the System:** 
> * If it takes too long to switch when you enter a loud room, change `%SIG_StrikeLimit` from `3` to `2`. 
> * If it still switches too erratically, increase the gap between your dB thresholds (e.g., change `%SIG_NoiseHigh` to `80` and `%SIG_NoiseLow` to `55`).
