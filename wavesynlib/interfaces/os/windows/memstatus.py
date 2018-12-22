# -*- coding: utf-8 -*-
"""
Created on Thur Feb 25 2016

@author: Feng-cong Li
"""
import ctypes as ct
import os
from pathlib import Path
# The following code generates the bytecode file of the 
# memstatus_struct.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import hy
try:
    from wavesynlib.interfaces.os.windows.memstatus_struct import MEMORYSTATUS
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    hyfile_path = Path(__file__).parent / 'memstatus_struct.hy'
    os.system(f'hyc {hyfile_path}')
    from wavesynlib.interfaces.os.windows.memstatus_struct import MEMORYSTATUS


def get_memory_usage():
    memstat = MEMORYSTATUS()
    memstat.dwLength = ct.sizeof(MEMORYSTATUS)    
    ct.windll.kernel32.GlobalMemoryStatus(ct.byref(memstat))
    memusage = memstat.dwMemoryLoad
    return memusage  

