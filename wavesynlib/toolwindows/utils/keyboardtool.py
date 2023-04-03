# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 23:32:52 2016

@author: Feng-cong Li
"""
import tkinter as tk
from tkinter import ttk

from wavesynlib.interfaces.os.windows import disablekeys
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import code_printer, Scripting, WaveSynScriptAPI



class KeyboardToolWindow(TkToolWindow):
    window_name = 'WaveSyn-KeyboardTool'
    
    def __init__(self):
        super().__init__()
        
        disable_tab = tk.Frame(self._tool_tabs)
        self._tool_tabs.add(disable_tab, text='Disable')        
        
        # Start Common group {
        common_group = Group(disable_tab)
        common_group.pack(side='left', fill='y')
        common_group.name = 'Common'
        
        key_codes = [['LWIN', 'RWIN', 'MENU'], ['ALT+ESC', 'ALT+TAB', 'CTRL+ESC']] 
        
        grid_frame = tk.Frame(common_group)
        grid_frame.pack()
        
        def callback(code, var):
            enable = False if var.get() else True
            with code_printer():
                self.enable_key(enable, code)
        
        for n in range(2):
            for m in range(3):
                code = key_codes[n][m]
                var = tk.IntVar(value=0)
                ttk.Checkbutton(grid_frame, text=disablekeys.key_name[code], variable=var, width=10, command=lambda code=code, var=var: callback(code, var)).grid(row=m, column=n)
        # }        
        
        self._make_window_manager_tab()
        
        
    @WaveSynScriptAPI
    def enable_key(self, enable, key_name):
        disablekeys.key_stat[key_name] = enable