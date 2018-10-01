# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 22:48:35 2018

@author: Feng-cong Li
"""

from ctypes import windll, byref
from ctypes.wintypes import POINT

GetCursorPos = windll.user32.GetCursorPos
GetParent = windll.user32.GetParent
WindowFromPoint = windll.user32.WindowFromPoint
GetForegroundWindow = windll.user32.GetForegroundWindow



def get_foreground():
    return GetForegroundWindow()



def get_hwnd_from_point(x, y, toplevel=True):
    p = POINT(x=x, y=y)
    h1 = WindowFromPoint(p)
    if toplevel:
        while True:
            h2 = GetParent(h1)
            if not h2:
                break
            h1 = h2
    return h1



def get_hwnd_from_cursor_pos(toplevel=True):
    cursor_pos = POINT()
    GetCursorPos(byref(cursor_pos))
    return get_hwnd_from_point(cursor_pos.x, cursor_pos.y, toplevel)