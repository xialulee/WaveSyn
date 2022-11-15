from ctypes import byref
from ctypes.wintypes import POINT
from ctypes import windll  

GetCursorPos = windll.user32.GetCursorPos
GetParent = windll.user32.GetParent
WindowFromPoint = windll.user32.WindowFromPoint
GetForegroundWindow = windll.user32.GetForegroundWindow


def get_foreground():
    return GetForegroundWindow()


def get_toplevel(child):
    while True:
        parent = GetParent(child)
        if not parent:
            return child
        else:
            child = parent


def get_hwnd_from_point(x, y, toplevel=True):
    p = POINT(x=x, y=y)
    h = WindowFromPoint(p)
    return get_toplevel(h) if toplevel else h


def get_hwnd_from_cursor_pos(toplevel=True):
    cursor_pos = POINT()
    GetCursorPos(byref(cursor_pos))
    return get_hwnd_from_point(cursor_pos.x, cursor_pos.y, toplevel)
