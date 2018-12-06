# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 12:04:33 2018

@author: Feng-cong Li
"""

import ctypes
from ctypes import byref, sizeof


user32 = ctypes.windll.user32

from wavesynlib.interfaces.os.windows.inputsender.constants import (
    KEYEVENTF_KEYUP, INPUT_KEYBOARD)

# The following code generates the bytecode file of the 
# structdef.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import os
from pathlib import Path
structdef_path = Path(__file__).parent / 'structdef.hy'
os.system(f'hyc {structdef_path}')
# After the bytecode file generated, we can import the module written by hy.
import hy
from wavesynlib.interfaces.os.windows.inputsender.structdef import ( 
    INPUT, KEYBDINPUT)



def send_key_input(code, press=False, release=False):
    def _generate_keybd_event(code, release=False):
        ki_args = {'wVk':code}
        if release:
            ki_args['dwFlags'] = KEYEVENTF_KEYUP
        ki = KEYBDINPUT(**ki_args)
        
        inp = INPUT(
            type=INPUT_KEYBOARD,
            ki=ki)
        user32.SendInput(1, byref(inp), sizeof(inp))    
        
    if press:
        _generate_keybd_event(code)
    elif release:
        _generate_keybd_event(code, release=True)
    else:
        _generate_keybd_event(code)
        _generate_keybd_event(code, release=True)
    

    