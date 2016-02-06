# -*- coding: utf-8 -*-
"""
Created on Mon March 30 2015

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from abc import ABCMeta, abstractproperty, abstractmethod

class BaseObservableTimer(Observable):
    __metaclass__ = ABCMeta
    
    def interval_getter(self):
        raise NotImplementedError
        
    def interval_setter(self, val):
        raise NotImplementedError
        
    interval = abstractproperty(interval_getter, interval_setter)
    
    def active_getter(self):
        raise NotImplementedError
        
    def active_setter(self, val):
        raise NotImplementedError
        
    active = abstractproperty(active_getter, active_setter)
    
    def counter_getter(self):
        raise NotImplementedError
        
    def counter_setter(self):
        raise NotImplementedError
        
    counter = abstractproperty(counter_getter, counter_setter)
    
    @abstractmethod
    def divider(self, divide_by):
        raise NotImplementedError
    
    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseObservableTimer:
            if hasattr(C, 'interval') \
                and hasattr(C, 'active') \
                and hasattr(C, 'counter') \
                and issubclass(C, Observable):
                    return True
        return NotImplemented
        

class Divider(Observable):
    def __init__(self, timer, divide_by):
        Observable.__init__(self)
        self.__counter = 0
        
        @SimpleObserver
        def on_timer():
            self.__counter += 1
            if self.__counter == divide_by:
                self.notify_observers()
                self.__counter = 0
                
        timer.add_observer(on_timer)