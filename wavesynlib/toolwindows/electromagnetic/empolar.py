# -*- coding: utf-8 -*-
"""
Created on Sun Dec 04 17:33:29 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from wavesynlib.widgets.tk.complexcanvas import ComplexCanvas
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow

class PolarWindow(TkToolWindow):
    def __init__(self):
        TkToolWindow.__init__(self)
        self._make_window_manager_tab()