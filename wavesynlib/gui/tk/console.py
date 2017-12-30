# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 02:49:38 2016

@author: Feng-cong Li
"""
# Some console functionalities are implemented by idlelib
##########################
#from idlelib.AutoComplete import AutoComplete
#import idlelib.AutoCompleteWindow
#idlelib.AutoCompleteWindow.KEYPRESS_SEQUENCES = ()
##########################
import os
from tkinter import Menu, IntVar, Toplevel
from tkinter.ttk import Progressbar, Scale, Combobox
from tkinter import Frame, Label

from tkinter.filedialog import asksaveasfilename
import queue
import _thread as thread

from datetime import datetime
import traceback

import jedi

from wavesynlib.guicomponents.tk import CWDIndicator, ScrolledText, ScrolledList
from wavesynlib.guicomponents.tkredirector import WidgetRedirector
from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, code_printer
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.languagecenter.designpatterns import SimpleObserver
from wavesynlib.languagecenter.utils import call_immediately
from wavesynlib.languagecenter import templates
from wavesynlib.languagecenter.python import prog as prog_pattern
from wavesynlib.status import busy_doing



def make_menu(win, menu, json=False):
    def func_gen(code, print_code=True):
        if print_code:
            f   = Scripting.root_node.print_and_eval
        else:
            f   = Scripting.root_node.eval
            
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
    
    
    
class History:
    '''Class for supporting console history.'''
    def __init__(self, max_records=50):
        self.__max_records = max_records
        self.__history_list = ['']
        self.__search_list = None
        self.__cursor = 0
        
        
    def get(self, direction):
        '''direction...'''
        direction = 1 if direction > 0 else -1
        new_cursor = self.__cursor + direction

        # Always return a string for this function
        if 0<=new_cursor<=len(self.__search_list):
            self.__cursor = new_cursor
            return self.__search_list[-new_cursor]        
        else:
            return self.__search_list[0]

        
            
    def put(self, code):
        '''Append a line of code to the history list.'''
        self.__history_list.append(code)
        if len(self.__history_list) > self.__max_records + 1:
            del self.__history_list[1]
            
            
    def search(self, code):
        if code:
            self.__search_list = [code]
            for line in self.__history_list:
                if code == line[:len(code)]:
                    self.__search_list.append(line)
        else:
            self.__search_list = self.__history_list            
            
            
    def reset_cursor(self):
        self.__search_list = None
        self.__cursor = 0
        
        

class KeyEventSim:
    def __init__(self, keysym):
        self.keysym = keysym


  
# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm              
class ConsoleText(ModelNode, ScrolledText):    
    def __init__(self, *args, **kwargs):
        tag_defs = kwargs.pop('tag_defs')
        super().__init__(*args, **kwargs)
        # The shared queue of the PRODUCER-CONSUMER model.
        self.__queue    = queue.Queue()
        self.text['wrap']   = 'word'
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')
        
        self.__syntax_tags = []
        for tag in tag_defs:
            self.__syntax_tags.append(tag)
            self.text.tag_configure(tag, **tag_defs[tag])
        
        self.text.bind('<KeyPress>', self.on_key_press)
        
        # Begin syntax highlight
        self.__redir = redir = WidgetRedirector(self.text)
        self.__true_insert = redir.register('insert', self.__insert_hook)
        self.__true_delete = redir.register('delete', self.__delete_hook)        
        # End syntax highlight

        
        # Auto complete is implemented by idlelib
        #############################################################
        self.indentwidth    = 4
        self.tabwidth       = 4
        self.context_use_ps1    = '>>> '
        #self.__auto_complete = AutoComplete(self)  
        #############################################################
                                      
        self.prompt_symbol = '>>> '  
        self.__history = History()
        
        
    def __insert_hook(self, index, chars, tags=None):
        if tags:
            # All of the text inserted by WaveSyn has a tag (except the prompts). 
            self.__true_insert(index, chars, tags)            
        else: # To do: handle multiline text                    
            if len(chars) == 1 or '\n' not in chars:
                self.__true_insert(index, chars)
                r, c = self.get_cursor_pos(index)
                self.__syntax_highlight(row=r)
            else:
                lines = chars.split('\n')
                if not lines[-1]:
                    del lines[-1]
                for line in lines:
                    self.__true_insert(index, line)
                    r, c = self.get_cursor_pos(index)
                    self.__syntax_highlight(row=r)                    
                    self.on_key_press(KeyEventSim('Return'))
    
    
    def __delete_hook(self, index1, index2=None):
        self.__true_delete(index1, index2)
        r, c = self.get_cursor_pos('insert')
        if self.text.get(f'{r}.0', f'{r}.3') in ('>>>', '...'):
            self.__syntax_highlight(row=r)        
        
        
    def __syntax_highlight(self, row):
        for tag in self.__syntax_tags:
            self.text.tag_remove(tag, f'{row}.0', f'{row}.end')
            
        line = self.text.get(f'{row}.0', f'{row}.end')
        start = 0
        while True: 
            m = prog_pattern.search(line, start)
            if not m: 
                break
            start = m.end()
            for key, value in m.groupdict().items():
                if value:
                    self.text.tag_add(key, 
                                      f'{row}.{m.start()}',
                                      f'{row}.{m.end()}')
        
        
    def update_content(self, tag, content):
        r, c    = self.get_cursor_pos('end')
        start   = 'end-5c'
        stop    = 'end-1c'
        if self.text.get(start, stop) == '>>> ' or self.text.get(start, stop) == '... ':
            self.text.delete(start, stop)

        # Record the position of the END before inserting anything.
        start    = self.text.index('end')

        self.text.insert('end', content, tag)

        self.text.insert('end', self.prompt_symbol, 'STDOUT')                
        self.text.see('end') 
        

    def on_key_press(self, evt, code_list=[], init_history=[True]):     
        # Begin Support History
        if evt.keysym not in ('Up', 'Down'):
            init_history[0] = True
        else:
            r_end, c_end = self.get_cursor_pos(mark='end')
            r, c = self.get_cursor_pos()
            
            if r != r_end-1:
                return
            
            if init_history[0]:
                self.__history.reset_cursor()
                current_input = self.text.get(f'{r}.4', 'end-1c')
                self.__history.search(current_input)
                init_history[0] = False

            self.text.delete(f'{r}.4', 'end')
            code = self.__history.get(
                1 if evt.keysym in ('Up', 'KP_Up') 
                else -1)
            self.text.insert('end', code)
            return 'break'     
        # End Support History
            
            
        # Begin: Tab key for auto complete
        if evt.keysym == 'Tab':
            # Using call_immediately to make an independent namespace, which
            # prevents the contamination of namespace.
            @call_immediately
            def do():
                r, c = self.get_cursor_pos('insert')
                script = jedi.api.Interpreter(
                    self.text.get(f'{r}.4', 'end-1c'), 
                    [Scripting.namespace['locals'], 
                     Scripting.namespace['globals']])
    
                if len(script.completions())==0:
                    return 'break'
    
                if len(script.completions())==1:
                    cstr = script.completions()[0].complete
                    self.text.insert('end', cstr)
                    return 'break'
                
                acw = Toplevel(self.text)            
                acw.wm_overrideredirect(1)
                namelist = ScrolledList(acw)
                namelist.pack(expand='yes', fill='both')
                namelist.list_config(selectmode='single')
                x, y, w, h = self.text.bbox('insert')
                x += self.text.winfo_rootx()
                y += self.text.winfo_rooty()
                acw.geometry(f'+{x}+{y+h}')
                namelist.list.focus_set()
                
                def on_exit(event):
                    acw.destroy()
                
                acw.bind('<FocusOut>', on_exit)   
                namelist.list.bind('<Escape>', on_exit)
                
                def on_updown(event, direction):
                    cursel = int(namelist.current_selection[0])
                    newsel = cursel + direction
                    if not (0<= newsel < namelist.length):
                        return 'break'
                    namelist.selection_clear(cursel)
                    namelist.selection_set(newsel)
                    namelist.see(newsel)
                    return 'break'
                    
                namelist.list.bind('<Down>', lambda event:on_updown(event, 1))
                namelist.list.bind('<Tab>', lambda event:on_updown(event, 1))
                namelist.list.bind('<Up>', lambda event:on_updown(event, -1))
                namelist.list.bind('<Shift-Tab>', lambda event:on_updown(event, -1))
                                
                for completion in script.completions():
                    namelist.append(completion.name)
                namelist.selection_set(0)
                
                def on_select(event):
                    cursel = int(namelist.current_selection[0])
                    cstr = script.completions()[cursel].complete
                    self.text.insert('end', cstr)
                    on_exit(None)
                    
                namelist.list.bind('<Return>', on_select)
                namelist.list.bind('<ButtonRelease-1>', on_select)
                
                keyseq = ['']
                def on_key_press(event):
                    if (evt.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_MODIFIERS.value) and \
                        (evt.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_CURSORKEYS.value):
                        keyseq[0] += event.keysym
                        for idx, completion in enumerate(script.completions()):
                            if completion.complete.startswith(keyseq[0]):
                                cursel = int(namelist.current_selection[0])
                                namelist.selection_clear(cursel)
                                namelist.selection_set(idx)
                                namelist.see(idx)
                                return
                        on_exit(None)
                    else:
                        return
                namelist.list.bind('<KeyPress>', on_key_press)
                # No more key bindings hereafter. 
            return 'break'
        # End
            
            
        # Begin control the cursor when HOME key pressed.
        if evt.keysym in ('KP_Home', 'Home'):
            r, c = self.get_cursor_pos()
            leading = self.text.get(f'{r}.0', f'{r}.4')
            if leading in ('... ', '>>> '):
                # The head position of a line is after the prompt. 
                self.text.mark_set('insert', f'{r}.4')
            else:
                self.text.mark_set('insert', f'{r}.0')
            return 'break'
        # End
            
            
        ##############################################################
        # Using keycode is not a good practice here, because for the same key,
        # the keycode may change on different machines and operating systems.
        #if evt.keysym not in ('Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R',  'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 'KP_Left', 'KP_Right', 'KP_Up', 'KP_Down', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Next', 'Prior'):
        if (evt.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_MODIFIERS.value) and \
           (evt.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_CURSORKEYS.value):
            r, c    = self.get_cursor_pos()
            prompt  = self.text.get(f'{r}.0', f'{r}.4')
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if evt.keysym == 'BackSpace' and c <= 4:
                return 'break'
            if evt.keysym == 'Escape':
                self.text.delete(f'{r}.4', 'end')
            if c < 4:
                return 'break'
            rend, cend  = self.get_cursor_pos('end-1c')
            if r < rend:
                return 'break'                
            if evt.keysym == 'Return': # Return
                app = Scripting.root_node
                code = self.text.get(f'{r}.4', f'{r}.end')
                self.__history.put(code)
                try:
                    stripped_code = code.strip()

                    try: # Code is in one mode of WaveSynScript
                        self.root_node.lang_center.wavesynscript.modes.run(stripped_code)
                        self.prompt_symbol   = '>>> '
                        self.update_content(tag='', content='\n')
                        return 'break'
                    except TypeError: # Code is normal Python code.
                        if stripped_code == '':
                            # A blank line ends a block.
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
                    self.text.mark_set('insert', 'end')
                    self.text.see('end')
                    return 'break'
                    # Do Not append anything below this line in this function, 
                    # because the return command is already executed. 

                
    def get_cursor_pos(self, mark='insert'): 
        r, c = (int(i) for i in self.text.index(mark).split('.'))
        return r, c
        

class StatusBar(Frame):
    def __init__(self, *args, **kwargs):
        self.__root_node = kwargs.pop('wavesyn_root')
        Frame.__init__(self, *args, **kwargs)
        timer = TkTimer(widget=self, interval=200, active=False)

        balloon = Scripting.root_node.gui.balloon
                        
        busy_lamp = Label(self, bg='forestgreen', width=1)
        busy_lamp.pack(side='right', fill='y')
        
        balloon.bind_widget(busy_lamp, balloonmsg='''Main-thread status.
Green: main-thread is available;
Red:   main-thread is busy.''')
        self.__busy_lamp = busy_lamp
        
        self.__membar = IntVar(0)
        self.__cpubar = IntVar(0)
        self._make_cpu_mem_status()

        # Transparent Scale {
        def on_scale(val):
            Scripting.root_node.gui.console.set_transparency(val)
        trans_scale = Scale(self, from_=0.2, to=1.0, orient='horizontal', value=1, command=on_scale)
        trans_scale.pack(side='right')
        balloon.bind_widget(trans_scale, balloonmsg='Set the transparency of the console.')
        # } End Transparent Scale

        # Topmost Button {
        import six.moves.tkinter as tkinter
        topmost_button = tkinter.Button(self, text='TOP', relief='groove') 
        topmost_button.pack(side='right')
        
        def on_click():
            tk_root = Scripting.root_node.gui.root
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
            Scripting.root_node.gui.windows[wid].tk_object.deiconify()
        window_combo.bind('<<ComboboxSelected>>', on_selected)
        window_combo.pack(side='right', fill='y') # deiconify a window
        
        @Scripting.root_node.gui.windows.add_observer
        def on_windows_change(node, command):
            values = window_combo['values']
            if values == '':
                values = []
            if isinstance(values, tuple):
                values = list(values)
            node_id = id(node)
            if command == 'new':
                type_name = node.__class__.__name__
                values.append(f'{type_name}: {node_id}')
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
            with code_printer(print_=False):
                # Important! Disable the code printer.
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
        if self.__root_node.thread_manager.in_main_thread:
            # Only main thread can set busy light
            self._set_busy_light()
            
    def _make_cpu_mem_status(self):
        balloon = Scripting.root_node.gui.balloon

        def on_progbar_dbclick(app):
            with code_printer():
                self.__root_node.interfaces.os.windows.launch(app)
        
        mem_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__membar)
        mem_progbar.pack(side='right', fill='y')
        mem_progbar.bind('<Double-Button-1>', lambda dumb: on_progbar_dbclick('memmeter.pyw'))
        balloon.bind_widget(mem_progbar, balloonmsg='Total memory usage.')
        
        cpu_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__cpubar)
        cpu_progbar.pack(side='right', fill='y')
        cpu_progbar.bind('<Double-Button-1>', lambda dumb: on_progbar_dbclick('cpumeter.pyw'))
        balloon.bind_widget(cpu_progbar, balloonmsg='Total CPU usage.')        
        

        
class ConsoleWindow(ModelNode):    
    def __init__(self, *args, **kwargs):
        self.__menu = kwargs.pop('menu')
        self.__tag_defs = kwargs.pop('tag_defs')
        super().__init__(*args, **kwargs)
    

    def on_connect(self):
        app = self.root_node
        root = app.gui.root

        root.title('WaveSyn-Console')
        
        def chdir_func(directory, passive):
            try:
                with code_printer(not passive):
                    self.root_node.interfaces.os.chdir(directory=directory)
            except AttributeError:
                # While the console node is connecting, several components
                # are not ready to use. 
                os.chdir(directory)

        dir_indicator = CWDIndicator(chdir_func=chdir_func)
        dir_indicator.pack(fill='x')

        self.__status_bar = status_bar = StatusBar(root, wavesyn_root=app)
        status_bar.pack(side='bottom', fill='x')
        
        self.console_text = ConsoleText(root, tag_defs=self.__tag_defs)        
        self.__stdstream_text = stdstream_text = self.console_text
        stdstream_text.pack(expand='yes', fill='both')
                    
        @busy_doing.add_observer
        def busy_status_observer(busy):
            status_bar.set_busy(busy)        

        tag_defs = self.__tag_defs
        for key in tag_defs:
            self.text.tag_configure(key, **tag_defs[key])        

        nowtime = datetime.now().hour
        if nowtime >= 19:
            time = 'evening'
        elif nowtime >= 12:
            time = 'afternoon'
        else:
            time = 'morning'
        app.stream_manager.write(templates.greeting.format(time), 'TIP')
        menu = self.__menu
        make_menu(root, menu, json=True)
        self.__default_cursor = self.__stdstream_text.text['cursor']
        @self.root_node.stream_manager.add_observer
        def observer(stream_type, content):
            self.console_text.update_content(tag=stream_type, content=content)
        
        
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
        with code_printer():
            self.save(filename)
            
    
    @Scripting.printable    
    def clear(self):
        self.__stdstream_text.clear()
        print('', sep='', end='')
        
        
    def on_clear(self):
        with code_printer():
            self.clear()
            

    def set_window_attributes(self, *args, **kwargs):
        return self.root_node.tk_root.wm_attributes(*args, **kwargs)  
      
        
    def set_topmost(self, b):
        tk_root = self.root_node.tk_root
        if b == 'flip':
            b = False if tk_root.wm_attributes('-topmost') else True
        tk_root.wm_attributes('-topmost', b)
        
        
    def set_transparency(self, transparency):
        self.root_node.gui.root.wm_attributes('-alpha', transparency)