(require [wavesynlib.languagecenter.hy.cdef [→]])
(require [wavesynlib.languagecenter.hy.win32def [import-func]])
(require [wavesynlib.languagecenter.hy.utils [on-exit]])

(import [ctypes [windll byref]])
(import [ctypes.wintypes [DWORD]])
(import-func user32 GetWindowThreadProcessId)
(import-func kernel32
    CreateMutexW
    CloseHandle
    GetLastError)
(setv ERROR-ALREADY-EXISTS 0xB7)



(defn singleton [unique-id]
    (setv mutex (CreateMutexW None True unique-id) )
    (unless mutex
        (raise (ValueError "Mutex creation failed.") ) )
    (on-exit 
        (when mutex
            (CloseHandle mutex) ) )
    (if (= ERROR-ALREADY-EXISTS (GetLastError) )
        False
    #_else
        True) )



(defn get-pid-from-hwnd [hwnd]
    (setv pid (DWORD))
    (GetWindowThreadProcessId hwnd #→ pid)
    pid.value)

