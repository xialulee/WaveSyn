# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:14:20 2015

@author: Administrator
"""
from tkinter import Toplevel, IntVar
from tkinter.ttk import Button, Checkbutton
from wavesynlib.interfaces.timer.basetimer import BaseObservableTimer, Divider
from wavesynlib.guicomponents.tk import LabeledEntry


class TkTimer(BaseObservableTimer):    
    class ConfigDialog(Toplevel):    
        '''Every instance of the TkTimer needs a Tk widget to call the after method.
If no widget is provided, the TkTimer will create this ConfigDialog,
and use its Toplevel's after method. 
'''             
        def __init__(self, *args, **kwargs):
            timer       = kwargs.pop('timer')
            self.__timer    = timer
            
            super().__init__(*args, **kwargs)
            interval    = LabeledEntry(self)
            interval.label_text  = 'Interval (ms)'
            interval.entry_text  = str(timer.interval)
            interval.entry_width = 5
            interval.pack(side='top')
            self.interval   = interval
            
            self.active   = IntVar(timer.active)
            Checkbutton(self, text='Activate', variable=self.active, command=self._on_active_button_click).pack(side='top')
            Button(self, text='OK', command=self._on_ok_button_click).pack(side='top')
            
            def hide(): self.visible    = False
            self.protocol('WM_DELETE_WINDOW', hide)

            self.__visible  = True
            self.visible = False
            

        def _on_active_button_click(self):
            self.__timer.active = self.active.get()
            
            
        def _on_ok_button_click(self):
            self.__timer.interval   = self.interval.get_int()
            
         
        @property    
        def visible(self):
            return self.__visible
        
            
        @visible.setter
        def visible(self, val):
            self.__visible  = val
            if val:
                self.update()
                self.deiconify()
            else:
                self.withdraw()
                
            
    
    def __init__(self, widget=None, interval=1000, active=False, counter=-1):
        '''A Tk timer implemented on the after method of Tk widgets.
widget: a Tk widget which provides the after method, if None provided, this object
    will create a ConfigDialog (which is a subclass of Toplevel) and use its after method.
    Default: None.
interval: the interval of the timer. 
    Units: millisecond.
    Default: 1000.
active: the timer will start to work if active==True.
    Default: False.
counter: The maximum number of the trigger, i.e., if counter=3, the timer will
    trigger three times. minus one denotes infinity. 
    Default: -1.
    
TkTimer is based on the Observer protocol. 
'''
        super().__init__()
        self.__interval = interval
        self.__active = active
        self.__counter = counter
        self.__divider_cache = {}        
        
        if widget is None:
            widget  = self.ConfigDialog(timer=self)
        self.__widget   = widget 
        
        
    def show_config_dialog(self, visible=True):
        if not isinstance(self.__widget, self.ConfigDialog):
            raise TypeError('This TkTimer does not have a config dialog.')
        config  = self.__widget
        config.visible  = visible
        
        
    def __timer_callback(self):
        if self.active:
            if self.__counter > 0:
                self.__counter -= 1
            if self.__counter == 0:
                # This is the last time executing the timer function. 
                self.active = False
                
            self.notify_observers()
            # Observer protocol.
            
            self.__widget.after(self.interval, self.__timer_callback)
            # The core of the timer is the after method of Tk widgets. 
        

    @property
    def interval(self):
        '''The interval of the timer.
    Unit: millisecond.'''        
        return self.__interval
    
        
    @interval.setter
    def interval(self, val):
        if isinstance(self.__widget, self.ConfigDialog):
            self.__widget.interval.entry_text    = str(val)
        self.__interval = val
        
    
    @property
    def active(self):
        '''True for activating the timer, and False for deactivating.'''
        return self.__active
    
        
    @active.setter
    def active(self, val):
        lastVal         = self.__active
        self.__active   = val
        if isinstance(self.__widget, self.ConfigDialog):        
            self.__widget.active.set(val)
        if val and not lastVal:
            self.__timer_callback()
            
            
    @property
    def counter(self):
        return self.__counter
    
        
    @counter.setter
    def counter(self, value):
        '''set counter to -1 means infinity timer loop.'''
        self.__counter = value
        
    
    def divider(self, divide_by):
        '''Just like a divider in digital circuits.'''
        if divide_by not in self.__divider_cache:
            self.__divider_cache[divide_by] = Divider(self, divide_by=divide_by)
        return self.__divider_cache[divide_by]
