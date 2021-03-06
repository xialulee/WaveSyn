(require [wavesynlib.languagecenter.hy.utils [super-init]])
(require [wavesynlib.languagecenter.hy.wmidef [wql]])
(require [wavesynlib.languagecenter.wavesynscript.macros [
    init-wavesynscript-macros
    BindLazyNode]])
(init-wavesynscript-macros)

(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting WaveSynScriptAPI code-printer]])

(import os)
(import [pathlib [Path]])
(import hy)
(import [wavesynlib.interfaces.os.windows.processes.utils 
    [get-pid-from-hwnd run-as-admin]])



(defclass Utils [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs))

    #@(WaveSynScriptAPI
    (defn run-as-admin [self executable parameters]
        (run-as-admin executable parameters) ) )

    #@(WaveSynScriptAPI
    (defn get-pid-from-hwnd [self pid]
        (get-pid-from-hwnd pid) ) )

    #@(WaveSynScriptAPI
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

    #@(WaveSynScriptAPI
    (defn get-prop-from-hwnd [self prop hwnd]
        (setv pid (get-pid-from-hwnd hwnd))
        (.get-prop-from-pid self prop pid) ))

    #@(WaveSynScriptAPI
    (defn get-prop-from-foreground [self prop]
        (setv hwnd (.foreground self.root-node.interfaces.os.windows.window-handle-getter) ) 
        (.get-prop-from-hwnd self prop hwnd) ))
        
    #@(WaveSynScriptAPI
    (defn get-execpath-from-pid [self pid]
"Get the executable path of the process specified by pid.
    pid (int): The PID of the process.
    
Return Value (Path): The path of the executable."
        (.get-prop-from-pid self "ExecutablePath" pid) ))

    #@(WaveSynScriptAPI
    (defn get-execpath-from-hwnd [self hwnd]
"Get the executable path of the window specified by hwnd.
    hwnd (int): The handle of the window.
    
Return Value (Path): The path of the executable."
        (.get-prop-from-hwnd self "ExecutablePath", hwnd) ))
        
    #@(WaveSynScriptAPI
    (defn get-execpath-from-foreground [self]
"Get the executable path of the foreground window.

Return Value (Path): The path of the executable."
        (.get-prop-from-foreground self "ExecutablePath") )) )


(defclass Processes [ModelNode]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (BindLazyNode 
            self.utils Utils) ) )

