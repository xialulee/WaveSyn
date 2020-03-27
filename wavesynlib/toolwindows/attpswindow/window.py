# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 10:26:00 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

import hy
from wavesynlib.widgets.tk import IQSlider
from wavesynlib.widgets.group import Group
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



class AttPSWindow(TkToolWindow):
    def __init__(self):
        TkToolWindow.__init__(self)
        
        driver_tab = tk.Frame(self._tool_tabs)
        self._tool_tabs.add(driver_tab, text='Driver')
        
        # Load Group {
        load_group = Group(driver_tab)
        load_group.pack(side='left', fill='y')
        load_group.name = 'Load'
        
        load_att_button = ttk.Button(load_group, text='Load Att Driver')
        load_att_button.pack(fill='x')
        load_ps_button = ttk.Button(load_group, text='Load PS Driver')
        load_ps_button.pack(fill='x')
        # } End
        
        self._make_window_manager_tab()
        
        iq_slider = IQSlider(self.tk_object, i_range=128, q_range=128, relief='raised')
        iq_slider.pack(expand='yes', fill='both')