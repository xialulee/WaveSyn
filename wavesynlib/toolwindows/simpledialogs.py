# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:01:43 2016

@author: Feng-cong Li
"""
import os
from pathlib import Path

import tkinter
from tkinter.simpledialog import askstring, askinteger
from tkinter.messagebox import showinfo, askyesno
from tkinter.filedialog import asksaveasfilename, askopenfilename, askopenfilenames, askdirectory

from wavesynlib.widgets.tk import ask_list_item

from wavesynlib.languagecenter.wavesynscript import ModelNode, constant_handler, code_printer


class Dialogs(ModelNode):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def ask_yesno(self, **kwargs):
        return askyesno(**kwargs)
        
        
    @constant_handler(doc='''Popup a yes/no dialog to ask users for a bool value, 
and the place where this constant holds
will be replaced with True (yes) or False (no).
''') 
    def constant_handler_ASK_YESNO(self, arg, **kwargs):
        '''Popup a dialog to ask users for a bool value.
        
arg: if arg is not the corresponding constant, arg will be returned directly.
**kwargs: see the usage of tkinter.simpledialog.askyesno.'''
        return self.askyesno(**kwargs)    
        
        
    @constant_handler(doc='''Popup a dialog to ask user an integer,
and the place where this constant holds will be replaced with the given integer.
''')
    def constant_handler_ASK_INTEGER(self, arg, **kwargs):
        return askinteger(**kwargs)
    
    
    @constant_handler(doc='''Popup a dialog to ask user a string,
and the place where this constant holds will be replaced with the given string.
''')
    def constant_handler_ASK_STRING(self, arg, **kwargs):
        return askstring(**kwargs)
    
                
    @constant_handler(doc='''Popup a dialog with a list and ask for an item in the list,
and the place where this constant holds will be replaced with the chosen item. 
''')
    def constant_handler_ASK_LIST_ITEM(self, arg, **kwargs):
        return ask_list_item(**kwargs)
    
    
    @constant_handler(doc='''Popup one or more dialogs to ask filenames,
and the place where this constant holds will be replaced with the list of the selected filenames.

Notice: the order of the selection is not preserved. 
''')
    def constant_handler_ASK_FILES(self, arg, **kwargs):
        file_list = []
        while True:
            filenames = askopenfilenames(**kwargs)
            if filenames:
                file_list.extend(filenames)
                kwargs['initialdir'] = os.path.split(filenames[-1])[0]
            if not askyesno('Continue?', 'Continue selecting files?'):
                break
        arg = file_list
        showinfo('File List', 'The following files are selected:\n' + '\n'.join(arg))
        return arg
    
    
    @constant_handler(doc='''Popup one or more dialogs to ask filenames,
and the place where this constant holds will be replaced with the list of the selected filenames,
and the order of the filenames is preserved. 
''')
    def constant_handler_ASK_ORDERED_FILES(self, arg, **kwargs):
        file_list = []
        while True:
            filename = askopenfilename(**kwargs)
            if filename:
                file_list.append(filename)
                kwargs['initialdir'] = os.path.split(filename)[0]
            if not askyesno('Continue?', 'Continue selecting files?'):
                break
        arg = file_list
        showinfo('File List', 'The following files are selected:\n' + '\n'.join(arg))
        return arg   
    
        
    @constant_handler(doc='''Popup a dialog asking a directory,
and the place where this constant holds will be replaced with the selected directory.
''')
    def constant_handler_ASK_DIRECTORY(self, arg, **kwargs):
        return Path(askdirectory(**kwargs))
        
    @constant_handler(doc='''Popup an open file dialog,
and the place where this constant holds will be replaced with the selected filename.
''')
    def constant_handler_ASK_OPEN_FILENAME(self, arg, **kwargs):
        return Path(askopenfilename(**kwargs))
    
        
    @constant_handler(doc='''Popup a saveas dialog,
and the place where this constant holds will be replaced with the selected filename.
''')
    def constant_handler_ASK_SAVEAS_FILENAME(self, arg, **kwargs):
        return Path(asksaveasfilename(**kwargs))
    
        
    @constant_handler('''Popup a dialog asking a slice (Python slice syntax),
and the place where this constant holds will be replaced with the given slice.
''')
    def constant_handler_ASK_SLICE(self, arg, **kwargs):
        title = kwargs.get('title', 'Ask Slice')
        message = kwargs.get('message', 'Input a slice using Python slice syntax.')
        user_input = askstring(title, message)
        if not user_input:
            return
        user_input = user_input.split(':')
        user_input = [int(item) if item else None for item in user_input]
        
        if len(user_input) == 1:
            arg = user_input[0]
        else:
            arg = slice(*user_input)            
        return arg
    
        
    def copy_link_text(self):
        win = tkinter.Toplevel()
        
        tkinter.Label(win, text='Please input link text:').pack()
        text = tkinter.Entry(win)
        text.pack()

        tkinter.Label(win, text='Please input link address:').pack()
        link = tkinter.Entry(win)
        link.pack()

        blank = tkinter.IntVar()
        tkinter.Checkbutton(win, text='target=_blank', var=blank).pack()
        
        def on_ok():
            link_str = link.get()
            text_str = text.get()
            target = '' if not blank.get() else 'target="_blank"'
            with code_printer():
                self.root_node.interfaces.os.clipboard.write(f'<a href="{link_str}" {target}>{text_str}</a>', html=True)
            win.destroy()
        tkinter.Button(win, text='Ok', command=on_ok).pack()
        
        win.focus_set()
        win.grab_set()
        win.wait_window()
        
        
    def report(self, message):
        showinfo('Message', message)
        self.root_node.stream_manager.write(f'\n{message}\n', 'TIP')
        
        