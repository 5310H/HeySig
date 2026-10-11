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
    def scroll_list(self, direction, root=None):
        root = self.screen() if root is None else root
        lists = [n for n in root.iter('node') if n.get('scrollable') == 'true'
                 and n.get('class') != 'androidx.viewpager.widget.ViewPager']
        if not lists:
            raise RuntimeError('No scrollable list on the current screen')
        x1, y1, x2, y2 = map(int, re.findall(r'\d+', lists[-1].get('bounds')))
        x = str((x1 + x2) // 2)
        top = str(y1 + (y2 - y1) // 4)
        bottom = str(y2 - (y2 - y1) // 4)
        start, end = (bottom, top) if direction == 'up' else (top, bottom)
        self.run(['shell', 'input', 'swipe', x, start, x, end, '350'])
        time.sleep(.4)
    def select_tab(self, label):
        root = self.screen()
        node = next((n for n in root.iter('node') if n.get('text') == label), None)
        if node is None and any(n.get('text') in ('Import Task', 'Set Sort', 'Clear All', 'Filter') for n in root.iter('node')):
            self.run(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
            root = self.screen()
            node = next((n for n in root.iter('node') if n.get('text') == label), None)
        if node is None:
            raise RuntimeError('Missing Tasker tab: ' + label)
        # Tapping an already selected tab opens its context menu.
        if node.get('selected') != 'true':
            self.tap_node(node)

    def main(self):
        self.run(['shell','am','start','-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER','-p','net.dinglisch.android.taskerm'])
        time.sleep(.7)
        root=self.screen()
        for attempt in range(4):
            if any(n.get('text') in ('TASKS', 'Task Edit', 'Task File Select')
                   for n in root.iter('node')):
                break
            time.sleep(.5)
            root=self.screen()
        if any(n.get('text')=='Task File Select' for n in root.iter('node')):
            self.tap('Cancel', root); root=self.screen()
        if any(n.get('text')=='Task Edit' for n in root.iter('node')):
            self.run(['shell','input','keyevent','KEYCODE_BACK']);time.sleep(.6);root=self.screen()
        if any(n.get('content-desc')=='Apply' for n in root.iter('node')):
            self.tap('Apply',root)
        # A focused VARS filter can reopen the keyboard when Tasker resumes.
        # Our portrait list gestures otherwise land on the keyboard and never scroll.
        ime = self.run(['shell', 'dumpsys', 'input_method']).stdout.decode()
        if re.search(r'\bmInputShown=true\b', ime):
            self.run(['shell', 'input', 'keyevent', 'KEYCODE_BACK'])
            time.sleep(.3)
    def import_task(self,name):
        self.main()
        root = self.screen()
        if not any(n.get('text') == 'Import Task' for n in root.iter('node')):
            self.select_tab('TASKS')
            root = self.screen()
            if not any(n.get('text') == 'Import Task' for n in root.iter('node')):
                header = next(n for n in root.iter('node') if n.get('text') == 'TASKS')
                x1, y1, x2, y2 = map(int, re.findall(r'\d+', header.get('bounds')))
                x, y = str((x1 + x2) // 2), str((y1 + y2) // 2)
                self.run(['shell', 'input', 'swipe', x, y, x, y, '1500'])
                time.sleep(1)
        self.tap('Import Task')
        root = self.screen()
        for unused in range(6):self.scroll_list('down', root)
        for page in range(12):
            root=self.screen()
            node=next((n for n in root.iter('node') if n.get('text') in (name, name.removesuffix('.tsk.xml'))),None)
            if node is not None:
                self.tap_node(node)
                print('Imported '+name,flush=True)
                self.main()
                return
            self.scroll_list('up', root)
        raise RuntimeError('Task file not found: '+name)
    def run_task(self,name):
        self.main();self.select_tab('TASKS')
        root = self.screen()
        node = next((n for n in root.iter('node') if n.get('text') in (name, name.removesuffix('.tsk.xml'))), None)
        if node is not None:
            self.tap_node(node); self.tap('Play'); time.sleep(15)
            print('Ran ' + name, flush=True)
            return

        root = self.screen()
        for unused in range(6):self.scroll_list('down', root)
        for page in range(16):
            root=self.screen()
            node=next((n for n in root.iter('node') if n.get('text') in (name, name.removesuffix('.tsk.xml'))),None)
            if node is not None:
                self.tap_node(node);self.tap('Play');time.sleep(15)
                print('Ran '+name,flush=True)
                return
            self.scroll_list('up', root)
        raise RuntimeError('Task not found: '+name)
    def variables(self,wanted):
        self.main();self.select_tab('VARS')
        values={}
        # Return to the top before reading the alphabetically sorted list.
        for unused in range(5):self.scroll_list('down')
        for page in range(14):
            root=self.screen()
            for n in root.iter('node'):
                kids=list(n)
                if kids and kids[0].get('text') in wanted:
                    values[kids[0].get('text')]=' | '.join(k.get('text','') for k in kids[1:])
            if len(values)==len(wanted):return values
            self.scroll_list('up', root)
        return values
