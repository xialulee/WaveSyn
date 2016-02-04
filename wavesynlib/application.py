# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: Feng-cong Li. xialulee@sina.com
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def dependencies_for_my_program():
    '''This function is used to solve the bugs of py2exe'''
    from scipy.sparse.csgraph   import _validation 
    from scipy.special          import _ufuncs_cxx

import thread
import threading
import Queue

import os
import os.path
import sys
REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr

import six
from six.moves.tkinter import *
from six.moves.tkinter_ttk import *

import six.moves.tkinter_tix as Tix
from six.moves.tkinter import Frame
from six.moves.tkinter_tkfiledialog import asksaveasfilename


import matplotlib
matplotlib.use('TkAgg')

from numpy import *


from datetime import datetime
from inspect import getsourcefile
import webbrowser
import subprocess
import json
import traceback

# Some console functionalities are implemented by idlelib
##########################
from idlelib.AutoComplete import AutoComplete
import idlelib.AutoCompleteWindow
idlelib.AutoCompleteWindow.KEYPRESS_SEQUENCES = ()
from idlelib.Percolator import Percolator
from idlelib.ColorDelegator import ColorDelegator
##########################

from wavesynlib.guicomponents.tk import CWDIndicator, TaskbarIcon, ScrolledText, ValueChecker, PILImageFrame
from wavesynlib.interfaces.clipboard.modelnode import Clipboard
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.editor.externaleditor import EditorDict, EditorNode
from wavesynlib.stdstream import StreamManager
#from wavesynlib.cuda                             import Worker as CUDAWorker
from wavesynlib.languagecenter.utils import auto_subs, eval_format, set_attributes, get_caller_dir
from wavesynlib.languagecenter.designpatterns import Singleton, SimpleObserver        
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.modelnode import LangCenterNode
from wavesynlib.languagecenter import templates
from wavesynlib.languagecenter import timeutils
from wavesynlib.languagecenter import datatypes
from wavesynlib.toolwindows.interrupter.modelnode import InterrupterNode
from wavesynlib.status import busy_doing


def make_menu(win, menu, json=False):
    def func_gen(code, print_code=True):
        if print_code:
            f   = Application.instance.print_and_eval
        else:
            f   = Application.instance.eval
        return lambda: f(code)
        
    def make(top, tree):
        for top_item in tree:
            if 'Command' in top_item:
                if json: # json cannot store callable objects.
                    print_code = top_item.get('Print', True)
                    cmd = func_gen(top_item['Command'], print_code)
                else:
                    # Python data object can store callable object, 
                    # and top_item['Command'] should be a callable object in this circumstance.
                    cmd = top_item['Command'] 
                top.add_command(label=top_item['Name'], command=cmd, underline=top_item['UnderLine'])
            else:
                tearoff = 1 if 'TearOff' not in top_item else int(top_item['TearOff'])
                submenu = Menu(top, tearoff=tearoff)
                make(submenu, top_item['SubMenu']) # recursion
                top.add_cascade(label=top_item['Name'], menu=submenu, underline=int(top_item['UnderLine']))
                
    top = Menu(win)
    make(top, menu)
    win.config(menu=top)        
        

        
def call_and_print_doc(func):
    '''This function is used as a decorator.'''
    def f(*args, **kwargs):
        ret = func(*args, **kwargs)
        if 'printDoc' in kwargs and kwargs['printDoc']:
            Application.instance.print_tip(func.__doc__)
        return ret
    f.__doc__   = func.__doc__
    return f



class WaveSynThread(object):
    class Thread(threading.Thread):
        def __init__(self, func):
            self.func   = func
            threading.Thread.__init__(self)
            
        def run(self):
            self.func()
            
    @staticmethod
    def start(func):
        app = Application.instance
        theThread  = WaveSynThread.Thread(func)
        theThread.start()
        while theThread.is_alive():
            app.root.update()
            for winId in app.windows:
                app.windows[winId].tk_object.update()


@six.add_metaclass(Singleton)
class Application(ModelNode): # Create an ABC for root node to help wavesynscript.Scripting determine whether the node is root. 
    '''This class is the root of the model tree.
In the scripting system, it is named as "wavesyn" (case sensitive).
It also manages the whole application and provide services for other components.
For other nodes on the model tree, the instance of Application can be accessed by Application.instance,
since the instance of Application is the first node created on the model tree.
The model tree of the application is illustrated as follows:
wavesyn
-console
-clipboard
-windows[id]
    -instance of PatternFitting
        -figure_book
    -instance of SingleSyn
        -figure_book
    -instance of MIMOSyn
        -figure_book
'''    
    
    _xmlrpcexport_  = [
        'create_window',
        'open_home_page'
    ]
    ''' '''
    def __init__(self):
        # The instance of this class is the root of the model tree. Thus is_root is set to True
        super(Application, self).__init__(node_name=Scripting.root_name, is_root=True)
        Scripting.name_space['locals'][Scripting.root_name] = self
        Scripting.name_space['globals'] = globals()
        Scripting.root_node = self
        self.homepage = 'https://github.com/xialulee/WaveSyn'
        
        file_path    = getsourcefile(type(self))
        dir_path     = os.path.split(file_path)[0]
        
        # load config file
        config_file_path  = os.path.join(dir_path, 'config.json')
        with open(config_file_path) as f:
            config  = json.load(f)
        console_menu = config['ConsoleMenu']
        self.editor_info   = config['EditorInfo']
        self.lock_attribute('editor_info')
        self.prompt_symbols  = config['PromptSymbols']

        tag_defs = config['TagDefs']
        # End load config file

        root = Tix.Tk()
        root.protocol("WM_DELETE_WINDOW", self._on_exit)
        main_thread_id = thread.get_ident()
        Scripting.main_thread_id = main_thread_id
        
        # To Do: WaveSyn will have a uniform command slot system.
        from wavesynlib.interfaces.xmlrpc.server import CommandSlot
        
        value_checker    = ValueChecker(root)        
        
        with self.attribute_lock:
            set_attributes(self,
                # UI elements
                root = root,
                tk_root = root,
                balloon = Tix.Balloon(root),
                taskbar_icon = TaskbarIcon(root),
                interrupter = InterrupterNode(),
                # End UI elements                
                
                main_thread_id = main_thread_id,
                exec_thread_lock = threading.RLock(),

                # To Do: WaveSyn will have a uniform command slot system.
                xmlrpc_command_slot = CommandSlot(),

                lang_center = LangCenterNode(),
            
                # Validation Functions
                value_checker = value_checker,
                check_int = value_checker.check_int,
                check_float = value_checker.check_float,
                check_positive_float = value_checker.check_positive_float,
                # End Validation Functions
                
                file_path = file_path,
                dir_path = dir_path,
                                
                stream_manager = StreamManager(),                
                
                config_file_path = config_file_path
                
#                cudaWorker      = CUDAWorker()
            )        

        # Timer utils
        self.timer = timeutils.ActionManager()              
        self.timer.after = timeutils.TimerActionNode(type_='after')
        self.timer.every = timeutils.TimerActionNode(type_='every')        
        # End Timer utils
                        
        from wavesynlib.toolwindows.basewindow import WindowDict                                  
        self.windows    = WindowDict() # Instance of ModelNode can be locked automatically.
        self.editors    = EditorDict()
        
        with self.attribute_lock:
            # The below one is the core of the new command system:
            self.command_queue = Queue.Queue()
            # The timer shown as follows checks the command queue
            # extracts command and execute.
            self.command_queue_timer = self.create_timer(interval=50, active=False)
        
        @SimpleObserver
        def command_queue_observer():
            try:
                while True:
                    command_slot = self.command_queue.get_nowait()
                    if command_slot.source == 'local':
                        node = command_slot.node_list[-1]
                        if callable(node):
                            node(*command_slot.args, **command_slot.kwargs)
                        elif isinstance(node, ModelNode):
                            getattr(node, command_slot.method_name)(*command_slot.args, **command_slot.kwargs)
                        else:
                            raise TypeError('The given object is not a ModelNode.')
            except Queue.Empty:
                return
                
        self.command_queue_timer.add_observer(command_queue_observer)
        self.command_queue_timer.active = True
        
        class EditorObserver(object): # use SimpleObserver instead
            def __init__(self, wavesyn):
                self.wavesyn    = wavesyn

            def update(self, editor):
                wavesyn = self.wavesyn                
                code    = editor.code
                if not code:
                    return
                wavesyn.stream_manager.write('WaveSyn: executing code from editor {0} listed as follows:\n'.format(id(editor)), 'TIP')
                wavesyn.stream_manager.write(code, 'HISTORY')
                wavesyn.stream_manager.write('\n')
                wavesyn.execute(code)

        self.editors.manager.add_observer(EditorObserver(self))

        with self.attribute_lock:
            self.monitor_timer = self.create_timer(interval=100, active=False)
            
        # Make wavesyn.editors.manager check wavesyn.editors every 100ms
        self.monitor_timer.add_observer(self.editors.manager) 
        
        # Check std streams every 100ms
        self.monitor_timer.add_observer(self.stream_manager)
        
        frm = Frame(root)
        frm.pack(side=TOP, fill=X)                

        self.console = ConsoleWindow(menu=console_menu, tag_defs=tag_defs)
        self.stream_manager.add_observer(self.console.stream_observer) #!
             
        self.clipboard = Clipboard()
        self.scripting = Scripting(self)
        self.no_tip = False

        self.monitor_timer.active    = True
        
        self._add_env_path()
        
    def _add_env_path(self):
        path_string = os.environ['path']        
        self_path = get_caller_dir()
        extra_path = [os.path.join(self_path, 'interfaces/windows/cmdutils')]
        extra_path.append(path_string)
        path_string = os.path.pathsep.join(extra_path)
        os.environ['path'] = path_string
        
    def create_window(self, module_name, class_name):
        '''Create a tool window.'''
        mod = __import__(auto_subs('wavesynlib.toolwindows.$module_name'), globals(), locals(), [class_name], -1)
        return self.windows.add(node=getattr(mod, class_name)())

    def launch_editor(self, editor_path=None):
        if editor_path is None:
            editor_path  = self.editor_info['Path']
        editor_id    = self.editors.add(EditorNode(editor_path=editor_path))
        self.editors[editor_id].launch()
        return editor_id
        
    def create_timer(self, interval=100, active=False):
        return TkTimer(self.tk_root, interval, active)
                     
        
    def print_and_eval(self, expr):
        with self.exec_thread_lock:
            self.stream_manager.write(expr+'\n', 'HISTORY')
            #ret = eval(expr, Scripting.name_space['globals'], Scripting.name_space['locals'])                
            ret = self.eval(expr)
            if ret is not None:
                self.stream_manager.write(str(ret)+'\n', 'RETVAL')
            return ret    
                              
    def eval(self, expr):
        with self.exec_thread_lock:
            try:
                with busy_doing:
                    ret = eval(expr, Scripting.name_space['globals'], Scripting.name_space['locals'])
            except KeyboardInterrupt:
                self.print_tip([{'type':'text', 'content':'The mission has been aborted.'}])
            Scripting.name_space['locals']['_']  = ret
            return ret
        
    def execute(self, code):
        with self.exec_thread_lock:
            ret = None
            stripped_code    = code.strip()
            if stripped_code[0] == '!':
                # To do: system(code)
                PIPE    = subprocess.PIPE
                p = subprocess.Popen(stripped_code[1:], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)  
                (stdout, stderr)    = p.communicate()
                encoding            = sys.getfilesystemencoding()
                print(stdout.decode(encoding, 'ignore'))
                print(stderr.decode(encoding, 'ignore'), file=sys.stderr)                
                return
            try:
                with busy_doing:
                    ret = self.eval(code)
            except SyntaxError:
                with busy_doing:
                    try:
                        exec code in Scripting.name_space['globals'], Scripting.name_space['locals']
                    except KeyboardInterrupt:
                        self.print_tip([{'type':'text', 'content':'The mission has been aborted.'}])
            return ret
            
                    
            
    def print_tip(self, contents):
        if self.no_tip:
            return
        stream_manager = self.stream_manager
        stream_manager.write('WaveSyn: ', 'TIP')
        if type(contents) in (str, unicode):
            stream_manager.write(contents+'\n', 'TIP')
            return
        for item in contents:
            if item['type'] == 'text':
                stream_manager.write(''.join((item['content'],'\n')), 'TIP')
            elif item['type'] == 'link':
                command = item['command']
                tagName = 'link' + str(id(command))
                stream_manager.write(item['content'], tagName)
                text    = self.console.text
                r, c = text.index(END).split('.')
                text.tag_config(tagName, underline=1, foreground='blue')
                text.tag_bind(tagName, '<Button-1>', command) # href implementation shold be added.
                text.tag_bind(tagName, '<Enter>', lambda dumb: text.config(cursor='hand2'))
                text.tag_bind(tagName, '<Leave>', lambda dumb: text.config(cursor=self.console.default_cursor))
                stream_manager.write('\n')
            elif item['type'] == 'pil_image':
                # stream_manager.write('The QR code of the text stored by clipboard is shown above.', 'TIP')
                text    = self.console.text                
                text.insert(END, '\n')
                pil_frame    = PILImageFrame(text, pil_image=item['content'])
                text.window_create(END, window=pil_frame)
                text.insert(END, '\n')
                stream_manager.write('\n')
                
                                            
                
    def print_error(self, text):
        self.stream_manager.write(text+'\n', 'STDERR')
        
            
    def on_window_quit(self, win):
        self.print_tip(eval_format('{win.node_path} is closed, and its ID becomes defunct for scripting system hereafter'))
        self.windows.pop(id(win))
        
        
    def open_home_page(self):
        '''Open the home page of wavesyn.'''
        webbrowser.open(self.homepage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.root.mainloop()
        

    def _on_exit(self):    
        self.interrupter.close()
        
        # Here we cannot iterate the 'windows' directly,
        # because the close method will change the size of the dict 'windows',
        # and this will raise a runtime error.
        keys = [key for key in self.windows]
        for key in keys:
            self.windows[key].close()
        self.tk_root.quit()
    
        
    @classmethod
    def do_events(cls):
        cls.instance.root.update()
        
    def start_xmlrpc_server(self, addr='localhost', port=8000):
        from wavesynlib.interfaces.xmlrpc.server    import start_xmlrpc_server
        start_xmlrpc_server(addr, port)        
        def check_command():
            command = self.xmlrpc_command_slot.command
            convert_args_to_str  = Scripting.convert_args_to_str # used by eval_format
            try:
                if command is not None:
                    node_path, method_name, args, kwargs  = command
                    ret, err    = None, None
                    try:
                        ret = self.print_and_eval(eval_format('{node_path}.{method_name}({convert_args_to_str(*args, **kwargs)})')) # paramToStr used here
                    except Exception as error:
                        err = error
                    ret = 0 if ret is None else ret
                    self.xmlrpc_command_slot.return_value    = (ret, err)
            finally:
                # Make sure that at any circumstance the check_command will be called repeatedly.
                self.root.after(100, self.xmlrpc_check_command)
        self.xmlrpc_check_command = check_command
        self.root.after(100, check_command) # To Do: Use TkTimer instead of after
        
        
def get_gui_image_path(filename):
    return os.path.join(Application.instance.dir_path, 'images', filename)        
                

        
# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm              
class ConsoleText(ScrolledText):
    class StreamObserver(object):
        def __init__(self, console_text):
            self.__console_text  = console_text
        def update(self, stream_type, content):
            self.__console_text.write(stream_type, content)
    
    def __init__(self, *args, **kwargs):
        super(ConsoleText, self).__init__(*args, **kwargs)
        # The shared queue of the PRODUCER-CONSUMER model.
        self.__queue    = Queue.Queue()
        self.text['wrap']   = 'word'
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')
        
        self.text.bind('<KeyPress>', self.on_key_press)

        
        # Experimenting with idlelib.AutoComplete
        #############################################################
        self.indent_width    = 4
        self.tab_width       = 4
        self.context_use_ps1    = '>>> '
        self.__auto_complete = AutoComplete(self)  
        #############################################################
                
        # Syntax highlight is implemented by idlelib
        #############################################################                
        self.percolator = Percolator(self.text)
        self.color_delegator = ColorDelegator()
        self.percolator.insertfilter(self.color_delegator)   
        #############################################################                        
        self.prompt_symbol = '>>> '    
        
        
    def update_content(self, tag, content):
        r, c    = self.get_cursor_pos(END)
        start   = 'end-5c'
        stop    = 'end-1c'
        if self.text.get(start, stop) == '>>> ' or self.text.get(start, stop) == '... ':
            self.text.delete(start, stop)

        # Record the position of the END before inserting anything.
        start    = self.text.index(END)

        self.text.insert(END, content, tag)

        # Remove unnecessary highlighting
        for tag in self.color_delegator.tagdefs:
            self.text.tag_remove(tag, start, "end")            
        self.text.insert(END, self.prompt_symbol)                
        # Remove unnecessary highlighting
        self.text.tag_remove("TODO", "1.0", END)
        self.text.tag_add("SYNC", "1.0", END)                                
        self.text.see(END)                        

    def on_key_press(self, evt, code_list=[]):       
        # Experimenting with idlelib's AutoComplete
        ##############################################################
        keysym = evt.keysym        
        if self.__auto_complete.autocompletewindow and \
                self.__auto_complete.autocompletewindow.is_active():
            if self.__auto_complete.autocompletewindow.keypress_event(evt) == 'break':
                return 'break'
            else:
                if keysym == 'Tab':
                    return 'break'
            
        if evt.keysym == 'Tab':
            return self.__auto_complete.autocomplete_event(evt)
        ##############################################################
        if evt.keycode not in range(16, 19) and evt.keycode not in range(33, 41):
            r, c    = self.get_cursor_pos()
            prompt  = self.text.get(auto_subs('$r.0'), auto_subs('$r.4'))
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if evt.keycode==8 and c <= 4:
                return 'break'
            if c < 4:
                return 'break'
            rend, cend  = self.get_cursor_pos('end-1c')
            if r < rend:
                return 'break'                
            if evt.keycode == 13:
                app = Application.instance
                code    = self.text.get(auto_subs('$r.4'), auto_subs('$r.end'))
                try:
                    stripped_code     = code.strip()
                    if stripped_code and stripped_code[0] == '!':
                        # Execute a system command
                        app.execute(code)
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n')
                        return 'break'
                    if stripped_code == '':
                        code    = '\n'.join(code_list)
                        del code_list[:]
                    stripped_code    = code.strip()
                    if stripped_code == '':
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n') 
                    elif stripped_code[-1] in (':', '\\') or code_list:
                        code_list.append(code)
                        self.prompt_symbol   = '... '
                        self.update_content(tag='', content='\n')
                    else:
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n')
                        try:
                            ret = app.execute(code)
                        except:
                            traceback.print_exc()
                        if ret is not None:
                            self.update_content(tag='RETVAL', content=repr(ret)+'\n')
    
                finally:
                    self.text.mark_set(INSERT, END)
                    self.text.see(END)
                    return 'break'            
                
    def get_cursor_pos(self, mark=INSERT): 
        return (int(i) for i in self.text.index(mark).split('.'))               
        

class StatusBar(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        timer = TkTimer(widget=self, interval=200, active=False)
        self.__busy_lamp = six.moves.tkinter.Label(self, bg='forestgreen', width=1)
        self.__busy_lamp.pack(side=RIGHT)
        self.__lock = lock = thread.allocate_lock()
        self.__busy = False
        
        @SimpleObserver
        def on_timer():
            with lock:
                bg = 'red' if self.__busy else 'forestgreen'
            self.__busy_lamp['bg'] = bg
            
        timer.add_observer(on_timer)
        timer.active = True
        # To Do: add several customizable lamps for users.
        
    def set_busy(self, busy=True):
        with self.__lock:
            self.__busy = busy
#        self.update()
        
        
class ConsoleWindow(ModelNode):    
    class StreamObserver(object):
        def __init__(self, console):
            self.__console  = console
            
        def update(self, stream_type, content):
            self.__console.console_text.update_content(tag=stream_type, content=content)

    def __init__(self, *args, **kwargs):
        super(ConsoleWindow, self).__init__(*args, **kwargs)
        app = Application.instance
        root = app.root
        root.title('WaveSyn-Console')

        dir_indicator = CWDIndicator()
        dir_indicator.pack(fill=X)
        
        self.__stdstream_text = stdstream_text = ConsoleText(root)
        stdstream_text.pack(expand=YES, fill=BOTH)
        
        self.__status_bar = status_bar = StatusBar(root)
        status_bar.pack(fill=X)
        
        @SimpleObserver
        def busy_status_observer(busy):
            status_bar.set_busy(busy)
            
        busy_doing.add_observer(busy_status_observer)

        tag_defs = kwargs['tag_defs']
        for key in tag_defs:
            self.text.tag_configure(key, **tag_defs[key])        

        nowtime = datetime.now().hour
        if nowtime >= 19:
            time    = 'evening'
        elif nowtime >= 12:
            time    = 'afternoon'
        else:
            time    = 'morning'
        app.stream_manager.write(templates.greeting.format(time), 'TIP')
        menu    = kwargs['menu']
        make_menu(root, menu, json=True)
        self.__default_cursor = self.__stdstream_text.text['cursor']
        self.stream_observer = self.StreamObserver(self)
        
        
    @property
    def console_text(self):
        return self.__stdstream_text        
        
    @property
    def prompt_symbol(self):
        return self.__stdstream_text.prompt_symbol
        
    @prompt_symbol.setter
    def prompt_symbol(self, val):
        self.__stdstream_text.prompt_symbol    = val
        
    @property
    def default_cursor(self):
        return self.__default_cursor
                                                               
    @property
    def text(self):
        return self.__stdstream_text.text
                                                                    
    @Scripting.printable    
    def save(self, filename): # for scripting system
        with open(filename, 'w') as f:
            f.write(self.__stdstream_text.get_text())
            
    def on_save_as(self):        
        filename    = asksaveasfilename(filetypes=[('All types of files', '*.*')])
        if not filename:
            return
        with code_printer:
            self.save(filename)
    
    @Scripting.printable    
    def clear(self):
        self.__stdstream_text.clear()
        print('', sep='', end='')
        
    def on_clear(self):
        with code_printer:
            self.clear()

    def set_window_attributes(self, *args, **kwargs):
        return Application.instance.root.wm_attributes(*args, **kwargs)        
        
        
        
     
    

def mainloop():
    Application().mainloop()
        
        