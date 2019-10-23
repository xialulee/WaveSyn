(require [wavesynlib.languagecenter.hy.wmidef [wql]])


(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting code-printer]])

(import os)
(import [pathlib [Path]])
(import hy)
(import [wavesynlib.interfaces.os.windows.processes.utils 
    [get-pid-from-hwnd]])



(defclass Utils [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs))

    #@(Scripting.printable
    (defn get-pid-from-hwnd [self pid]
        (get-pid-from-hwnd pid) ) )

    #@(Scripting.printable
    (defn get-prop-from-pid [self prop pid]
        (setv wmi (. self root-node interfaces os windows wmi) ) 
        (setv result (
            .query
                wmi
                (wql 
                    SELECT (eval prop)
                    FROM Win32_Process
                    WHERE (= ProcessId (eval pid) ) ) 
            :output-format "python") ) 
        (. result [0] [prop]) ) )

    #@(Scripting.printable
    (defn get-prop-from-hwnd [self prop hwnd]
        (setv pid (get-pid-from-hwnd hwnd))
        (.get-prop-from-pid self prop pid) ))

    #@(Scripting.printable
    (defn get-prop-from-foreground [self prop]
        (setv hwnd (.foreground self.root-node.interfaces.os.windows.window-handle-getter) ) 
        (.get-prop-from-hwnd self prop hwnd) ))
        
    #@(Scripting.printable
    (defn get-execpath-from-pid [self pid]
"Get the executable path of the process specified by pid.
    pid (int): The PID of the process.
    
Return Value (Path): The path of the executable."
        (.get-prop-from-pid self "ExecutablePath" pid) ))

    #@(Scripting.printable
    (defn get-execpath-from-hwnd [self hwnd]
"Get the executable path of the window specified by hwnd.
    hwnd (int): The handle of the window.
    
Return Value (Path): The path of the executable."
        (.get-prop-from-hwnd self "ExecutablePath", hwnd) ))
        
    #@(Scripting.printable
    (defn get-execpath-from-foreground [self]
"Get the executable path of the foreground window.

Return Value (Path): The path of the executable."
        (.get-prop-from-foreground self "ExecutablePath") )) )


(defclass Processes [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (.--init-- (super) #* args #** kwargs)
        (setv self.utils (
            ModelNode 
                :is-lazy True 
                :class-object Utils))))

