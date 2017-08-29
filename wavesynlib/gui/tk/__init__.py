# -*- coding: utf-8 -*-
"""
Created on Fri Apr 07 17:08:49 2017

@author: Feng-cong Li
"""
import tkinter.tix as Tix


from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.guicomponents.tk import TaskbarIcon, ValueChecker
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.toolwindows.interrupter.modelnode import InterrupterNode
from wavesynlib.toolwindows import simpledialogs
from wavesynlib.toolwindows.basewindow import WindowDict
from wavesynlib.gui.tk.console import ConsoleWindow



class TkNode(ModelNode):
    '''TkNode is a ModelNode which maintains the Tk root window object,
and related utilities like Balloon, value checker, and some other related
WaveSyn components. 
'''
    def __init__(self, *args, **kwargs):
        self.__console_menu = kwargs.pop('console_menu')
        self.__tag_defs = kwargs.pop('tag_defs')
        super().__init__(*args, **kwargs)
        self._on_exit = None        
        
        
    def on_connect(self):
        super().on_connect()
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
        '''The on_exit property is a callable object, 
which will be called on the exit event of WaveSyn.'''
        return self._on_exit
        
        
    @on_exit.setter
    def on_exit(self, val):
        self._on_exit = val
        self.root.protocol('WM_DELETE_WINDOW', self._on_exit)
        
        
    def create_timer(self, interval=100, active=False):
        '''Create an instance of TkTimer. 
interval: the interval of the timer.
    Default: 100
    Unit: millisecond.
active: True for activating the timer, and False for deactivating. 
    Default: False

The TkTimer is based on the Observer protocol.
'''
        return TkTimer(self.root, interval, active)
        
        
    def mainloop(self):
        '''Lauch the event loop of Tk.'''
        self.root.mainloop()
        
        
    def quit(self):
        self.root.quit()