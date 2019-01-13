(require [wavesynlib.languagecenter.hy.utils [on-exit]])

(import [ctypes [windll byref]])
(import [ctypes.wintypes [DWORD]])
(setv -kernel32 windll.kernel32)
(setv -user32 windll.user32)
(setv ERROR-ALREADY-EXISTS 0xB7)



(defn singleton [unique-id]
    (setv mutex (-kernel32.CreateMutexW None True unique-id) )
    (unless mutex
        (raise (ValueError "Mutex creation failed.") ) )
    (on-exit 
        (when mutex
            (-kernel32.CloseHandle mutex) ) )
    (if (= ERROR-ALREADY-EXISTS (-kernel32.GetLastError) )
        False
    #_else
        True) )



(defn get-pid-from-hwnd [hwnd]
    (setv pid (DWORD))
    (-user32.GetWindowThreadProcessId hwnd (byref pid))
    pid.value)

