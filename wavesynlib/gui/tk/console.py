# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 02:49:38 2016

@author: Feng-cong Li
"""
import os
from io import StringIO
import pathlib
import importlib

from tkinter import Menu, IntVar, Toplevel
from tkinter.ttk import Progressbar, Scale, Combobox
from tkinter import Frame, Label
from PIL import ImageTk

from tkinter.filedialog import asksaveasfilename
import queue
import _thread as thread
from pathlib import Path
from datetime import datetime
import traceback

import jedi
import quantities as pq

from wavesynlib.stdstream import dumb_stream
from wavesynlib.widgets.tk.cwdindicator import CWDIndicator
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.scrolledtext import ScrolledText
from wavesynlib.widgets.tk.pilimageframe import PILImageFrame
from wavesynlib.widgets.tk.syntaxhighlighter import SyntaxHighlighter
from wavesynlib.widgets.tk.tkredirector import WidgetRedirector
from wavesynlib.widgets.tk.busylight import BusyLight
from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.languagecenter.utils import call_immediately, FunctionChain
from wavesynlib.languagecenter import templates
from wavesynlib.status import busy_doing
from .candidatelist import CandidateList



_retvaldisp = {}

@call_immediately
def load_plugin():
    selfdir = pathlib.Path(__file__).parent
    retvaldisp = selfdir / 'plugins' / 'retvaldisp'
    files = filter(
        lambda p: p.stem != "__init__",
        retvaldisp.glob('*.py'))
    for file in files:
        mod_name = file.stem
        mod_path = f'wavesynlib.gui.tk.plugins.retvaldisp.{mod_name}'
        mod = importlib.import_module(mod_path)
        plugin = mod.Plugin(Scripting.root_node)
        _type = plugin._type
        if _type not in _retvaldisp:
            _retvaldisp[_type] = [plugin]
        else:
            _retvaldisp[_type].append(plugin)



def make_menu(win, menu, json=False):
    def func_gen(code, print_code=True):
        if print_code:
            f = Scripting.root_node.lang_center.wavesynscript.display_and_eval
        else:
            f = Scripting.root_node.lang_center.wavesynscript.eval
            
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
        self.text.bind('<KeyRelease>', self.on_key_release)
        
        # Begin syntax highlight
        self.__syntax_highlighter = SyntaxHighlighter(
            text_widget = self.text,
            syntax_tags = self.__syntax_tags)
        self.__redir = redir = WidgetRedirector(self.text)
        self.__true_insert = redir.register('insert', self.__insert_hook)
        self.__true_delete = redir.register('delete', self.__delete_hook)        
        # End syntax highlight

        self.indentwidth    = 4
        self.tabwidth       = 4
        self.context_use_ps1    = '>>> '
                                      
        self.prompt_symbol = '>>> '  
        
        # should use func chain
        self.__encounter_func_callback = FunctionChain()

        # A small pop window for displaying auto completion candidates.
        self.candidate_list = CandidateList()


    def on_connect(self):
        self.__shell = shell = self.root_node.lang_center.wavesynscript.interactive_shell
        self.__history = shell.history
        
        
    def __insert_hook(self, index, chars, tags=None):
        highlight = self.__syntax_highlighter.highlight_one_row
        if tags:
            # All of the text inserted by WaveSyn has a tag (except the prompts). 
            self.__true_insert(index, chars, tags)            
        else: # To do: handle multiline text                    
            if len(chars) == 1 or '\n' not in chars:
                self.__true_insert(index, chars)
                r, c = self.get_cursor_pos(index)
                highlight(row=r)
            else:
                lines = chars.split('\n')
                if not lines[-1]:
                    del lines[-1]
                for line in lines:
                    self.__true_insert(index, line)
                    r, c = self.get_cursor_pos(index)
                    highlight(row=r)
                    self.on_key_press(KeyEventSim('Return'))
    
    
    def __delete_hook(self, index1, index2=None):
        self.__true_delete(index1, index2)
        r, c = self.get_cursor_pos('insert')
        if self.text.get(f'{r}.0', f'{r}.3') in ('>>>', '...'):
            self.__syntax_highlighter.highlight_one_row(row=r)        
        
        
    @property                    
    def encounter_func_callback(self):
        return self.__encounter_func_callback
                    
        
    def update_content(self, tag, content, extras=None):
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
        
        if tag == 'RETVAL':
            if extras and 'obj' in extras:
                ret = extras['obj']
                plugins = []
                
                for _type in _retvaldisp:
                    if isinstance(ret, _type):
                        plugins.extend(_retvaldisp[_type])

                for plugin in plugins:
                    plugin.action(ret)     
        
        self.text.update()
        
        
    def on_key_release(self, event):
        r, c = self.get_cursor_pos('insert')
        current_code = self.text.get(f'{r}.4', f'{r}.{c}')
        #script = jedi.api.Interpreter(
            #current_code,
            #[Scripting.namespaces['locals'], Scripting.namespaces['globals']])
        #try:
            #with dumb_stream(stderr=True):
                #cs = script.goto_assignments()
        #except:
            #pass
        #else:
            #if cs:
                #self.__encounter_func_callback(cs)


    def _on_launch_autocomplete(self):
        r = self.get_cursor_pos('insert')[0]
        script = jedi.api.Interpreter(
            self.text.get(f'{r}.4', 'end-1c'), 
            [Scripting.namespaces['locals'], 
                Scripting.namespaces['globals']])

        completions = script.complete()
        
        match len(completions):
            case 0:
                return
            case 1:
                completion = completions[0]
                cstr = completion.complete
                self.text.insert('end', cstr)
                return
            case _:
                pass

        self.candidate_list.launch(completions)


    def _on_goto_line_start(self):
        text_widget = self.text
        r = self.get_cursor_pos()[0]
        r_0, r_4 = f"{r}.0", f"{r}.4"
        leading = text_widget.get(r_0, r_4)
        new_pos = r_4 if leading in ("... ", ">>> ") else r_0
        text_widget.mark_set("insert", new_pos)
            

    def on_key_press(self, event, 
            code_list=[], 
            init_history=[True],
            line_continuation=[False]):     
        # Begin Support History
        if event.keysym not in ('Up', 'Down'):
            init_history[0] = True
        else:
            r_end = self.get_cursor_pos(mark='end')[0]
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
                1 if event.keysym in ('Up', 'KP_Up') 
                else -1)
            self.text.insert('end', code)
            self.__syntax_highlighter.highlight_one_row(row=r)
            return 'break'     
        # End Support History
            
        if event.keysym == 'Tab':
            self._on_launch_autocomplete()
            return 'break'
            
        if event.keysym in ('KP_Home', 'Home'):
            self._on_goto_line_start()
            return 'break'

        # Using keycode is not a good practice here, because for the same key,
        # the keycode may vary on different machines and operating systems.
        #if event.keysym not in ('Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R',  'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 'KP_Left', 'KP_Right', 'KP_Up', 'KP_Down', 'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Next', 'Prior'):
        if (event.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_MODIFIERS.value) and \
           (event.keysym not in self.root_node.lang_center.wavesynscript.constants.KEYSYM_CURSORKEYS.value):
            r, c    = self.get_cursor_pos()
            prompt  = self.text.get(f'{r}.0', f'{r}.4')
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if event.keysym == 'BackSpace' and c <= 4:
                return 'break'
            if event.keysym == 'Escape':
                self.text.delete(f'{r}.4', 'end')
            if c < 4:
                return 'break'
            rend = self.get_cursor_pos('end-1c')[0]
            if r < rend:
                return 'break'
            
            if event.keysym == 'Return': 
                code = self.text.get(f'{r}.4', f'{r}.end')
                if code.strip() == "exit":
                    code = code.replace("exit", "exit()")
                self.__history.put(code)
                try:
                    status, funcobj = self.__shell.feed(code)
                    if status == "APPEND":
                        self.prompt_symbol = "... "
                    elif status == "EXECUTE":
                        self.prompt_symbol = ">>> "
                    self.update_content(tag="", content="\n")
                    ret = funcobj()
                    if ret is not None:
                        repr_ret = repr(ret)
                        maxlen = 1000
                        if len(repr_ret) > maxlen:
                            repr_ret = f'{repr_ret[:maxlen-10]}\n\n...\n\n{repr_ret[-10:]}'
                        self.update_content(tag='RETVAL', content=f'{repr_ret}\n', extras={'obj':ret})    
                finally:
                    self.text.mark_set('insert', 'end')
                    self.text.see('end')
                    return 'break'
                    #! Do Not append anything below this line in this function, 
                    #  because the return "break" statement is already executed. 

                
    def get_cursor_pos(self, mark='insert'): 
        r, c = (int(i) for i in self.text.index(mark).split('.'))
        return r, c
        

class StatusBar(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        timer = TkTimer(widget=self, interval=0.2*pq.second, active=False)
        
        self.__battery_images = battery_images = {}
        image_dir = Path(Scripting.root_node.get_gui_image_path('battery'))
        for image_name in ['10per', '25per', '50per', '75per', '100per',
                           '10per_charge', '25per_charge', 
                           '50per_charge', '75per_charge', '100per_charge']:
            battery_images[image_name] = ImageTk.PhotoImage(
                file=str(image_dir/(image_name+'.png')))
            
        balloon = Scripting.root_node.gui.balloon
                        
        self.__busy_lamp = busy_lamp = BusyLight(self)
        busy_lamp.pack(side='right', fill='y')
        
        balloon.bind_widget(busy_lamp, balloonmsg='''Main-thread status.
Green: main-thread is available;
Red:   main-thread is busy.''')
        
        battery_meter = Label(self)
        battery_meter.pack(side='right', fill='y')
        battery_meter_tip = balloon.bind_widget(battery_meter, balloonmsg='Battery: ')
        def battery_meter_tip_show_callback():
            battery_status = Scripting.root_node.interfaces.os.get_battery_status()
            if battery_status is None:
                return 'No battery detected.'
            else:
                return f'{battery_status.percent}%'
        battery_meter_tip.show_callback = battery_meter_tip_show_callback
        
        self.__membar = IntVar(value=0)
        self.__cpubar = IntVar(value=0)
        self._make_cpu_mem_status()

        # Transparent Scale {
        def on_scale(val):
            Scripting.root_node.gui.console.set_opacity(val)
        trans_scale = Scale(self, from_=0.2, to=1.0, orient='horizontal', value=1, command=on_scale)
        trans_scale.pack(side='right')
        balloon.bind_widget(trans_scale, balloonmsg='Set the opacity of the console.')
        # } End Transparent Scale

        # Topmost Button {
        import tkinter
        topmost_button = tkinter.Button(self, text='TOP', relief='groove') 
        topmost_button.pack(side='right')
        
        def on_click():
            console =Scripting.root_node.gui.console
            b = console.is_topmost
            fg = 'black' if b else 'lime green'
            topmost_button['fg'] = fg
            with code_printer(True):
                console.set_topmost(not b)
            
        topmost_button['command'] = on_click
        balloon.bind_widget(topmost_button, balloonmsg='Set the console as a topmost window.')
        # } End Topmost Button 
        
        # Doc Button {
        (docbtn := \
            tkinter.Button(self, text='DOC', relief='groove')
        ).pack(side="right")
        
        def on_click():
            docwin = Scripting.root_node.gui.console.doc_window
            with code_printer(True):
                docwin.show_window()
                
        docbtn['command'] = on_click
        balloon.bind_widget(docbtn, balloonmsg='Show document window.')
        #} End Doc Window        
        
        # Debug Button {
        (debbtn := \
            tkinter.Button(self, text='DEB', relief='groove')
        ).pack(side='right')
        
        def on_click():
            debwin = Scripting.root_node.gui.console.debug_window
            with code_printer(True):
                debwin.show_window()
                
        debbtn['command'] = on_click
        balloon.bind_widget(debbtn, balloonmsg='Show debug window.')
        #} End Debug Button
        
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
             
        os_node = Scripting.root_node.interfaces.os
        get_memory_usage = os_node.get_memory_usage
        get_cpu_usage    = os_node.get_cpu_usage
        get_battery_status = os_node.get_battery_status
                                
        def check_cpu_mem_battery(event):
            with code_printer(print_=False):
                self.__membar.set(get_memory_usage())
                self.__cpubar.set(get_cpu_usage())
                battery_status = get_battery_status()
                if battery_status:
                    percent = battery_status.percent
                    if percent > 75:
                        percent = 100
                    elif percent > 50:
                        percent = 75
                    elif percent > 25:
                        percent = 50
                    elif percent > 10:
                        percent = 25
                    else:
                        percent = 10
                    
                    charge = '_charge' if battery_status.power_plugged else ''
                    image_name = f'{percent}per{charge}'
                    image = battery_images[image_name]
                    if battery_meter['image'] != image:
                        battery_meter['image'] = image
                
        timer.divider(divide_by=10).add_observer(check_cpu_mem_battery)                
        timer.active = True
        # To Do: add several customizable lamps for users.
        
    def _set_busy_light(self):
        self.__busy_lamp.busy = self.__busy
        
    def set_busy(self, busy=True):
        with self.__lock:
            self.__busy = busy
        if Scripting.root_node.thread_manager.in_main_thread:
            # Only main thread can set busy light
            self._set_busy_light()
            
    def _make_cpu_mem_status(self):
        balloon = Scripting.root_node.gui.balloon

        def on_progbar_dbclick(app):
            with code_printer():
                Scripting.root_node.gadgets.launch(app)
        
        mem_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__membar)
        mem_progbar.pack(side='right', fill='y')
        mem_progbar.bind('<Double-Button-1>', lambda dumb: on_progbar_dbclick('wsmemmeter.pyw'))
        membar_tip = balloon.bind_widget(mem_progbar, balloonmsg='Total memory usage:')
        membar_tip.show_callback = lambda: f' {Scripting.root_node.interfaces.os.get_memory_usage()}%.'
        
        cpu_progbar = Progressbar(self, orient="horizontal", length=60, maximum=100, variable=self.__cpubar)
        cpu_progbar.pack(side='right', fill='y')
        cpu_progbar.bind('<Double-Button-1>', lambda dumb: on_progbar_dbclick('wscpugauge.pyw'))
        cpubar_tip = balloon.bind_widget(cpu_progbar, balloonmsg='Total CPU usage: ')        
        cpubar_tip.show_callback = lambda: f' {Scripting.root_node.interfaces.os.get_cpu_usage()}%.'
        
        
        
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

        CWDIndicator(chdir_func=chdir_func).pack(fill="x")
        self.__status_bar = status_bar = StatusBar(root)
        status_bar.pack(side='bottom', fill='x')
        
        self.console_text = ConsoleText(root, tag_defs=self.__tag_defs)        
        self.__stdstream_text = stdstream_text = self.console_text
        stdstream_text.pack(expand='yes', fill='both')
                    
        busy_doing.add_observer(
            lambda event: status_bar.set_busy(True if event.name=="busy" else False))

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

        self.root_node.stream_manager.add_observer(lambda event:
            self.console_text.update_content(
                tag=event.kwargs["stream_type"],
                content=event.kwargs["content"],
                extras=event.kwargs["extras"]))
            
        self.doc_window = ModelNode(
            is_lazy=True, 
            module_name='wavesynlib.gui.tk.docwindow', 
            class_name='DocWindow')       
        
        self.debug_window = ModelNode(
            is_lazy=True,
            module_name='wavesynlib.gui.tk.debugwindow',
            class_name='DebugWindow')
    
        
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
    
                                                                    
    @WaveSynScriptAPI    
    def save(self, filename): # for scripting system
        with open(filename, 'w') as f:
            f.write(self.__stdstream_text.get_text())
            
            
    def on_save_as(self):        
        filename    = asksaveasfilename(filetypes=[('All types of files', '*.*')])
        if not filename:
            return
        with code_printer():
            self.save(filename)
            
    
    @WaveSynScriptAPI    
    def clear(self):
        self.__stdstream_text.clear()
        print('', sep='', end='')
        
        
    def on_clear(self):
        with code_printer():
            self.clear()
            

    def set_window_attributes(self, *args, **kwargs):
        return self.root_node.gui.root.wm_attributes(*args, **kwargs)  
      
     
    @WaveSynScriptAPI
    def set_topmost(self, b):
        tk_root = self.root_node.gui.root
        if b == 'flip':
            b = False if self.is_topmost else True
        tk_root.wm_attributes('-topmost', b)
        
        
    @property
    def is_topmost(self):
        tk_root = self.root_node.gui.root
        return bool(tk_root.wm_attributes('-topmost'))
        
        
    def set_opacity(self, opacity):
        self.root_node.gui.root.wm_attributes('-alpha', opacity)
        
        
    def show_tips(self, contents, prompt=True):         
        if self.root_node.no_tip:
            return
        
        stream_manager = self.root_node.stream_manager
        if prompt:
            stream_manager.write('WaveSyn: \n', 'TIP')

        if isinstance(contents, str):
            stream_manager.write(contents+'\n', 'TIP')
            return

        return_list = []            

        console_text = self.console_text
        text = console_text.text
        
        # For "open" link.
        def new_open_func(path):
            def open_func(*args):
                with code_printer():
                    self.root_node.webbrowser_open(path)
            return open_func
            
        # For "browse" link.
        def new_browse_func(path):
            def browse_func(*args):
                with code_printer():
                    self.root_node.interfaces.os.win_open(path)
            return browse_func        
                    
        for item in contents:
            end = item.get('end', '\n')

            match item["type"]:
                case "text":
                    stream_manager.write(f'{item["content"]}{end}', 'TIP')
                    return_list.append(None)
                case "link":
                    command = item['command']
                    tag_name = console_text.create_link_tag(command, self.default_cursor)                
                    stream_manager.write(item['content'], tag_name)
                    stream_manager.write(end)
                    return_list.append(None)
                case "pil_image":
                    text.insert('end', '\n')
                    pil_frame = PILImageFrame(text, pil_image=item['content'], balloon=self.root_node.gui.balloon)
                    text.window_create('end', window=pil_frame)
                    text.insert('end', '\n')
                    stream_manager.write(end)
                    return_list.append(id(pil_frame))
                case "file_list":
                    file_list = item['content']                 
                    for file_path in file_list:
                        open_func = new_open_func(file_path)
                        open_tag_name = console_text.create_link_tag(open_func, self.default_cursor)
                        stream_manager.write('open', open_tag_name)
                        stream_manager.write(' ')

                        browse_func = new_browse_func(file_path)                    
                        browse_tag_name = console_text.create_link_tag(browse_func, self.default_cursor)
                        stream_manager.write('browse', browse_tag_name)                    
                        stream_manager.write(' ')
                        
                        stream_manager.write(f'{file_path}{end}', 'TIP')
                    return_list.append(None)
                case "directories":
                    dir_list = item['content']
                    for dir_path in dir_list:
                        browse_func = new_browse_func(dir_path)
                        browse_tag_name = console_text.create_link_tag(browse_func, self.default_cursor)
                        stream_manager.write('browse', browse_tag_name)
                        stream_manager.write(' ')
                        stream_manager.write(f'{dir_path}{end}', 'TIP')
        return return_list
