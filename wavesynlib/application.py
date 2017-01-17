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

REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr

from six.moves.tkinter import *
from six.moves.tkinter_ttk import *

import six.moves.tkinter_tix as Tix
from six.moves.tkinter import Frame


import matplotlib
matplotlib.use('TkAgg')

from numpy import *


from inspect import getsourcefile
import webbrowser
import subprocess
import json


from wavesynlib.guicomponents.tk import TaskbarIcon, ValueChecker, PILImageFrame
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.editor.externaleditor import EditorDict, EditorNode
from wavesynlib.interfaces.modelnode import Interfaces
from wavesynlib.stdstream import StreamManager
from wavesynlib.threadtools import ThreadManager
from wavesynlib.languagecenter.utils import eval_format, set_attributes, get_caller_dir
from wavesynlib.languagecenter.designpatterns import Singleton      
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, model_tree_monitor, code_printer
from wavesynlib.languagecenter.modelnode import LangCenterNode
from wavesynlib.languagecenter import timeutils
from wavesynlib.toolwindows.interrupter.modelnode import InterrupterNode
from wavesynlib.toolwindows import simpledialogs
from wavesynlib.toolwindows.basewindow import WindowDict
from wavesynlib.status import busy_doing
from wavesynlib.console import ConsoleWindow
from wavesynlib.languagecenter import datatypes


def call_and_print_doc(func):
    '''This function is used as a decorator.'''
    def f(*args, **kwargs):
        ret = func(*args, **kwargs)
        if 'printDoc' in kwargs and kwargs['printDoc']:
            Application.instance.print_tip(func.__doc__)
        return ret
    f.__doc__   = func.__doc__
    return f



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
-interfaces
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
        super(Application, self).__init__(
            node_name=Scripting.root_name, 
            is_root=True)

        # init tk root window            
        root = Tix.Tk()
        root.protocol("WM_DELETE_WINDOW", self._on_exit)
        with self.attribute_lock:
            self.tk_root = root
        # end init tk root window            
            
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

        
        # To Do: WaveSyn will have a uniform command slot system.
        from wavesynlib.interfaces.xmlrpc.server import CommandSlot
                
        value_checker    = ValueChecker(root)
                
        with self.attribute_lock:
            set_attributes(self,
                # UI elements
                #tk_root = root,
                balloon = Tix.Balloon(root),
                taskbar_icon = TaskbarIcon(root),
                interrupter = InterrupterNode(),
                dialogs = simpledialogs.Dialogs(self),
                windows = WindowDict(),
                # End UI elements
                                                
                # Interfaces node
                interfaces = Interfaces(),
                # End Interfaces node
                
                file_utils = ModelNode(
                    is_lazy=True,
                    module_name='wavesynlib.fileutils', 
                    class_name='FileUtils'),
                
                # Thread related
                thread_manager = ThreadManager(),
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
            )  
            
        # Timer utils
        self.timer = timeutils.ActionManager()              
        self.timer.after = timeutils.TimerActionNode(type_='after')
        self.timer.every = timeutils.TimerActionNode(type_='every')        
        # End Timer utils
                        
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
        # To Do: Use the new create_link_tag method of ScrolledText
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
        
                
    def get_gui_image_path(self, filename):
        return os.path.join(self.dir_path, 'images', filename)        
                
        
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
        
        
