/* Read-only app foreground check: avoid relaunching an already active Signia window. */
service = tasker.getAccessibilityService();
root = service == null ? null : service.getRootInActiveWindow();
foreground = root != null && root.getPackageName() != null && "com.signia.rta".contentEquals(root.getPackageName());
tasker.setVariable("SIG3_AppAlreadyForeground", foreground ? "1" : "0");
return foreground ? "already foreground" : "launch required";
