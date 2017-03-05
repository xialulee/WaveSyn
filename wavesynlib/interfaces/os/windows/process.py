# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 21:44:05 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import ctypes as ct
import atexit



ERROR_ALREADY_EXISTS = 0xB7


def singleton(unique):
    mutex = ct.windll.kernel32.CreateMutexW(None, True, unique)
    ret = True
    if mutex:
        if ct.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            ret = False
            
    def on_exit():
        if mutex:
            ct.windll.kernel32.CloseHandle(mutex)
            
    atexit.register(on_exit)
    return ret
    
    
    