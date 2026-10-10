"""ADB helper for importing and testing SIG3 tasks on an authorized phone."""
import subprocess
import time
import re
import xml.etree.ElementTree as E

class PhoneUI:
    def __init__(self, serial):
        self.adb = ['adb', '-s', serial]
    def run(self, args):
        return subprocess.run(self.adb + args, capture_output=True, check=True, timeout=40)
    def screen(self):
        self.run(['shell', 'uiautomator', 'dump', '/sdcard/heysig-window.xml'])
        return E.fromstring(self.run(['shell', 'cat', '/sdcard/heysig-window.xml']).stdout)
    def tap_node(self, node):
        x1,y1,x2,y2 = map(int,re.findall(r'\d+',node.get('bounds')))
        self.run(['shell','input','tap',str((x1+x2)//2),str((y1+y2)//2)])
        time.sleep(.6)
    def tap(self, label, root=None):
        root = self.screen() if root is None else root
        node = next((n for n in root.iter('node') if n.get('text')==label or n.get('content-desc')==label),None)
        if node is None:
            raise RuntimeError('Missing control: '+label+'; visible: '+str([n.get('text') or n.get('content-desc') for n in root.iter('node') if n.get('text') or n.get('content-desc')]))
        self.tap_node(node)
    def main(self):
        self.run(['shell','am','start','-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER','-p','net.dinglisch.android.taskerm'])
        time.sleep(.7)
        root=self.screen()
        if any(n.get('text')=='Task File Select' for n in root.iter('node')):
            self.tap('Cancel', root); root=self.screen()
        if any(n.get('text')=='Task Edit' for n in root.iter('node')):
            self.run(['shell','input','keyevent','KEYCODE_BACK']);time.sleep(.6);root=self.screen()
        if any(n.get('content-desc')=='Apply' for n in root.iter('node')):
            self.tap('Apply',root)
    def import_task(self,name):
        self.main()
        self.run(['shell','input','swipe','405','354','405','354','900'])
        self.tap('Import Task')
        for unused in range(6):self.run(['shell','input','swipe','730','700','730','1950','200'])
        for page in range(12):
            root=self.screen()
            node=next((n for n in root.iter('node') if n.get('text') in (name, name.removesuffix('.tsk.xml'))),None)
            if node is not None:
                self.tap_node(node)
                print('Imported '+name,flush=True)
                self.main()
                return
            self.run(['shell','input','swipe','740','1900','740','700','400'])
        raise RuntimeError('Task file not found: '+name)
    def run_task(self,name):
        self.main();self.tap('TASKS')
        for unused in range(6):self.run(['shell','input','swipe','730','700','730','1950','200'])
        for page in range(16):
            root=self.screen()
            node=next((n for n in root.iter('node') if n.get('text') in (name, name.removesuffix('.tsk.xml'))),None)
            if node is not None:
                self.tap_node(node);self.tap('Play');time.sleep(15)
                print('Ran '+name,flush=True)
                return
            self.run(['shell','input','swipe','730','1960','730','700','400'])
        raise RuntimeError('Task not found: '+name)
    def variables(self,wanted):
        self.main();self.tap('VARS')
        values={}
        # Return to the top before reading the alphabetically sorted list.
        for unused in range(5):self.run(['shell','input','swipe','730','700','730','1950','200'])
        for page in range(14):
            root=self.screen()
            for n in root.iter('node'):
                kids=list(n)
                if kids and kids[0].get('text') in wanted:
                    values[kids[0].get('text')]=' | '.join(k.get('text','') for k in kids[1:])
            if len(values)==len(wanted):return values
            self.run(['shell','input','swipe','730','1700','730','1100','600'])
        return values
