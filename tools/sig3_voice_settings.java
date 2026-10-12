/* Show separate visible on/off controls; Cancel leaves preferences unchanged. */
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Handler;
import android.os.Looper;
import java.util.function.Consumer;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

selected = new boolean[] {"1".equals(tasker.getVariable("SIG3_VoiceResponses")), "1".equals(tasker.getVariable("SIG3_VoicePrompts"))};
decision = new AtomicReference("cancel"); activityRef = new AtomicReference(); dialogRef = new AtomicReference(); done = new CountDownLatch(1);
ui = new Handler(Looper.getMainLooper());
tasker.setVariable("sig3_voice_settings_decision", "cancel");
try {
    tasker.doWithActivity(new Consumer() {
        accept(Object value) {
            final Activity screen = (Activity) value; activityRef.set(screen);
            dialog = new AlertDialog.Builder(screen).setTitle("HeySig3 voice settings")
                .setMultiChoiceItems(new String[] {"Spoken results", "Voice prompts"}, selected, new DialogInterface.OnMultiChoiceClickListener() {
                    onClick(DialogInterface dialog, int which, boolean checked) { selected[which] = checked; }
                }).setPositiveButton("Save", new DialogInterface.OnClickListener() {
                    onClick(DialogInterface dialog, int which) { decision.set("save"); }
                }).setNegativeButton("Cancel", null).create();
            dialogRef.set(dialog); dialog.setCancelable(true);
            dialog.setOnDismissListener(new DialogInterface.OnDismissListener() {
                onDismiss(DialogInterface dialog) { done.countDown(); screen.finish(); }
            });
            dialog.show();
        }
    });
    if (done.await(60, TimeUnit.SECONDS) && "save".equals(decision.get())) {
        tasker.setVariable("sig3_voice_results_choice", selected[0] ? "1" : "0");
        tasker.setVariable("sig3_voice_prompts_choice", selected[1] ? "1" : "0");
        tasker.setVariable("sig3_voice_settings_decision", "save");
    }
} finally {
    ui.post(new Runnable() {
        run() {
            dialog = dialogRef.get(); if (dialog != null && dialog.isShowing()) dialog.dismiss();
            screen = activityRef.get(); if (screen != null && !screen.isFinishing()) screen.finish();
        }
    });
}
return tasker.getVariable("sig3_voice_settings_decision");
