# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 21:44:05 2017

@author: Feng-cong Li
"""

#from __future__ import print_function, division, unicode_literals
#
#import ctypes as ct
#import atexit
#
#
#
#ERROR_ALREADY_EXISTS = 0xB7
#
#
#def singleton(unique):
#    mutex = ct.windll.kernel32.CreateMutexW(None, True, unique)
#    ret = True
#    if mutex:
#        if ct.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
#            ret = False
#            
#    def on_exit():
#        if mutex:
#            ct.windll.kernel32.CloseHandle(mutex)
#            
#    atexit.register(on_exit)
#    return ret
    
    
import os
from pathlib import Path
import hy
try:
    from wavesynlib.interfaces.os.windows.process.hyutils \
        import singleton
except hy.errors.HyCompileError:
    hy_path = Path(__file__).parent / 'hyutils.hy'
    os.system(f'hyc {hy_path}')
    from wavesynlib.interfaces.os.windows.process.hyutils \
        import singleton   
