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
    from wavesynlib.interfaces.os.windows.hymemstatus import *
except hy.errors.HyCompileError:
# After the bytecode file generated, we can import the module written by hy.    
    hyfile_path = Path(__file__).parent / 'hymemstatus.hy'
    os.system(f'hyc {hyfile_path}')
    from wavesynlib.interfaces.os.windows.hymemstatus import *



