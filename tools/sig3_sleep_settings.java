/* Select programs and clock times without changing the current hearing program. */
import android.app.Activity;
import android.app.AlertDialog;
import android.app.TimePickerDialog;
import android.content.DialogInterface;
import android.widget.*;
import android.view.View;
import android.os.Handler;
import android.os.Looper;
import java.util.function.Consumer;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

names = new String[7]; names[0] = "Choose a program";
for (i = 1; i <= 6; i++) {
    name = tasker.getVariable("SIG3_ProgramName" + i);
    if (name == null || name.trim().length() == 0 || name.startsWith("%"))
        throw new Exception("Configure all six program names before opening sleep settings");
    names[i] = name;
}
selected = new int[] {0, 0};
for (i = 0; i < 2; i++) {
    value = tasker.getVariable(i == 0 ? "SIG3_SleepProgram" : "SIG3_WakeProgram");
    if (value != null && value.matches("[1-6]")) selected[i] = Integer.parseInt(value);
}
times = new String[] {"22.00", "07.00"};
for (i = 0; i < 2; i++) {
    value = tasker.getVariable(i == 0 ? "SIG3_SleepTime" : "SIG3_WakeTime");
    if (value != null && value.matches("(?:[01][0-9]|2[0-3])\\.[0-5][0-9]")) times[i] = value;
}
decision = new AtomicReference("cancel"); activityRef = new AtomicReference(); dialogRef = new AtomicReference();
done = new CountDownLatch(1); ui = new Handler(Looper.getMainLooper());
tasker.setVariable("sig3_sleep_settings_decision", "cancel");
try {
    tasker.doWithActivity(new Consumer() {
        accept(Object value) {
            final Activity screen = (Activity) value; activityRef.set(screen);
            layout = new LinearLayout(screen); layout.setOrientation(LinearLayout.VERTICAL);
            padding = (int) (20 * screen.getResources().getDisplayMetrics().density);
            layout.setPadding(padding, padding, padding, padding);
            sleepLabel = new TextView(screen); sleepLabel.setText("Sleep program"); layout.addView(sleepLabel);
            sleepProgram = new Spinner(screen);
            sleepProgram.setAdapter(new ArrayAdapter(screen, android.R.layout.simple_spinner_dropdown_item, names));
            sleepProgram.setSelection(selected[0]); layout.addView(sleepProgram);
            sleepTime = new Button(screen); sleepTime.setText("Sleep time: " + times[0].replace('.', ':')); layout.addView(sleepTime);
            sleepTime.setOnClickListener(new View.OnClickListener() {
                onClick(View view) {
                    new TimePickerDialog(screen, new TimePickerDialog.OnTimeSetListener() {
                        onTimeSet(TimePicker picker, int hour, int minute) {
                            times[0] = String.format(java.util.Locale.US, "%02d.%02d", hour, minute);
                            sleepTime.setText("Sleep time: " + times[0].replace('.', ':'));
                        }
                    }, Integer.parseInt(times[0].substring(0, 2)), Integer.parseInt(times[0].substring(3)), true).show();
                }
            });
            wakeLabel = new TextView(screen); wakeLabel.setText("Wake program"); layout.addView(wakeLabel);
            wakeProgram = new Spinner(screen);
            wakeProgram.setAdapter(new ArrayAdapter(screen, android.R.layout.simple_spinner_dropdown_item, names));
            wakeProgram.setSelection(selected[1]); layout.addView(wakeProgram);
            wakeTime = new Button(screen); wakeTime.setText("Wake time: " + times[1].replace('.', ':')); layout.addView(wakeTime);
            wakeTime.setOnClickListener(new View.OnClickListener() {
                onClick(View view) {
                    new TimePickerDialog(screen, new TimePickerDialog.OnTimeSetListener() {
                        onTimeSet(TimePicker picker, int hour, int minute) {
                            times[1] = String.format(java.util.Locale.US, "%02d.%02d", hour, minute);
                            wakeTime.setText("Wake time: " + times[1].replace('.', ':'));
                        }
                    }, Integer.parseInt(times[1].substring(0, 2)), Integer.parseInt(times[1].substring(3)), true).show();
                }
            });
            note = new TextView(screen);
            note.setText("Times use the phone's local clock. Save keeps automation off; enable it after schedule verification.");
            layout.addView(note);
            dialog = new AlertDialog.Builder(screen).setTitle("HeySig3 sleep settings").setView(layout)
                .setPositiveButton("Save", null).setNegativeButton("Cancel", null).create();
            dialogRef.set(dialog); dialog.setCancelable(true);
            dialog.setOnDismissListener(new DialogInterface.OnDismissListener() {
                onDismiss(DialogInterface dialog) { done.countDown(); screen.finish(); }
            });
            dialog.show();
            dialog.getButton(DialogInterface.BUTTON_POSITIVE).setOnClickListener(new View.OnClickListener() {
                onClick(View view) {
                    if (sleepProgram.getSelectedItemPosition() == 0 || wakeProgram.getSelectedItemPosition() == 0) {
                        Toast.makeText(screen, "Choose both programs", Toast.LENGTH_SHORT).show(); return;
                    }
                    if (times[0].equals(times[1])) {
                        Toast.makeText(screen, "Choose different sleep and wake times", Toast.LENGTH_SHORT).show(); return;
                    }
                    selected[0] = sleepProgram.getSelectedItemPosition(); selected[1] = wakeProgram.getSelectedItemPosition();
                    decision.set("save"); dialog.dismiss();
                }
            });
        }
    });
    if (done.await(180, TimeUnit.SECONDS) && "save".equals(decision.get())) {
        tasker.setVariable("sig3_sleep_program_choice", "" + selected[0]);
        tasker.setVariable("sig3_wake_program_choice", "" + selected[1]);
        tasker.setVariable("sig3_sleep_time_choice", times[0]); tasker.setVariable("sig3_wake_time_choice", times[1]);
        tasker.setVariable("sig3_sleep_settings_decision", "save");
    }
} finally {
    ui.post(new Runnable() {
        run() {
            dialog = dialogRef.get(); if (dialog != null && dialog.isShowing()) dialog.dismiss();
            screen = activityRef.get(); if (screen != null && !screen.isFinishing()) screen.finish();
        }
    });
}
return tasker.getVariable("sig3_sleep_settings_decision");
