(require [wavesynlib.languagecenter.hy.cdef [init-cdef →]])
(init-cdef)
(require [wavesynlib.languagecenter.hy.win32def [import-func]])

(import ctypes)
(import [ctypes [byref sizeof]])

(import-func user32 SendInput)

(import [wavesynlib.interfaces.os.windows.inputsender.constants [*]])
(import [wavesynlib.interfaces.os.windows.inputsender.structdef [
    INPUT KEYBDINPUT MOUSEINPUT]])



(defn send-key-input ^int [^int code &optional ^bool press ^bool release]
"Generate a synthesized keystroke.

Parameters:
    [int] code: The key code. The module win32con provides the corresponing constants start with VK_.
    Optional:
    [bool] press: Generate a KEYEVENTF_KEYDOWN event.
    [bool] release: Generate a KEYEVENTF_KEYUP event.
    
Return value:
    [int] 0 if failed, the number of the event if success. (See SendInput for more information)"

    (defn generate-keybd-event [code &optional release]
        (setv ki-args {"wVk" code})
        (when release
            (assoc ki-args "dwFlags" KEYEVENTF_KEYUP))
        (setv ki (KEYBDINPUT #** ki-args))
        (setv inp (INPUT
            :type INPUT_KEYBOARD
            :ki ki))
        (SendInput 1 #→[inp] (sizeof inp)))
        
    (cond
    [press 
        (generate-keybd-event code)]
    [release 
        (generate-keybd-event code :release True)]
    [True
        (generate-keybd-event code)
        (generate-keybd-event code :release True)]))



(defn send-mouse-input [
        ^int dx ^int dy  
        &optional 
        ^str [button ""]
        ^bool absolute ^bool press ^bool release 
        ^bool wheel ^int wheel-data ^int [time 0]]
"Generate a synthesized mouse event. 

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
    [int] 0 if failed, the number of the event if success. (See SendInput for more information)"

    (setv mi-args {"dx" dx "dy" dy})
    (setv dw-flags 0)
    (when absolute
        (|= dw-flags MOUSEEVENTF_ABSOLUTE) ) 
    (setv button (.upper button)) 

    (setv consts (globals))

    (defn generate-mouse-button [dx dy button absolute &optional release]
        (setv mi-args {"dx" dx "dy" dy}) 
        (setv flags 0)
        (if absolute (|= flags (| MOUSEEVENTF_ABSOLUTE MOUSEEVENTF_MOVE)))
        (setv event-name "MOUSEEVENTF_")
        (+= event-name button) 
        (+= event-name (if release "UP" "DOWN") ) 
        (|= flags (.get consts event-name) ) 
        (assoc mi-args "dwFlags" flags) 
        (setv mi (MOUSEINPUT #** mi-args)) 
        (setv inp (INPUT
            :type INPUT_MOUSE
            :mi mi) ) 
        (SendInput 1 #→[inp] (sizeof inp)) )

    (defn generate-mouse-wheel [wheel-data &optional time]
        (setv mi (MOUSEINPUT))
        (setv 
            mi.mouseData   wheel-data
            mi.dwFlags     MOUSEEVENTF_WHEEL
            mi.time        time
            mi.dwExtraInfo 0)
        (setv inp (INPUT
            :type INPUT_MOUSE
            :mi mi))
        (SendInput 1 #→[inp] (sizeof inp)))

    (cond 
    [press (generate-mouse-button dx dy button absolute)]
    [release (generate-mouse-button dx dy button absolute :release True)]
    [wheel (generate-mouse-wheel wheel-data time)]
    [True
        (generate-mouse-button dx dy button absolute)
        (generate-mouse-button dx dy button absolute :release True)]) )

