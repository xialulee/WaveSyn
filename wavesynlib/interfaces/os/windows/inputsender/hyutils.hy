(import ctypes)
(import [ctypes [byref sizeof]])

(setv user32 ctypes.windll.user32)

(import [wavesynlib.interfaces.os.windows.inputsender.constants [
    KEYEVENTF_KEYUP INPUT_KEYBOARD]])
(import [wavesynlib.interfaces.os.windows.inputsender.structdef [
    INPUT KEYBDINPUT]])



(defn send-key-input [code &optional press release]
    (defn generate-keybd-event [code &optional release]
        (setv ki-args {"wVk" code})
        (when release
            (assoc ki-args "dwFlags" KEYEVENTF_KEYUP))
        (setv ki (KEYBDINPUT #** ki-args))
        (setv inp (INPUT
            :type INPUT_KEYBOARD
            :ki ki))
        (user32.SendInput 1 (byref inp) (sizeof inp)))
        
    (cond
    [press 
        (generate-keybd-event code)]
    [release 
        (generate-keybd-event code :release True)]
    [True
        (generate-keybd-event code)
        (generate-keybd-event code :release True)]))

