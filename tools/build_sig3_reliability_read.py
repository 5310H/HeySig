"""Build a temporary read-only persistence snapshot task in /tmp."""
import sys,xml.etree.ElementTree as E
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_heysig3 as b
code='''import org.json.*;import java.io.*;
j=new JSONObject();j.put("time",System.currentTimeMillis());j.put("uptimeMillis",android.os.SystemClock.elapsedRealtime());
for(name:new String[]{"noise","sleep","voice"})j.put(name,new JSONObject(context.getSharedPreferences("heysig3-"+name,0).getAll()));
for(key:new String[]{"NoiseEnabled","NoiseMode","NoiseSettingsReady","NoiseLow","NoiseHigh","NoiseHysteresis","NoiseStrikeLimit","NoiseCooldownSeconds","WakeEnabled","SleepEnabled","VoiceResponses","VoicePrompts","NoiseLogEnabled"}){v=tasker.getVariable("SIG3_"+key);j.put(key,v==null||v.startsWith("%")?"":v);}
f=new File(context.getFilesDir(),"heysig3-settings-v1.json");if(f.isFile()){in=new FileInputStream(f);bytes=new byte[(int)f.length()];in.read(bytes);in.close();d=java.security.MessageDigest.getInstance("SHA-256").digest(bytes);hex="";for(x:d)hex+=String.format("%02x",new Object[]{new Integer(x&255)});j.put("snapshotSHA256",hex);}
out=new FileOutputStream("/sdcard/Tasker/sig3-reliability-snapshot.json");out.write(j.toString(2).getBytes("UTF-8"));out.close();return "read-only reliability snapshot";'''
a=[b.java_code(code)];r=E.Element('TaskerData',sr='',dvi='1',tv='6.6.20');r.append(b.task('00_SIG3_ReliabilityRead',9930,a));E.ElementTree(r).write('/tmp/00_sig3_reliability_read.tsk.xml',encoding='utf-8',xml_declaration=True)
