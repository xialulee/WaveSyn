(require [wavesynlib.languagecenter.hy.wmidef [wql]])

(import ctypes)

(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting]])

(import os)
(import [pathlib [Path]])
(import hy)
(import [wavesynlib.interfaces.os.windows.processes.utils 
    [get-pid-from-hwnd]])



(defclass Utils [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs))
        
    #@(Scripting.printable
    (defn get-execpath-from-pid [self pid]
"Get the executable path of the process specified by pid.
    pid (int): The PID of the process.
    
Return Value (str): The path of the executable."
        (setv wmi (. self root-node interfaces os windows wmi))
        (setv result (
            .query 
                wmi 
                (wql 
                    SELECT ExecutablePath 
                    FROM Win32_Process 
                    WHERE (= ProcessId (eval pid))) 
                :output-format "python"))
        (. result [0] ["ExecutablePath"])))
        
    #@(Scripting.printable
    (defn get-execpath-from-hwnd [self hwnd]
"Get the executable path of the window specified by hwnd.
    hwnd (int): The handle of the window.
    
Return Value (str): The path of the executable."
        (setv pid (get-pid-from-hwnd hwnd))
        (.get-execpath-from-pid self pid))))



(defclass Processes [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs)
        (setv self.utils (
            ModelNode 
                :is-lazy True 
                :class-object Utils))))

