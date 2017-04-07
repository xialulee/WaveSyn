# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:08:49 2017

@author: Feng-cong Li
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import six.moves.tkinter_tix as Tix


from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, model_tree_monitor, code_printer
from wavesynlib.guicomponents.tk import TaskbarIcon, ValueChecker
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.toolwindows.interrupter.modelnode import InterrupterNode
from wavesynlib.toolwindows import simpledialogs
from wavesynlib.toolwindows.basewindow import WindowDict
from wavesynlib.gui.tk.console import ConsoleWindow



class TkNode(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__console_menu = kwargs.pop('console_menu')
        self.__tag_defs = kwargs.pop('tag_defs')
        super(TkNode, self).__init__(*args, **kwargs)
        self._on_exit = None        
        
        
    def on_connect(self):
        with self.attribute_lock:
            self.root = Tix.Tk()
            self.balloon = Tix.Balloon(self.root)
            self.taskbar_icon = TaskbarIcon(self.root)
            self.interrupter = InterrupterNode()
            self.dialogs = simpledialogs.Dialogs()
            self.windows = WindowDict()
            self.value_checker = ValueChecker(self.root)
            self.console = ConsoleWindow(root=self.root, menu=self.__console_menu, tag_defs=self.__tag_defs)
        
        
    @Scripting.printable
    def get_gui_name(self):
        return 'tk'
        
        
    @property
    def on_exit(self):
        return self._on_exit
        
        
    @on_exit.setter
    def on_exit(self, val):
        self._on_exit = val
        self.root.protocol('WM_DELETE_WINDOW', self._on_exit)
        
        
    def create_timer(self, interval=100, active=False):
        return TkTimer(self.root, interval, active)
        
        
    def mainloop(self):
        self.root.mainloop()
        
        
    def quit(self):
        self.root.quit()