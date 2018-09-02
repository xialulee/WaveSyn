# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 12:04:33 2018

@author: Feng-cong Li
"""

import ctypes
from ctypes import byref, sizeof
from ctypes.wintypes import WORD, DWORD, LONG

user32 = ctypes.windll.user32
ULONG_PTR = ctypes.wintypes.WPARAM # See https://stackoverflow.com/a/13615802.

from wavesynlib.languagecenter.utils import ctype_build



@ctype_build('struct')
def MOUSEINPUT(
    dx: LONG,
    dy: LONG,
    mouseData: DWORD,
    dwFlags: DWORD,
    time: DWORD,
    dwExtraInfo: ULONG_PTR
):pass
        
        
        
KEYEVENTF_EXTENDEDKEY	=0x0001
KEYEVENTF_KEYUP	=0x0002
KEYEVENTF_SCANCODE	=0x0008
KEYEVENTF_UNICODE	=0x0004
        
@ctype_build('struct')
def KEYBDINPUT(
    wVk: WORD,
    wScan: WORD,
    dwFlags: DWORD,
    time: DWORD,
    dwExtraInfo: ULONG_PTR
):pass
        
        

    
@ctype_build('struct')
def HARDWAREINPUT(
    uMsg: DWORD,
    wParamL: WORD,
    wParamH: WORD
):pass
        
        
        
@ctype_build('union')
def _DUMMYUNIONNAME(
    mi: MOUSEINPUT,
    ki: KEYBDINPUT,
    hi: HARDWAREINPUT
):pass



INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

@ctype_build('struct', doc='''\
According to Microsoft, INPUT is used by SendInput to store information for 
synthesizing input events such as keystrokes, mouse movement, and mouse clicks.

Fields:
    type: DWORD. The type of the input event.
        0: (INPUT_MOUSE) The event is a mouse event. Corresponding to the mi 
            field.
        1: (INPUT_KEYBOARD) The event is a keyboard event. Corresponding to the
            ki field.
        2: (INPUT_HARDWARE) The event is a hardware event. Corresponding to the 
            hi field.
    mi: MOUSEINPUT. The information about a simulated mouse event.
    ki: KEYBDINPUT. The information about a simulated keyboard event.
    hi: HARDWAREINPUT. The information about a simulated hardware event. 
''')
def INPUT(
    type: DWORD,
    dummy: (_DUMMYUNIONNAME, 'anonymous')
):pass


    
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
    

    