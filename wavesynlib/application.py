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

import six
from six.moves import _thread as thread
import threading
from six.moves import queue

import os
import os.path
import sys
from importlib import import_module
REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr

import tarfile

from six.moves.tkinter import *
from six.moves.tkinter_ttk import *

import six.moves.tkinter_tix as Tix
from six.moves.tkinter import Frame
from six.moves.tkinter_tkfiledialog import asksaveasfilename, askopenfilename, askdirectory

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
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.editor.externaleditor import EditorDict, EditorNode
from wavesynlib.interfaces.modelnode import Interfaces
from wavesynlib.stdstream import StreamManager
from wavesynlib.languagecenter.utils import auto_subs, eval_format, set_attributes, get_caller_dir
from wavesynlib.languagecenter.designpatterns import Singleton, SimpleObserver      
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, model_tree_monitor, code_printer, Constant
from wavesynlib.languagecenter.modelnode import LangCenterNode
from wavesynlib.languagecenter import templates
from wavesynlib.languagecenter import timeutils
from wavesynlib.toolwindows.interrupter.modelnode import InterrupterNode
from wavesynlib.toolwindows import simpledialogs
from wavesynlib.status import busy_doing


def make_menu(win, menu, json=False):
    def func_gen(code, print_code=True):
        if print_code:
            f   = Application.instance.print_and_eval
        else:
            f   = Application.instance.eval
            
        if isinstance(code, list):
            def func():
                for cmd in code:
                    retval = f(cmd)
                return retval
            return func
        else:
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
            app.tk_root.update()
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
-os
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
        
        # Construct Constants                
        class Constants(object): 
            name_value_pairs = (                
                ('KEYSYM_MODIFIERS', {'Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R'}),
                ('KEYSYM_CURSORKEYS', {
                    'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 
                    'KP_Left', 'KP_Right', 'KP_Up', 'KP_Down', 
                    'Left', 'Right', 'Up', 'Down', 
                    'Home', 'End', 'Next', 'Prior'                
                })
            )
            
            for name, value in name_value_pairs:
                locals()[name] = Constant(name, value)            
            
            for name in simpledialogs.constant_names:
                locals()[name] = Constant(name, None)
        # End Construct Constants
        
        value_checker    = ValueChecker(root)
                
        # File Utils Node                     
        class TarFileManipulator(ModelNode):
            def __init__(self, *args, **kwargs):
                filename = kwargs.pop('filename')
                ModelNode.__init__(self, *args, **kwargs)
                with self.attribute_lock:
                    self.filename = filename
                    
            @property
            def node_path(self):
                return eval_format('{self.parent_node.node_path}["{self.filename}"]')
                
            @Scripting.printable
            def extract_all(self, directory):
                if directory is self.root_node.constants.ASK_DIALOG:
                    directory = askdirectory(initialdir=os.getcwd())
                if not directory:
                    return
                    
                tar = tarfile.open(self.filename)
                tar.extractall(directory)
        
        class TarFileManager(ModelNode):
            def __init__(self, *args, **kwargs):
                ModelNode.__init__(self, *args, **kwargs)
                
            def __getitem__(self, filename):
                if filename is self.root_node.constants.ASK_DIALOG:
                    filename = askopenfilename(filetypes=[('TAR Files', ('*.tar', '*.tar.gz', '*.tgz')), ('All Files', '*.*')])
                if not filename:
                    return
                    
                manipulator = TarFileManipulator(filename=filename)
                object.__setattr__(manipulator, 'parent_node', self)
                manipulator.lock_attribute('parent_node')
                return manipulator
                
        
        class FileUtils(ModelNode):
            def __init__(self, *args, **kwargs):
                ModelNode.__init__(self, *args, **kwargs)                
                self.pdf_files = ModelNode(is_lazy=True, module_name='wavesynlib.interfaces.pdf.modelnode', class_name='PDFFileManager')
                self.touchstone_files = ModelNode(is_lazy=True, module_name='wavesynlib.interfaces.devcomm.touchstone.modelnode', class_name='TouchstoneFileManager')
                self.tar_files = ModelNode(is_lazy=True, class_object=TarFileManager)
                
        self.file_utils = FileUtils()
        # End File Utils Node
                
        
        with self.attribute_lock:
            set_attributes(self,
                # UI elements
                tk_root = root,
                balloon = Tix.Balloon(root),
                taskbar_icon = TaskbarIcon(root),
                interrupter = InterrupterNode(),
                dialogs = simpledialogs.Dialogs(self),
                # End UI elements
                
                # Constants
                constants = Constants,
                # End Constants
                                
                # Interfaces node
                interfaces = Interfaces(),
                # End Interfaces node
                
                # Thread related
                main_thread_id = main_thread_id,
                exec_thread_lock = threading.RLock(),
                # End
                
                model_tree_monitor = model_tree_monitor,

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
            self.command_queue = queue.Queue()
            # The timer shown as follows checks the command queue
            # extracts command and execute.
            self.command_queue_timer = self.create_timer(interval=50, active=False)
        
        @self.command_queue_timer.add_observer
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
            except queue.Empty:
                return
                
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
             
        self.scripting = Scripting(self)
        self.no_tip = False

        self.monitor_timer.active    = True
        
        self._add_env_path()
        
    def _add_env_path(self):
        path_string = os.environ['PATH']        
        self_path = get_caller_dir()
        extra_path = [os.path.join(self_path, 'interfaces/os/cmdutils')]
        extra_path.append(path_string)
        path_string = os.path.pathsep.join(extra_path)
        os.environ['PATH'] = path_string
        
    def create_window(self, module_name, class_name):
        '''Create a tool window.'''
        # To Do: Move this method to window node
        mod = import_module(auto_subs('wavesynlib.toolwindows.$module_name'))
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
                PIPE = subprocess.PIPE
                p = subprocess.Popen(stripped_code[1:], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)  
                (stdout, stderr) = p.communicate()
                encoding = sys.getfilesystemencoding()
                print(stdout.decode(encoding, 'ignore'))
                print(stderr.decode(encoding, 'ignore'), file=sys.stderr)                
                return
            try:
                try:
                    with busy_doing:
                        ret = self.eval(code)
                except SyntaxError:
                    with busy_doing:
                        try:
                            six.exec_(code, Scripting.name_space['globals'], Scripting.name_space['locals'])
                        except KeyboardInterrupt:
                            self.print_tip([{'type':'text', 'content':'The mission has been aborted.'}])
            except SystemExit:
                self._on_exit()
            return ret
            
                    
            
    def print_tip(self, contents):
        def config_link_tag(widget, tag_name, command, original_cursor):
            widget.tag_config(tag_name, underline=1, foreground='blue')
            widget.tag_bind(tag_name, '<Button-1>', command)
            widget.tag_bind(tag_name, '<Enter>', lambda dumb: text.config(cursor='hand2'))
            widget.tag_bind(tag_name, '<Leave>', lambda dumb: text.config(cursor=original_cursor))
        
        if self.no_tip:
            return
        stream_manager = self.stream_manager
        stream_manager.write('WaveSyn: ', 'TIP')
        if type(contents) in (str, unicode):
            stream_manager.write(contents+'\n', 'TIP')
            return

        return_list = []            
            
        for item in contents:
            if item['type'] == 'text':
                stream_manager.write(''.join((item['content'],'\n')), 'TIP')
                return_list.append(None)
            elif item['type'] == 'link':
                command = item['command']
                tag_name = 'link' + str(id(command))
                stream_manager.write(item['content'], tag_name)
                text = self.console.text
                #r, c = text.index(END).split('.')
#                text.tag_config(tagName, underline=1, foreground='blue')
#                text.tag_bind(tagName, '<Button-1>', command) # href implementation shold be added.
#                text.tag_bind(tagName, '<Enter>', lambda dumb: text.config(cursor='hand2'))
#                text.tag_bind(tagName, '<Leave>', lambda dumb: text.config(cursor=self.console.default_cursor))
                config_link_tag(text, tag_name, command, self.console.default_cursor)                                
                stream_manager.write('\n')
                return_list.append(None)
            elif item['type'] == 'pil_image':
                # stream_manager.write('The QR code of the text stored by clipboard is shown above.', 'TIP')
                text    = self.console.text                
                text.insert(END, '\n')
                pil_frame    = PILImageFrame(text, pil_image=item['content'])
                text.window_create(END, window=pil_frame)
                text.insert(END, '\n')
                stream_manager.write('\n')
                return_list.append(id(pil_frame))
            elif item['type'] == 'file_list':
                file_list = item['content']
                def new_open_func(path):
                    def open_func(*args):
                        import webbrowser
                        webbrowser.open(path)
                    return open_func
                    
                def new_browse_func(path):
                    def browse_func(*args):
                        with code_printer:
                            self.interfaces.os.win_open(path)
                    return browse_func
                    
                for file_path in file_list:
                    text = self.console.text                    
                    
                    open_func = new_open_func(file_path)
                    open_tag_name = 'link' + str(id(open_func))
                    stream_manager.write('open', open_tag_name)
                    config_link_tag(text, open_tag_name, open_func, self.console.default_cursor)
                    stream_manager.write(' ')

                    browse_func = new_browse_func(file_path)                    
                    browse_tag_name = 'link' + str(id(browse_func))
                    stream_manager.write('browse', browse_tag_name)
                    config_link_tag(text, browse_tag_name, browse_func, self.console.default_cursor)                    
                    stream_manager.write(' ')
                    
                    stream_manager.write(eval_format('{file_path}\n'))
                return_list.append(None)
        return return_list
                                            
                
    def print_error(self, text):
        self.stream_manager.write(text+'\n', 'STDERR')
        
            
    def on_window_quit(self, win):
        self.print_tip(eval_format('{win.node_path} is closed, and its ID becomes defunct for scripting system hereafter'))
        self.windows.pop(id(win))
        
        
    def open_home_page(self):
        '''Open the home page of wavesyn.'''
        webbrowser.open(self.homepage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.tk_root.mainloop()
        

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
        cls.instance.tk_root.update()
        
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
                self.tk_root.after(100, self.xmlrpc_check_command)
        self.xmlrpc_check_command = check_command
        self.tk_root.after(100, check_command) # To Do: Use TkTimer instead of after
        
    @Scripting.printable
    def system(self, command):
        subprocess.call(command, shell=True)
        
        
    @Scripting.printable
    def set_matplotlib_style(self, style_name=''):
        import matplotlib.pyplot as plt
        
        style_name = self.root_node.dialogs.support_ask_list_item(
            style_name,
            the_list=plt.style.available,
            message='Select a style for newly-created figures.')

        plt.style.use(style_name)
        
                
def get_gui_image_path(filename):
    return os.path.join(Application.instance.dir_path, 'images', filename)        
                

        
# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm              
class ConsoleText(ScrolledText, ModelNode):
    class StreamObserver(object):
        def __init__(self, console_text):
            self.__console_text  = console_text
        def update(self, stream_type, content):
            self.__console_text.write(stream_type, content)
    
    def __init__(self, *args, **kwargs):
        #super(ConsoleText, self).__init__(*args, **kwargs)
        ScrolledText.__init__(self, *args, **kwargs)
        ModelNode.__init__(self, *args, **kwargs)
        # The shared queue of the PRODUCER-CONSUMER model.
        self.__queue    = queue.Queue()
        self.text['wrap']   = 'word'
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')
        
        self.text.bind('<KeyPress>', self.on_key_press)

        
        # Auto complete is implemented by idlelib
        #############################################################
        self.indentwidth    = 4
        self.tabwidth       = 4
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
        # Using keycode is not a good practice here, because for the same key,
        # the keycode may change on different machines and operating systems.
        #if evt.keysym not in ('Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R',  'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 'KP_Left', 'KP_Right', 'KP_Up', 'KP_Down', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Next', 'Prior'):
        if (evt.keysym not in self.root_node.constants.KEYSYM_MODIFIERS.value) and \
           (evt.keysym not in self.root_node.constants.KEYSYM_CURSORKEYS.value):
            r, c    = self.get_cursor_pos()
            prompt  = self.text.get(auto_subs('$r.0'), auto_subs('$r.4'))
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if evt.keysym=='BackSpace' and c <= 4:
                return 'break'
            if c < 4:
                return 'break'
            rend, cend  = self.get_cursor_pos('end-1c')
            if r < rend:
                return 'break'                
            if evt.keysym == 'Return': # Return
                app = Application.instance
                code = self.text.get(auto_subs('$r.4'), auto_subs('$r.end'))
                try:
                    stripped_code     = code.strip()
                    if stripped_code and stripped_code[0] == '!':
                        # Execute a system command
                        app.execute(code)
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n')
                        return 'break'
                    if stripped_code == '':
                        code = '\n'.join(code_list)
                        del code_list[:]
                    stripped_code = code.strip()
                    if stripped_code == '':
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n') 
                    elif code_list or stripped_code[-1] in (':', '\\') or stripped_code[0] in ('@',): # Threre is a bug here for decorators! To do: Solve it.
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
        
        balloon = Scripting.root_node.balloon
                
        busy_lamp = six.moves.tkinter.Label(self, bg='forestgreen', width=1)
        busy_lamp.pack(side=RIGHT, fill='y')
        balloon.bind_widget(busy_lamp, balloonmsg='''Main-thread status.
Green: main-thread is available;
Red:   main-thread is busy.''')
        self.__busy_lamp = busy_lamp
        
        self.__membar = IntVar(0)
        self.__cpubar = IntVar(0)
        self._make_cpu_mem_status()

        # Transparent Scale {
        def on_scale(val):
            Scripting.root_node.console.set_transparency(val)
        trans_scale = Scale(self, from_=0.2, to=1.0, orient='horizontal', value=1, command=on_scale)
        trans_scale.pack(side='right')
        balloon.bind_widget(trans_scale, balloonmsg='Set the transparency of the console.')
        # } End Transparent Scale

        # Topmost Button {
        import six.moves.tkinter as tkinter
        topmost_button = tkinter.Button(self, text='TOP', relief='groove') 
        topmost_button.pack(side='right')
        
        def on_click():
            tk_root = Scripting.root_node.tk_root
            b = bool(tk_root.wm_attributes('-topmost'))
            fg = 'black' if b else 'lime green'
            topmost_button['fg'] = fg
            tk_root.wm_attributes('-topmost', not b)
            
        topmost_button['command'] = on_click
        balloon.bind_widget(topmost_button, balloonmsg='Set the console as a topmost window.')
        # } End Topmost Button 
        
        #{ Window Combo
        window_combo = Combobox(self, value=[], takefocus=1, stat='readonly')
        def on_selected(event):
            text = event.widget.get()
            wid = int(text.split(':')[1].strip())
            Scripting.root_node.windows[wid].tk_object.deiconify()
        window_combo.bind('<<ComboboxSelected>>', on_selected)
        window_combo.pack(side='right', fill='y') # deiconify a window
        
        @Scripting.root_node.windows.add_observer
        def on_windows_change(node, command):
            values = window_combo['values']
            if values == '':
                values = []
            if isinstance(values, tuple):
                values = list(values)
            node_id = id(node)
            if command == 'new':
                type_name = node.__class__.__name__
                values.append(eval_format('{type_name}: {node_id}'))
            elif command == 'del':
                for index, value in enumerate(values):
                    wid = int(value.split(':')[1].strip())
                    if node_id == wid:
                        del values[index]
            window_combo['values'] = values
            if len(values) > 0:
                window_combo.current(len(values)-1)
            else:
                window_combo.set('')
        #} End Window Combo
                
        self.__lock = thread.allocate_lock()
        self.__busy = False
             
        get_memory_usage = Scripting.root_node.interfaces.os.get_memory_usage
        get_cpu_usage    = Scripting.root_node.interfaces.os.get_cpu_usage
                    
        @SimpleObserver
        def check_cpu_mem():
            self.__membar.set(get_memory_usage())
            self.__cpubar.set(get_cpu_usage())
            
        timer.divider(divide_by=10).add_observer(check_cpu_mem)
        timer.active = True
        # To Do: add several customizable lamps for users.
        
    def _set_busy_light(self):
        bg = 'red' if self.__busy else 'forestgreen'
        self.__busy_lamp['bg'] = bg
        self.update()
        
    def set_busy(self, busy=True):
        with self.__lock:
            self.__busy = busy
        if thread.get_ident() == Scripting.main_thread_id:
            # Only main thread can set busy light
            self._set_busy_light()
            
    def _make_cpu_mem_status(self):
        balloon = Scripting.root_node.balloon
        
        mem_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__membar)
        mem_progbar.pack(side='right', fill='y')
        balloon.bind_widget(mem_progbar, balloonmsg='Total memory usage.')
        
        cpu_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__cpubar)
        cpu_progbar.pack(side='right', fill='y')
        balloon.bind_widget(cpu_progbar, balloonmsg='Total CPU usage.')        
        
        
class ConsoleWindow(ModelNode):    
    class StreamObserver(object):
        def __init__(self, console):
            self.__console  = console
            
        def update(self, stream_type, content):
            self.__console.console_text.update_content(tag=stream_type, content=content)

    def __init__(self, *args, **kwargs):
        super(ConsoleWindow, self).__init__(*args, **kwargs)
        app = Application.instance
        root = app.tk_root
        root.title('WaveSyn-Console')

        dir_indicator = CWDIndicator()
        dir_indicator.pack(fill='x')

        self.__status_bar = status_bar = StatusBar(root)
        status_bar.pack(side='bottom', fill='x')
        
        self.console_text = ConsoleText(root)        
        self.__stdstream_text = stdstream_text = self.console_text
        stdstream_text.pack(expand='yes', fill='both')
                    
        @busy_doing.add_observer
        def busy_status_observer(busy):
            status_bar.set_busy(busy)        

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
        
        
#    @property
#    def console_text(self):
#        return self.__stdstream_text        
        
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
        return self.root_node.tk_root.wm_attributes(*args, **kwargs)        
        
    def set_topmost(self, b):
        tk_root = self.root_node.tk_root
        if b == 'flip':
            b = False if tk_root.wm_attributes('-topmost') else True
        tk_root.wm_attributes('-topmost', b)
        
    def set_transparency(self, transparency):
        self.root_node.tk_root.wm_attributes('-alpha', transparency)
        
     
    

def mainloop():
    wavesyn = Application()
    # We cannot launch the process of interrupter in Application __init__ on Windows,
    # or a runtime error will be raised:
    # "Attempt to start a new process before the current process
    # has finished its bootstrapping phase..."
    #
    # launch.py and launchwavesyn.py will call this mainloop function in __main__.
    wavesyn.interrupter.launch()
    wavesyn.mainloop()
        
        
