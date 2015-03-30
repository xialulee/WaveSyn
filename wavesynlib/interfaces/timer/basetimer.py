# -*- coding: utf-8 -*-
"""
Created on Mon March 30 2015

@author: Feng-cong Li
"""

from wavesynlib.common import Observable
from abc import ABCMeta, abstractproperty

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
    
    @classmethod
    def __subclasshook__(cls, C):
        if cls is BaseObservableTimer:
            if hasattr(C, 'interval') \
                and hasattr(C, 'active') \
                and issubclass(C, Observable):
                    return True
        return NotImplemented
        
