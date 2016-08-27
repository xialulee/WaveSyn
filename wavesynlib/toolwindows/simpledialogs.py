# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 22:01:43 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os

from six.moves.tkinter_tksimpledialog import askstring, askinteger
from six.moves.tkinter_messagebox import showinfo, askyesno
from six.moves.tkinter_tkfiledialog import asksaveasfilename, askopenfilename, askopenfilenames

from wavesynlib.guicomponents.tk import ask_list_item

from wavesynlib.languagecenter.wavesynscript import ModelNode, constant_handler


class Dialogs(ModelNode):    
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        
    @constant_handler() 
    def support_ask_yesno(self, arg, **kwargs):
        return askyesno(**kwargs)            
        
    @constant_handler()
    def support_ask_integer(self, arg, **kwargs):
        return askinteger(**kwargs)
                
    @constant_handler()
    def support_ask_list_item(self, arg, **kwargs):
        return ask_list_item(**kwargs)
    
    @constant_handler()
    def support_ask_files(self, arg, **kwargs):
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
    
    @constant_handler()
    def support_ask_ordered_files(self, arg, **kwargs):
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
        
    @constant_handler()
    def support_ask_open_filename(self, arg, **kwargs):
        return askopenfilename(**kwargs)
        
    @constant_handler()
    def support_ask_saveas_filename(self, arg, **kwargs):
        return asksaveasfilename(**kwargs)
        
    @constant_handler()
    def support_ask_slice(self, arg, **kwargs):
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
        