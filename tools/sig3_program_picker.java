/* BEGIN PICKER DETECTION */
pickerProgram(root) {
    if(root==null||root.getPackageName()==null||!"com.signia.rta".contentEquals(root.getPackageName()))return "";
    queue=new java.util.ArrayList();queue.add(root);heading=0;selected=0;program="";
    for(scan=0;scan<queue.size()&&scan<300;scan++) {
        node=queue.get(scan);
        if(node.isVisibleToUser()&&node.isEnabled()) {
            text=node.getText();description=node.getContentDescription();
            if(text!=null&&"Programs".equals(text.toString()))heading++;
            if(description!=null&&description.toString().endsWith(" Selected Button")) {
                name=description.toString().substring(0,description.toString().length()-" Selected Button".length());
                matches=0;for(slot=1;slot<=6;slot++)if(name.equals(tasker.getVariable("SIG3_ProgramName"+slot)))matches++;
                if(matches!=1)throw new JavaCodeException("Program picker selection is not uniquely configured");
                selected++;program=name;
            }
        }
        for(childIndex=0;childIndex<node.getChildCount();childIndex++) {
            child=node.getChild(childIndex);if(child!=null)queue.add(child);
        }
    }
    if(queue.size()>300)throw new JavaCodeException("Program picker tree exceeds inspection limit");
    if(heading==0)return "";
    if(heading!=1||selected!=1)throw new JavaCodeException("Cannot identify selected program in picker");
    return program;
}
/* END PICKER DETECTION */
controlsLabel(root) {
    if(root==null||root.getPackageName()==null||!"com.signia.rta".contentEquals(root.getPackageName()))return "";
    queue=new java.util.ArrayList();queue.add(root);labels=0;headers=0;label="";header="";
    id=tasker.getVariable("SIG3_ProgramId");
    for(scan=0;scan<queue.size()&&scan<300;scan++) {
        node=queue.get(scan);
        if(node.isVisibleToUser()&&node.isEnabled()) {
            text=node.getText();description=node.getContentDescription();
            if(id!=null&&id.equals(node.getViewIdResourceName())&&text!=null&&text.toString().trim().length()>0){labels++;label=text.toString().trim();}
            if(description!=null&&description.toString().startsWith("Hearing program ")&&description.toString().endsWith(" Active")) {
                headers++;header=description.toString().substring(16,description.toString().length()-7).trim();
            }
        }
        for(i=0;i<node.getChildCount();i++){child=node.getChild(i);if(child!=null)queue.add(child);}
    }
    if(queue.size()>300||headers>1||labels>1)return "";
    if(labels==1&&(headers==0||label.equals(header)))return label;
    return labels==0&&headers==1?header:"";
}
prepareProgramRead(service) {
    root=service.getRootInActiveWindow();picker=pickerProgram(root);
    if(root==null||root.getPackageName()==null||!"com.signia.rta".contentEquals(root.getPackageName()))throw new JavaCodeException("Signia is not foreground");
    queue=new java.util.ArrayList();queue.add(root);battery=0;pageId=tasker.getVariable("SIG3_BatteryPageId");
    for(scan=0;scan<queue.size()&&scan<300;scan++) {
        node=queue.get(scan);
        if(node.isVisibleToUser()&&node.isEnabled()&&pageId!=null&&pageId.equals(node.getViewIdResourceName()))battery++;
        for(i=0;i<node.getChildCount();i++){child=node.getChild(i);if(child!=null)queue.add(child);}
    }
    if(queue.size()>300||battery>1||(battery==1&&picker.length()>0))throw new JavaCodeException("Signia page is ambiguous");
    if(battery==0&&picker.length()==0)return root;
    if(!service.performGlobalAction(1))throw new JavaCodeException("Could not return to Signia Controls");
    for(attempt=0;attempt<20;attempt++) {
        android.os.SystemClock.sleep(150);root=service.getRootInActiveWindow();current=controlsLabel(root);
        if(current.length()>0) {
            if(picker.length()>0&&!picker.equals(current))throw new JavaCodeException("Program changed while returning to Controls; retry");
            return root;
        }
    }
    throw new JavaCodeException("Signia Controls did not return; open Controls and retry");
}
