# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 12:50:36 2016

@author: Feng-cong Li
"""
import _thread as thread

from wavesynlib.languagecenter.datatypes import Event
from wavesynlib.languagecenter.designpatterns import Observable


_lock = thread.allocate_lock()

_status = {'busy':False}


def is_busy():
    with _lock:
        return _status['busy']
        

class _BusyContext(Observable):
    def __init__(self):
        super().__init__()
        self.__busy = Event(sender=self, name="busy")
        self.__available = Event(sender=self, name="available")
    
    def __enter__(self):
        with _lock:
            _status['busy'] = True
            self.notify_observers(self.__busy)
            
    def __exit__(self, *args):
        with _lock:
            _status['busy'] = False
            self.notify_observers(self.__available)
            
            
busy_doing = _BusyContext()