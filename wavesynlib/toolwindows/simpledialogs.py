# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:01:43 2016

@author: Feng-cong Li
"""
import os

import tkinter
from tkinter.simpledialog import askstring, askinteger
from tkinter.messagebox import showinfo, askyesno
from tkinter.filedialog import asksaveasfilename, askopenfilename, askopenfilenames, askdirectory

from wavesynlib.guicomponents.tk import ask_list_item

from wavesynlib.languagecenter.wavesynscript import ModelNode, constant_handler, code_printer


class Dialogs(ModelNode):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @constant_handler(doc='''Popup a yes/no dialog to ask users for a bool value, 
and the place where this constant holds
will be replaced with True (yes) or False (no).
''') 
    def ask_yesno(self, arg, **kwargs):
        '''Popup a dialog to ask users for a bool value.
        
arg: if arg is not the corresponding constant, arg will be returned directly.
**kwargs: see the usage of tkinter.simpledialog.askyesno.'''
        return askyesno(**kwargs)    
        
        
    @constant_handler(doc='''Popup a dialog to ask user an integer,
and the place where this constant holds will be replaced with the given integer.
''')
    def ask_integer(self, arg, **kwargs):
        return askinteger(**kwargs)
    
                
    @constant_handler(doc='''Popup a dialog with a list and ask for an item in the list,
and the place where this constant holds will be replaced with the chosen item. 
''')
    def ask_list_item(self, arg, **kwargs):
        return ask_list_item(**kwargs)
    
    
    @constant_handler(doc='''Popup one or more dialogs to ask filenames,
and the place where this constant holds will be replaced with the list of the selected filenames.

Notice: the order of the selection is not preserved. 
''')
    def ask_files(self, arg, **kwargs):
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
    def ask_ordered_files(self, arg, **kwargs):
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
    def ask_directory(self, arg, **kwargs):
        return askdirectory(**kwargs)
        
    @constant_handler(doc='''Popup an open file dialog,
and the place where this constant holds will be replaced with the selected filename.
''')
    def ask_open_filename(self, arg, **kwargs):
        return askopenfilename(**kwargs)
    
        
    @constant_handler(doc='''Popup a saveas dialog,
and the place where this constant holds will be replaced with the selected filename.
''')
    def ask_saveas_filename(self, arg, **kwargs):
        return asksaveasfilename(**kwargs)
    
        
    @constant_handler('''Popup a dialog asking a slice (Python slice syntax),
and the place where this constant holds will be replaced with the given slice.
''')
    def ask_slice(self, arg, **kwargs):
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
        self.root_node.print_tip([{'type':'text', 'content':'\n'+message}])
        
        