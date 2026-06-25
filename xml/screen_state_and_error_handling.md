# Tasker Improvement: Non-Interruptive Execution & Error Handling

Since your project relies heavily on AutoInput to control the Signia app, there are two major quality-of-life improvements you should consider implementing to make the system feel flawless.

## 1. Non-Interruptive Screen Checks

AutoInput requires the screen to be on and unlocked. If the background Noise Monitor triggers a program switch while you are in the middle of typing a text message, AutoInput will suddenly rip you out of your text and open the Signia app. This is very jarring!

To fix this, we can create a "wrapper" task that checks what you are doing before it runs an AutoInput action.

### Create Task: `SIG_SafeExecute`
This task will decide *how* to run your other tasks based on the screen state.

1.  **Action: Test Display**
    *   Type: `State`
    *   Store Result In: `%screen_state`
2.  **Action: If (Screen is OFF)**
    *   Condition: `%screen_state ~ off`
3.  **Action: Turn On & Unlock**
    *   Use AutoInput `Unlock Screen` (or Tasker's `Turn On` + Keyguard actions).
4.  **Action: Perform Task**
    *   Name: `%par1` *(We will pass the name of the task we want to run, like `SIG_VolumeUp`, into this parameter)*
5.  **Action: System Lock (Turn screen back off)**
    *   *(Only turn it off if we were the ones who turned it on)*
6.  **Action: Else (Screen is ON)**
7.  **Action: AutoTools Web Screen / Tasker Scene**
    *   Instead of interrupting, flash a small, non-intrusive popup: "Switching Hearing Aid Program. Tap to cancel."
    *   Timeout: 3 Seconds.
8.  **Action: If (Not Canceled)**
    *   **Action: Perform Task** -> `%par1`
9.  **Action: End If**

**How to use it:** Instead of your Voice Router calling `SIG_VolumeUp` directly, it calls `SIG_SafeExecute` and passes `SIG_VolumeUp` as `%par1`. 

---

## 2. AutoInput Error Recovery

Sometimes the Signia app might take too long to load, or a random "Rate this App" popup might appear, causing AutoInput to fail.

Tasker has built-in error handling that you should enable on your AutoInput actions.

1.  Open any AutoInput `Click` action in your tasks (e.g., in `SIG_VolumeUp`).
2.  Check the box for **"Continue Task After Error"**.
3.  Add a new action immediately after it: **If (`%err` is set)**
4.  If an error occurred, `%err` will contain an error code. 
5.  **Recovery Actions:** Inside the If statement, you can add actions to:
    *   Flash a message: "Signia App Error. Retrying..."
    *   Use AutoInput `Global Action` -> `Back` (to clear any popups).
    *   Use `Go To` action to loop back and try the click again (up to a maximum of 3 retries).
6.  **End If**

Implementing these two concepts will take your project from a "prototype" to a robust, bulletproof system that runs silently in the background without frustrating you!
