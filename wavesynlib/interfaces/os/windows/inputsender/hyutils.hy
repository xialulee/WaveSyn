(require [wavesynlib.languagecenter.hy.cdef [init-cdef →]])
(init-cdef)
(require [wavesynlib.languagecenter.hy.win32def [import-func]])

(import ctypes)
(import [ctypes [byref sizeof]])

(import-func user32 SendInput)

(import [wavesynlib.interfaces.os.windows.inputsender.constants [*]])
(import [wavesynlib.interfaces.os.windows.inputsender.structdef [
    INPUT KEYBDINPUT MOUSEINPUT]])



(defn send-key-input [code &optional press release]
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



(defn send-mouse-input [dx dy button &optional absolute press release]
    (setv mi-args {"dx" dx "dy" dy})
    (setv dw-flags 0)
    (when absolute
        (|= dw-flags MOUSEEVENTF_ABSOLUTE) ) 
    (setv button (.upper button)) 

    (setv consts (globals))

    (defn generate-mouse-event [dx dy button absolute &optional release]
        (setv mi-args {"dx" dx "dy" dy}) 
        (setv flags 0)
        (if absolute (|= flags MOUSEEVENTF_ABSOLUTE))
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

    (cond 
    [press (generate-mouse-event dx dy button absolute)]
    [release (generate-mouse-event dx dy button absolute :release True)]
    [True
        (generate-mouse-event dx dy button absolute)
        (generate-mouse-event dx dy button absolute :release True)]) )

