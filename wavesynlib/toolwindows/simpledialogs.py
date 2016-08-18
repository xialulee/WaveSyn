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

from wavesynlib.languagecenter.wavesynscript import ModelNode, Constant


constant_names = []

    
def _arg_handling(func):
    # Automatic constants generation based on method names. 
    constant_name = func.__name__.replace('support_', '').upper()
    constant_names.append(constant_name)
    constant = Constant(constant_name)
    #Wrapper function
    def f(self, arg, **kwargs):
        if arg is constant:
            arg = func(self, arg, **kwargs)
            self._print_actual_value(constant, arg)
        return arg
    return f


class Dialogs(ModelNode):    
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        
    @_arg_handling 
    def support_ask_yesno(self, arg, **kwargs):
        return askyesno(**kwargs)            
        
    @_arg_handling
    def support_ask_integer(self, arg, **kwargs):
        return askinteger(**kwargs)
                
    @_arg_handling
    def support_ask_list_item(self, arg, **kwargs):
        return ask_list_item(**kwargs)
    
    @_arg_handling
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
    
    @_arg_handling
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
        
    @_arg_handling
    def support_ask_open_filename(self, arg, **kwargs):
        return askopenfilename(**kwargs)
        
    @_arg_handling
    def support_ask_saveas_filename(self, arg, **kwargs):
        return asksaveasfilename(**kwargs)
        
    @_arg_handling
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
        
    def _print_actual_value(self, const, value):
        self.root_node.print_tip([{'type':'text', 'content':'''
The actual value of the place where {0} holds is
  {1}'''.format(const.name, repr(value))}])