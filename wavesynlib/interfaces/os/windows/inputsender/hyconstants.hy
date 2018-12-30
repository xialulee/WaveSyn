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
        (.format "VK_F{}" (inc k)) 
        (+ k 0x70) ) )

