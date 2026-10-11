/* Reopen recognition only after an explicit Try again choice. */
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.os.Handler;
import android.os.Looper;
import java.util.function.Consumer;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

choice = new AtomicReference("cancel");
activityRef = new AtomicReference();
dialogRef = new AtomicReference();
done = new CountDownLatch(1);
ui = new Handler(Looper.getMainLooper());
tasker.setVariable("sig3_retry", "cancel");
heard = tasker.getVariable("SIG3_VoiceHeard");
message = heard == null || heard.length() == 0 || heard.startsWith("%")
    ? "No command was recognized. Try speaking again?"
    : "I heard: " + heard + "\nThat command was not recognized. Try speaking again?";
try {
    tasker.doWithActivity(new Consumer() {
        accept(Object value) {
            final Activity screen = (Activity) value;
            activityRef.set(screen);
            buttons = new DialogInterface.OnClickListener() {
                onClick(DialogInterface dialog, int which) {
                    if (which == DialogInterface.BUTTON_POSITIVE) choice.set("retry");
                }
            };
            dialog = new AlertDialog.Builder(screen).setTitle("HeySig3 voice")
                .setMessage(message).setPositiveButton("Try again", buttons)
                .setNegativeButton("Cancel", buttons).create();
            dialogRef.set(dialog);
            dialog.setOnDismissListener(new DialogInterface.OnDismissListener() {
                onDismiss(DialogInterface dialog) {
                    done.countDown();
                    screen.finish();
                }
            });
            dialog.show();
        }
    });
    if (done.await(60, TimeUnit.SECONDS)) tasker.setVariable("sig3_retry", choice.get());
} finally {
    ui.post(new Runnable() {
        run() {
            dialog = dialogRef.get();
            if (dialog != null && dialog.isShowing()) dialog.dismiss();
            screen = activityRef.get();
            if (screen != null && !screen.isFinishing()) screen.finish();
        }
    });
}
return tasker.getVariable("sig3_retry");
