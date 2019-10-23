(require [wavesynlib.languagecenter.hy.utils [
    bit-names dyn-setv]])



(bit-names
    KEYEVENTF_EXTENDEDKEY 
    KEYEVENTF_KEYUP
    KEYEVENTF_UNICODE
    KEYEVENTF_SCANCODE)

(setv INPUT_MOUSE    0
      INPUT_KEYBOARD 1
      INPUT_HARDWARE 2)

(setv VK_CONTROL  0x11)
(setv VK_CTRL     VK_CONTROL)
(setv VK_LCONTROL 0xA2)
(setv VK_LCTRL    VK_LCONTROL)
(setv VK_RCONTROL 0xA3)
(setv VK_RCTRL    VK_RCONTROL)

(setv VK_MENU  0x12)
(setv VK_ALT   VK_MENU)
(setv VK_LMENU 0xA4)
(setv VK_LALT  VK_LMENU)
(setv VK_RMENU 0xA5)
(setv VK_RALT  VK_RMENU)

(setv VK_SHIFT  0x10)
(setv VK_LSHIFT 0xA0)
(setv VK_RSHIFT 0xA1)


(for [k (range 24)]
    (dyn-setv 
        f"VK_F{(inc k)}"
        (+ k 0x70) ) )

(setv MOUSEEVENTF_ABSOLUTE        0x8000)
(setv MOUSEEVENTF_HWHEEL          0x1000)
(setv MOUSEEVENTF_MOVE            0x0001)
(setv MOUSEEVENTF_MOVE_NOCOALESCE 0x2000)
(setv MOUSEEVENTF_LEFTDOWN        0x0002)
(setv MOUSEEVENTF_LEFTUP          0x0004)
(setv MOUSEEVENTF_RIGHTDOWN       0x0008)
(setv MOUSEEVENTF_RIGHTUP         0x0010)
(setv MOUSEEVENTF_MIDDLEDOWN      0x0020)
(setv MOUSEEVENTF_MIDDLEUP        0x0040)
(setv MOUSEEVENTF_VIRTUALDESK     0x4000)
(setv MOUSEEVENTF_WHEEL           0x0800)
(setv MOUSEEVENTF_XDOWN           0x0080)
(setv MOUSEEVENTF_XUP             0x0100)

(bit-names 
    XBUTTON1
    XBUTTON2)
