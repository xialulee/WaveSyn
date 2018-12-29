(require [wavesynlib.languagecenter.hy.wmidef [wql]])

(import ctypes)

(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])

(import os)
(import [pathlib [Path]])
(import hy)
(import [wavesynlib.interfaces.os.windows.processes.utils 
    [get-pid-from-hwnd]])



(defclass Utils [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs))
        
    (defn get-execpath-from-pid [self pid]
        (setv wmi (. self root-node interfaces os windows wmi))
        (setv result (.query 
            wmi 
            (wql 
                SELECT ExecutablePath 
                FROM Win32_Process 
                WHERE (= ProcessId (eval pid))) 
            "python"))
        (. result [0] ["ExecutablePath"]))
        
    (defn get-execpath-from-hwnd [self hwnd]
        (setv pid (get-pid-from-hwnd hwnd))
        (.get-execpath-from-pid self pid)))



(defclass Processes [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs)
        (setv self.utils (ModelNode :is-lazy True :class-object Utils))))

