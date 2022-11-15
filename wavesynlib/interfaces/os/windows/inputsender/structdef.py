# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 22:39:13 2018

@author: Feng-cong Li
"""
from ctypes import Structure, Union
from ctypes.wintypes import WORD, DWORD, LONG, WPARAM

# See https://stackoverflow.com/a/13615802.
ULONG_PTR = WPARAM


class MOUSEINPUT(Structure):
    _fields_ = [
        ('dx', LONG), 
        ('dy', LONG), 
        ('mouseData', DWORD), 
        ('dwFlags', DWORD), 
        ('time', DWORD), 
        ('dwExtraInfo', ULONG_PTR)
    ]


class KEYBDINPUT(Structure):
    _fields_ = [
        ('wVk', WORD), 
        ('wScan', WORD), 
        ('dwFlags', DWORD), 
        ('time', DWORD), 
        ('dwExtraInfo', ULONG_PTR)
    ]


class HARDWAREINPUT(Structure):
    _fields_ = [
        ('uMsg', DWORD), 
        ('wParamL', WORD), 
        ('wParamH', WORD)
    ]


class _DUMMYUNIONNAME(Union):
    _fields_ = [
        ('mi', MOUSEINPUT), 
        ('ki', KEYBDINPUT), 
        ('hi', HARDWAREINPUT)
    ]


# According to Microsoft, INPUT is used by SendInput to store information for 
# synthesizing input events such as keystrokes, mouse movement, and mouse clicks.
# 
# Fields:
#     type: DWORD. The type of the input event.
#         0: (INPUT_MOUSE) The event is a mouse event. Corresponding to the mi 
#             field.
#         1: (INPUT_KEYBOARD) The event is a keyboard event. Corresponding to the
#             ki field.
#         2: (INPUT_HARDWARE) The event is a hardware event. Corresponding to the 
#             hi field.
#     mi: MOUSEINPUT. The information about a simulated mouse event.
#     ki: KEYBDINPUT. The information about a simulated keyboard event.
#     hi: HARDWAREINPUT. The information about a simulated hardware event. 
class INPUT(Structure):
    _anonymous_ = 'dummy',
    _fields_ = [
        ('type', DWORD), 
        ('dummy', _DUMMYUNIONNAME)
    ]
