(require [wavesynlib.languagecenter.hy.utils [
    call= super-init defprop]])

(import locale)
(setv -encoding (locale.getpreferredencoding) )
(import subprocess)
(import sys)
(import re)

(import [hy.contrib.hy-repr [hy-repr]])

(import [.basemode [ModeInfo BaseMode]])
(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting ScriptCode code-printer]])



(defclass SystemShell [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M!") 
    (setv -PREFIX-ARG-PATTERN (re.compile
r"(?P<exec_mode>[stn]*)      # s for storage; t for threading; n for not displaying.
(?:\((?P<stdin_var>.*)\))?  # the var name of which the content will be written into stdin."
        re.VERBOSE) )
    
    #@(classmethod
    (defn get-prefix [cls]
        (cls.-MODE-PREFIX) ) ) 
        
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (with [self.attribute-lock]
            (setv self.info (ModeInfo "system_shell" False self) ) 
            (setv self.result {"stdout" "" "stderr" ""}) ) ) 
            
    (defn --run-process [self command input]
        (setv PIPE subprocess.PIPE) 
        (setv p (subprocess.Popen command :shell True :stdin PIPE :stdout PIPE :stderr PIPE) ) 
        (setv [stdout stderr] (.communicate p :input input) ) 
        (, 
            (.decode stdout -encoding "ignore") 
            (.decode stderr -encoding "ignore") ) ) 
        
    (defn test [self code]
        (if (and code (.startswith code self.-MODE-PREFIX) ) 
            self.info
        #_else
            False) ) 
            
    #@(Scripting.printable 
    (defn run [self command &optional [display True] [input None] [store False] [thread False]]
        (comment "To-Do:
                Support store stdout & stderr;
                Support run in thread.") 
        (assoc self.result "stdout" "")
        (assoc self.result "stderr" "")
        (when (instance? str input) 
            (setv input (.encode input -encoding) ) )
        (setv [stdout stderr] (.--run-process self command :input input) ) 
        (when store
            (assoc self.result "stdout" stdout) 
            (assoc self.result "stderr" stderr) )
        (when display
            (print stdout) 
            (print stderr :file sys.stderr) ) ) )
        
    (defn -arg-parse [self code]
        (comment "To-Do:
                #M!  default;
                #M!s store stdout & stderr;
                #M!t run in thread.") 
        (setv splited (.split code :maxsplit 1) ) 
        (when (< (len splited) 2) 
            (raise (SyntaxError "Mode prefix and code should be splited by blank.") ) ) 
        (setv [prefix code] splited)
        (setv prefix-args (cut prefix (len self.-MODE-PREFIX) None) )
        (setv match-obj (re.match self.-PREFIX-ARG-PATTERN prefix-args) )
        (setv stdin-var (get match-obj "stdin_var") )
        (setv exec-mode (get match-obj "exec_mode") )
        (setv arg-dict {"command" code}) 
        (when stdin-var
            (assoc arg-dict "input" (ScriptCode stdin-var) ) ) 
        (when (in "s" exec-mode) 
            (assoc arg-dict "store" True) )
        (when (in "n" exec-mode) 
            (assoc arg-dict "display" False) )
        arg-dict) 

    (defn translate [self code]
        (setv arg-dict (.-arg-parse self code) ) 
        (setv arg-str (Scripting.convert-args-to-str #** arg-dict) )
        f"{self.node-path}.run({arg-str})")

    (defn translate-and-run [self code]
        (try 
            (setv arg-dict (.-arg-parse self code) ) 
        (except [err SyntaxError]
            (print) 
            (print err :file sys.stderr) 
            (return) ) )
        (with [(code-printer True)]
            (.run self #** arg-dict) ) ) ) 
