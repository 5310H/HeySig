/* Select roles and noise-index tuning without changing hearing programs. */
import android.app.*;
import android.content.DialogInterface;
import android.widget.*;
import android.view.View;
import android.os.*;
import java.util.function.Consumer;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicReference;
names=new String[7];names[0]="Choose a program";
for(i=1;i<=6;i++) { name=tasker.getVariable("SIG3_ProgramName"+i);if(name==null||name.trim().length()==0||name.startsWith("%")) throw new Exception("Configure all six program names");names[i]=name; }
labels=new String[]{"Quiet program","Noisy program","Very noisy program"};
roleKeys=new String[]{"QuietProgram","MiddleProgram","LoudProgram"};
fieldKeys=new String[]{"low","high","margin","strikes","cooldown"};
fieldGlobals=new String[]{"Low","High","Hysteresis","StrikeLimit","CooldownSeconds"};
fieldLabels=new String[]{"Quiet/noisy boundary","Noisy/very-noisy boundary","Hysteresis margin","Consecutive samples","Cooldown seconds"};
defaults=new String[]{"","","3","3","60"};
choices=new String[8];confirmed=new boolean[]{false};
decision=new AtomicReference("cancel");activityRef=new AtomicReference();dialogRef=new AtomicReference();done=new CountDownLatch(1);ui=new Handler(Looper.getMainLooper());
tasker.setVariable("sig3_noise_settings_decision","cancel");
try {
 tasker.doWithActivity(new Consumer() {
  accept(Object value) {
   final Activity screen=(Activity)value;activityRef.set(screen);
   layout=new LinearLayout(screen);layout.setOrientation(LinearLayout.VERTICAL);padding=(int)(16*screen.getResources().getDisplayMetrics().density);layout.setPadding(padding,padding,padding,padding);
   note=new TextView(screen);note.setText("Phone noise index, not calibrated decibels. Choose thresholds after observation. Save leaves switching off.");layout.addView(note);
   selectors=new Spinner[3];
   for(i=0;i<3;i++) {
    label=new TextView(screen);label.setText(labels[i]);layout.addView(label);
    selectors[i]=new Spinner(screen);selectors[i].setAdapter(new ArrayAdapter(screen,android.R.layout.simple_spinner_dropdown_item,names));
    saved=tasker.getVariable("SIG3_Noise"+roleKeys[i]);if(saved!=null&&saved.matches("[1-6]"))selectors[i].setSelection(Integer.parseInt(saved));layout.addView(selectors[i]);
   }
   inputs=new EditText[5];
   for(i=0;i<5;i++) {
    label=new TextView(screen);label.setText(fieldLabels[i]);layout.addView(label);
    inputs[i]=new EditText(screen);inputs[i].setSingleLine(true);inputs[i].setInputType(8194|4096);
    saved=tasker.getVariable("SIG3_Noise"+fieldGlobals[i]);inputs[i].setText(saved==null||saved.startsWith("%")||saved.length()==0?defaults[i]:saved);layout.addView(inputs[i]);
   }
   check=new CheckBox(screen);check.setText("I checked that louder sound gives a higher noise index");check.setChecked("1".equals(tasker.getVariable("SIG3_NoiseScaleConfirmed")));layout.addView(check);
   scroll=new ScrollView(screen);scroll.addView(layout);
   dialog=new AlertDialog.Builder(screen).setTitle("HeySig3 noise settings").setView(scroll).setPositiveButton("Save",null).setNegativeButton("Cancel",null).create();dialogRef.set(dialog);
   dialog.setOnDismissListener(new DialogInterface.OnDismissListener(){onDismiss(DialogInterface d){done.countDown();screen.finish();}});
   dialog.show();
   dialog.getButton(DialogInterface.BUTTON_POSITIVE).setOnClickListener(new View.OnClickListener(){
    onClick(View v) {
     for(i=0;i<3;i++)if(selectors[i].getSelectedItemPosition()==0){Toast.makeText(screen,"Choose all three programs",Toast.LENGTH_SHORT).show();return;}
     try {
      lo=Double.parseDouble(inputs[0].getText().toString());hi=Double.parseDouble(inputs[1].getText().toString());m=Double.parseDouble(inputs[2].getText().toString());count=Integer.parseInt(inputs[3].getText().toString());cool=Integer.parseInt(inputs[4].getText().toString());
      if(Double.isNaN(lo)||Double.isNaN(hi)||Double.isNaN(m)||Double.isInfinite(lo)||Double.isInfinite(hi)||Double.isInfinite(m)||lo>=hi||m<0||2*m>=hi-lo||count<1||count>20||cool<0||cool>3600)throw new Exception("Invalid tuning");
     }catch(Exception e){Toast.makeText(screen,"Check thresholds, margin, sample count and cooldown",Toast.LENGTH_LONG).show();return;}
     for(i=0;i<3;i++)choices[i]=""+selectors[i].getSelectedItemPosition();
     for(i=0;i<5;i++)choices[3+i]=inputs[i].getText().toString().trim();
     confirmed[0]=check.isChecked();decision.set("save");dialog.dismiss();
    }
   });
  }
 });
 if(done.await(180,TimeUnit.SECONDS)&&"save".equals(decision.get())) {
  for(i=0;i<3;i++)tasker.setVariable("sig3_noise_choice_"+new String[]{"quiet","middle","loud"}[i],choices[i]);
  for(i=0;i<5;i++)tasker.setVariable("sig3_noise_choice_"+fieldKeys[i],choices[3+i]);
  tasker.setVariable("sig3_noise_choice_confirmed",confirmed[0]?"1":"0");tasker.setVariable("sig3_noise_settings_decision","save");
 }
}finally{ui.post(new Runnable(){run(){d=dialogRef.get();if(d!=null&&d.isShowing())d.dismiss();a=activityRef.get();if(a!=null&&!a.isFinishing())a.finish();}});}
return tasker.getVariable("sig3_noise_settings_decision");
