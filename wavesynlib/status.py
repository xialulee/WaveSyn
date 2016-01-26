# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 12:50:36 2016

@author: Feng-cong Li
"""

from __future__ import print_function, unicode_literals, division

import thread

from wavesynlib.languagecenter.designpatterns import Observable


_lock = thread.allocate_lock()

_status = {'busy':False}


def is_busy():
    with _lock:
        return _status['busy']
        

class _BusyContext(Observable):
    def __init__(self):
        Observable.__init__(self)
    
    def __enter__(self):
        with _lock:
            _status['busy'] = True
            self.notify_observers(True)
            
    def __exit__(self, *args):
        with _lock:
            _status['busy'] = False
            self.notify_observers(False)
            
            
busy_doing = _BusyContext()