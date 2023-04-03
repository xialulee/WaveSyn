from ctypes import windll, byref, sizeof

from .constants import *
from .structdef import INPUT, KEYBDINPUT, MOUSEINPUT

SendInput = windll.user32.SendInput



def send_key_input(code: int, press: bool=None, release: bool=None) -> int:
    """Generate a synthesized keystroke.

Parameters:
    [int] code: The key code. The module win32con provides the corresponing constants start with VK_.
    Optional:
    [bool] press: Generate a KEYEVENTF_KEYDOWN event.
    [bool] release: Generate a KEYEVENTF_KEYUP event.

Return value:
    [int] 0 if failed, the number of the event if success. (See SendInput for more information)"""

    def generate_keybd_event(code, release=None):
        dwFlags = 0
        if code in (VK_LEFT, VK_RIGHT, VK_DOWN, VK_UP, VK_HOME, VK_END):
            dwFlags |= KEYEVENTF_EXTENDEDKEY
        ki_args = {'wVk': code}
        if release:
            dwFlags |= KEYEVENTF_KEYUP
        ki_args['dwFlags'] = dwFlags
        ki = KEYBDINPUT(**ki_args)
        inp = INPUT(type=INPUT_KEYBOARD, ki=ki)
        SendInput(1, byref(inp), sizeof(inp))

    if press:
        generate_keybd_event(code)
    elif release:
        generate_keybd_event(code, release=True)
    else:
        generate_keybd_event(code)
        generate_keybd_event(code, release=True)
        

def send_mouse_input(
        dx: int, dy: int, 
        button: str='', 
        absolute: bool = None,
        press: bool = None, release: bool = None, 
        wheel: bool = None, wheel_data: int = None, 
        time: int = 0):
    """\
Generate a synthesized mouse event.

Parameters:
    [int] dx, dy: a given absolute/relative coordinate for mouse pointer.
    Optional:
    [str] button: The name of the mouse button. Valid names include: left, middle and right.
    [bool] absolute: The new mouse pointer coordinate is (dx+x, dy+y) where (x, y) is the current mouse position if true, else (dx+0, dy+0)
    [bool] press: Generate a MOUSEEVENTF_{button}DOWN event.
    [bool] release: Generate a MOUSEEVENTF_{button}UP event.
    [bool] wheel: Generate a MOUSEEVENTF_WHEEL event.
    [int] wheel_data: The amount of wheel movement. See MOUSEINPUT (winuser.h) for more information.
    [int] time: The time stamp for the event, in milliseconds. If it is 0, the system will provide its own time stamp.

Return value:
    [int] 0 if failed, the number of the event if success. (See SendInput for more information)"""
    # mi_args = {'dx': dx, 'dy': dy}
    dw_flags = 0
    if absolute:
        dw_flags |= MOUSEEVENTF_ABSOLUTE
    button = button.upper()
    consts = globals()

    def generate_mouse_button(dx, dy, button, absolute, release = None):
        mi_args = {'dx': dx, 'dy': dy}
        flags = 0
        if absolute:
            flags |= MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
        event_name = 'MOUSEEVENTF_'
        event_name += button
        event_name += 'UP' if release else 'DOWN'
        flags |= consts.get(event_name)
        mi_args['dwFlags'] = flags
        mi = MOUSEINPUT(**mi_args)
        inp = INPUT(type=INPUT_MOUSE, mi=mi)
        return SendInput(1, byref(inp), sizeof(inp))

    def generate_mouse_wheel(wheel_data, time = None):
        mi = MOUSEINPUT()
        mi.mouseData = wheel_data
        mi.dwFlags = MOUSEEVENTF_WHEEL
        mi.time = time
        mi.dwExtraInfo = 0
        inp = INPUT(type=INPUT_MOUSE, mi=mi)
        SendInput(1, byref(inp), sizeof(inp))

    if press:
        generate_mouse_button(dx, dy, button, absolute)
    elif release:
        generate_mouse_button(dx, dy, button, absolute, release=True)
    elif wheel:
        generate_mouse_wheel(wheel_data, time)
    else:
        generate_mouse_button(dx, dy, button, absolute)
        generate_mouse_button(dx, dy, button, absolute, release=True)
