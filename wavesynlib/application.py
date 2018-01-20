# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: Feng-cong Li. xialulee@sina.com
"""
import threading
import queue

import os
import os.path
import sys
import locale
import tkinter
import pickle
from pathlib import Path

from collections import OrderedDict

REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr

import matplotlib
matplotlib.use('TkAgg')

from numpy import *


from inspect import getsourcefile
import webbrowser
import subprocess
import json


from wavesynlib.guicomponents.tk import PILImageFrame, ArgEntry, ScrolledText
from wavesynlib.interfaces.editor.externaleditor import EditorDict, EditorNode
from wavesynlib.interfaces import Interfaces
from wavesynlib.stdstream import StreamManager
from wavesynlib.threadtools import ThreadManager
from wavesynlib.processtools import ProcessDict
from wavesynlib.languagecenter.utils import set_attributes, get_caller_dir
from wavesynlib.languagecenter.designpatterns import Singleton      
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, model_tree_monitor, code_printer
from wavesynlib.languagecenter.modelnode import LangCenterNode
from wavesynlib.languagecenter import timeutils, datatypes
from wavesynlib.toolwindows.imagedisplay.modelnode import DisplayLauncher
from wavesynlib.status import busy_doing



def call_and_print_doc(func):
    '''This function is used as a decorator.'''
    def f(*args, **kwargs):
        ret = func(*args, **kwargs)
        if 'printDoc' in kwargs and kwargs['printDoc']:
            Application.instance.print_tip(func.__doc__)
        return ret
    f.__doc__   = func.__doc__
    return f



class Application(ModelNode, metaclass=Singleton): # Create an ABC for root node to help wavesynscript.Scripting determine whether the node is root. 
    '''This class is the root of the model tree.
In the scripting system, it is named as "wavesyn" (case sensitive).
It also manages the whole application and provide services for other components.
For other nodes on the model tree, the instance of Application can be accessed by Application.instance,
since the instance of Application is the first node created on the model tree.
'''    
    
    _xmlrpcexport_  = [
        'create_window',
        'open_home_page'
    ]
    ''' '''
    def __init__(self):
        # The instance of this class is the root of the model tree. Thus is_root is set to True
        super().__init__(node_name=Scripting.root_name, is_root=True)
            
        Scripting.namespace['locals'][Scripting.root_name] = self
        Scripting.namespace['globals'] = globals()
        Scripting.root_node = self
        
        file_path    = getsourcefile(type(self))
        dir_path     = os.path.split(file_path)[0]
        with self.attribute_lock:
            self.homepage = 'https://github.com/xialulee/WaveSyn'
            self.file_path = file_path
            self.dir_path = dir_path
        
        
        # load config file
        config_file_path  = os.path.join(dir_path, 'config.json')
        with open(config_file_path) as f:
            config  = json.load(f)
        console_menu = config['ConsoleMenu']
        with self.attribute_lock:
            self.editor_info   = config['EditorInfo']
            self.prompt_symbols  = config['PromptSymbols']

        tag_defs = config['TagDefs']
        # End load config file
        
        
        self.interfaces = Interfaces()
        self.stream_manager = StreamManager()
        
        from wavesynlib.gui.tk import TkNode
        # TkNode is a ModelNode which maintains the Tk root window
        # and related utilities like value checker, balloon, and related
        # WaveSyn components. 
        self.gui = TkNode(console_menu=console_menu, tag_defs=tag_defs)
        self.gui.on_exit = self._on_exit         

        
        # To Do: WaveSyn will have a uniform command slot system.
        from wavesynlib.interfaces.xmlrpc.server import CommandSlot                
                
        with self.attribute_lock:
            set_attributes(self,
                code_printer = code_printer,
                           
                processes = ProcessDict(),
                                                                
                file_utils = ModelNode(
                    is_lazy=True,
                    module_name='wavesynlib.fileutils', 
                    class_name='FileUtils'),
                
                # Thread related
                thread_manager = ThreadManager(),
                exec_thread_lock = threading.RLock(), # should be replaced with the "ensure main thread" mechanism. 
                # End
                
                # To Do: build a widget on console
                # for displaying the nodes of the model tree.
                model_tree_monitor = model_tree_monitor,

                # To Do: WaveSyn will have a uniform command slot system.
                xmlrpc_command_slot = CommandSlot(),

                lang_center = LangCenterNode(),
                                            
                config_file_path = config_file_path,
                
                image_display = DisplayLauncher()
            )  
            
        # Timer utils
        self.timer_manager = timeutils.ActionManager()              
        self.timer_manager.after = timeutils.TimerActionNode(type_='after')
        self.timer_manager.every = timeutils.TimerActionNode(type_='every')        
        # End Timer utils
                        
        self.editors    = EditorDict()
        
        
        ## Begin: The command system of WaveSyn
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
                    # No blocking, or the main thread will not 
                    # responds to other events. 
                    
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
        ## End.
        
        
        @self.editors.manager.add_observer
        def editor_observer(editor):
            code = editor.code
            if not code:
                return
            self.stream_manager.write(f'WaveSyn: executing code from editor {id(editor)} listed as follows:\n', 'TIP')
            self.stream_manager.write(code, 'HISTORY')
            self.stream_manager.write('\n')
            self.execute(code)            
        

        with self.attribute_lock:
            self.monitor_timer = self.create_timer(interval=100, active=False)
            
        # Make wavesyn.editors.manager check wavesyn.editors every 100ms
        self.monitor_timer.add_observer(self.editors.manager) 
        
        # Check std streams every 100ms
        self.monitor_timer.add_observer(self.stream_manager)
                     
        self.scripting = Scripting(self)
        self.no_tip = False

        self.monitor_timer.active = True
        
        self._add_env_path()
        

    def _add_env_path(self):
        path_string = os.environ['PATH']        
        self_path = get_caller_dir()
        extra_path = [str(self_path / 'interfaces/os/cmdutils')]
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
        '''Create a timer which is based on the Observer protocol.

interval: the interval of the timer.
    Default: 100.
    Unit: millisecond.
active: True for activating the timer, and False for deactivating.
    Default: False.'''
        return self.gui.create_timer(interval, active)
        # The timer system of WaveSyn is build on 
        # tkinter. 
        
        
    def create_arg_panel_for_func(self, func):
        '''Read the argument information of the given function, 
and generate a dialog which helps user to input parameters.'''
        dialog = tkinter.Toplevel()
        frmright = tkinter.Frame(dialog)
        frmright.pack(side='right', expand='yes', fill='both')
        frmleft = tkinter.Frame(dialog)
        frmleft.pack(side='left', fill='y')
        
        argmap = OrderedDict()
        annotations = func.__annotations__
        defaults = func.__defaults__
        defcount = len(defaults)
        argcount = func.__code__.co_argcount
        defstart = argcount - defcount
        for idx, name in enumerate(func.__code__.co_varnames[:argcount]):
            if name == 'self':
                continue
            else:
                argmap[name] = ae = ArgEntry(frmleft)
                ae.pack()
                ae.arg_name = name
                if idx >= defstart:
                    ae.entry_text = repr(defaults[idx-defstart])
                if name in annotations:
                    if annotations[name] == datatypes.ArgOpenFile:
                        ae.button['command'] = lambda ae=ae: open_file(arg_entry=ae)   
                        ae.button['state'] = 'enable'
                        ae.button['text'] = 'Select'
        
        def open_file(arg_entry):
            path = tkinter.filedialog.askopenfilename()
            arg_entry.entry_text = repr(path)
        
        def on_ok(event=None):
            for name in argmap:
                argmap[name] = argmap[name].arg_value
            dialog.destroy()
            
        items = tuple(argmap.items())
        items[0][1].entry.focus_set()
        items[-1][1].entry.bind('<Return>', on_ok)            
            
        ok_btn = tkinter.ttk.Button(frmleft, text='ok', command=on_ok)
        ok_btn.pack()
                
        doctext = ScrolledText(frmright)
        doctext.pack(expand='yes', fill='both')
        if func.__doc__:
            doctext.set_text(func.__doc__)
        
        dialog.focus_set()
        dialog.grab_set()
        dialog.wait_window()
        
        return argmap
                     
        
    def print_and_eval(self, expr):
        with self.exec_thread_lock:
            self.stream_manager.write(expr+'\n', 'HISTORY')               
            ret = self.eval(expr)
            if ret is not None:
                self.stream_manager.write(str(ret)+'\n', 'RETVAL')
                
                if isinstance(ret, Path):
                    self.print_tip([{'type':'file_list', 'content':(str(ret),)}])
                    
            return ret    
            
                              
    def eval(self, expr):
        with self.exec_thread_lock:
            try:
                with busy_doing:
                    ret = eval(expr, Scripting.namespace['globals'], Scripting.namespace['locals'])
            except KeyboardInterrupt:
                self.print_tip([{'type':'text', 'content':'The mission has been aborted.'}])
            Scripting.namespace['locals']['_']  = ret
            return ret
            
        
    def execute(self, code):
        with self.exec_thread_lock:
            ret = None
            stripped_code    = code.strip()
            if stripped_code[0] == '!':
                PIPE = subprocess.PIPE
                p = subprocess.Popen(stripped_code[1:], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)  
                (stdout, stderr) = p.communicate()
                encoding = locale.getpreferredencoding()
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
                            exec(code, Scripting.namespace['globals'], Scripting.namespace['locals'])
                        except KeyboardInterrupt:
                            self.print_tip([{'type':'text', 'content':'The mission has been aborted.'}])
            except SystemExit:
                self._on_exit()
            return ret
            
            
    def print_tip(self, contents): # To Do: Move the main logic to the console.
        # To Do: Use the new create_link_tag method of ScrolledText
        def config_link_tag(widget, tag_name, command, original_cursor):
            widget.tag_config(tag_name, underline=1, foreground='blue')
            widget.tag_bind(tag_name, '<Button-1>', command)
            widget.tag_bind(tag_name, '<Enter>', lambda dumb: text.config(cursor='hand2'))
            widget.tag_bind(tag_name, '<Leave>', lambda dumb: text.config(cursor=original_cursor))
        
        if self.no_tip:
            return
        stream_manager = self.stream_manager
        stream_manager.write('WaveSyn: \n', 'TIP')

        if isinstance(contents, str):
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
                text = self.gui.console.text
                #r, c = text.index(END).split('.')
                config_link_tag(text, tag_name, command, self.gui.console.default_cursor)                                
                stream_manager.write('\n')
                return_list.append(None)
            elif item['type'] == 'pil_image':
                text    = self.gui.console.text                
                text.insert('end', '\n')
                pil_frame    = PILImageFrame(text, pil_image=item['content'])
                text.window_create('end', window=pil_frame)
                text.insert('end', '\n')
                stream_manager.write('\n')
                return_list.append(id(pil_frame))
            elif item['type'] == 'file_list':
                file_list = item['content']
                def new_open_func(path):
                    def open_func(*args):
                        with code_printer():
                            self.webbrowser_open(path)
                    return open_func
                    
                def new_browse_func(path):
                    def browse_func(*args):
                        with code_printer():
                            self.interfaces.os.win_open(path)
                    return browse_func
                    
                for file_path in file_list:
                    text = self.gui.console.text                    
                    
                    open_func = new_open_func(file_path)
                    open_tag_name = 'link' + str(id(open_func))
                    stream_manager.write('open', open_tag_name)
                    config_link_tag(text, open_tag_name, open_func, self.gui.console.default_cursor)
                    stream_manager.write(' ')

                    browse_func = new_browse_func(file_path)                    
                    browse_tag_name = 'link' + str(id(browse_func))
                    stream_manager.write('browse', browse_tag_name)
                    config_link_tag(text, browse_tag_name, browse_func, self.gui.console.default_cursor)                    
                    stream_manager.write(' ')
                    
                    stream_manager.write(f'{file_path}\n')
                return_list.append(None)
        return return_list
                                            
                
    def print_error(self, text):
        self.stream_manager.write(text+'\n', 'STDERR')
        

    def open_home_page(self):
        '''Open the home page of WaveSyn.'''
        webbrowser.open(self.homepage, new=1, autoraise=True)
             
                    
    def _mainloop(self):
        '''Lauch the event loop of WaveSyn.'''
        return self.gui.mainloop()
        

    def _on_exit(self):   
        '''Called when WaveSyn exit. '''
        self.gui.interrupter.close()
        
        # Here we cannot iterate the 'windows' directly,
        # because the close method will change the size of the dict 'windows',
        # and this will raise a runtime error.
        keys = [key for key in self.gui.windows]
        for key in keys:
            self.gui.windows[key].close()
        self.gui.quit()
    
        
    @classmethod
    def do_events(cls):
        # Please avoid to call this method. 
        # Use the thread manager and the command queue instead.
        cls.instance.gui.root.update()
        
        
    def start_xmlrpc_server(self, addr='localhost', port=8000):
        from wavesynlib.interfaces.xmlrpc.server    import start_xmlrpc_server
        start_xmlrpc_server(addr, port)        
        def check_command():
            command = self.xmlrpc_command_slot.command
            convert_args_to_str  = Scripting.convert_args_to_str
            try:
                if command is not None:
                    node_path, method_name, args, kwargs  = command
                    ret, err    = None, None
                    try:
                        ret = self.print_and_eval(f'{node_path}.{method_name}({convert_args_to_str(*args, **kwargs)})') # paramToStr used here
                    except Exception as error:
                        err = error
                    ret = 0 if ret is None else ret
                    self.xmlrpc_command_slot.return_value    = (ret, err)
            finally:
                # Make sure that at any circumstance the check_command will be called repeatedly.
                self.gui.root.after(100, self.xmlrpc_check_command)
        self.xmlrpc_check_command = check_command
        self.gui.root.after(100, check_command) # To Do: Use TkTimer instead of after
        
        
    @Scripting.printable
    def system(self, command):
        '''Call system command.

command: system command in string form. '''
        subprocess.call(command, shell=True)
        
        
    @Scripting.printable
    def webbrowser_open(self, url:str):
        '''Open the given URL using the default app.
        
    url: string. the URL of the object to be opened.'''
        webbrowser.open(url)
        
        
    @Scripting.printable
    def save_var(self, var, filename, protocol=pickle.HIGHEST_PROTOCOL):        
        from wavesynlib.languagecenter.wavesynscript import Constant
                    
        is_var_name = True if isinstance(var, Constant) else False
            
        dialogs = self.gui.dialogs
        var = dialogs.ask_string(var,
            title='Variable Name',
            prompt='Enter variable name here:')
        
        if not var:
            return
        
        if is_var_name:
            f_locals = Scripting.namespace['locals']
            f_globals = Scripting.namespace['globals']
            if var in f_locals:
                var = f_locals[var]
            else:
                var = f_globals[var]
        
        filename = dialogs.ask_saveas_filename(
            filename,
            filetypes=[('Pickle Files', '*.pkl')])
        
        if not filename:
            return
        
        with open(filename, 'wb') as fileobj:
            pickle.dump(var, fileobj, protocol)
            
            
    @Scripting.printable
    def load_var(self, filename):
        filename = self.gui.dialogs.ask_open_filename(
            filename,
            filetypes=[('Pickle Files', '*.pkl'), ('All Files', '*.*')])
        
        if not filename:
            return
        
        with open(filename, 'rb') as fileobj:
            ret = pickle.load(fileobj)
        return ret
        
        
    @Scripting.printable
    def set_matplotlib_style(self, style_name=''):
        '''Set the plot style of matplotlib.
        
    style_name: string. The name of the new style.'''
        import matplotlib.pyplot as plt
        
        style_name = self.root_node.gui.dialogs.ask_list_item(
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
    wavesyn.gui.interrupter.launch()
    wavesyn._mainloop()
        
        
