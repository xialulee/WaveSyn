# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 10:14:20 2015

@author: Administrator
"""
from Tkinter import * 
from wavesynlib.interfaces.timer.basetimer import BaseObservableTimer
from wavesynlib.guicomponents import ParamItem


class TkTimer(BaseObservableTimer):    
    class ConfigDialog(Toplevel, object):                 
        def __init__(self, *args, **kwargs):
            timer       = kwargs.pop('timer')
            self.__timer    = timer
            
            Toplevel.__init__(self, *args, **kwargs)
            interval    = ParamItem(self)
            interval.labelText  = 'Interval (ms)'
            interval.entryText  = str(timer.interval)
            interval.entryWidth = 5
            interval.pack(side=TOP)
            self.interval   = interval
            
            self.active   = IntVar(timer.active)
            Checkbutton(self, text='Activate', variable=self.active, command=self.onActivateClick).pack(side=TOP)
            Button(self, text='OK', command=self.onOKClick).pack(side=TOP)
            
            def hide(): self.visible    = False
            self.protocol('WM_DELETE_WINDOW', hide)

            self.__visible  = True
            self.visible = False

        def onActivateClick(self):
            self.__timer.active = self.active.get()
            
        def onOKClick(self):
            self.__timer.interval   = self.interval.getInt()
         
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
            
    
    def __init__(self, widget=None, interval=1000, active=False):
        super(TkTimer, self).__init__()
        self.__interval   = interval
        self.__active   = active
        if widget is None:
            widget  = self.ConfigDialog(timer=self)
        self.__widget   = widget        
        
    def showConfigDialog(self, visible=True):
        if not isinstance(self.__widget, self.ConfigDialog):
            raise TypeError('This TkTimer does not have a config dialog.')
        config  = self.__widget
        config.visible  = visible
        
        
    def __timerFunc(self):
        if self.active:
            self.notifyObservers()
            self.__widget.after(self.interval, self.__timerFunc)
        

    @property
    def interval(self):
        return self.__interval
        
    @interval.setter
    def interval(self, val):
        if isinstance(self.__widget, self.ConfigDialog):
            self.__widget.interval.entryText    = str(val)
        self.__interval = val
    
    @property
    def active(self):
        return self.__active
        
    @active.setter
    def active(self, val):
        lastVal         = self.__active
        self.__active   = val
        if isinstance(self.__widget, self.ConfigDialog):        
            self.__widget.active.set(val)
        if val and not lastVal:
            self.__timerFunc()
    
    
