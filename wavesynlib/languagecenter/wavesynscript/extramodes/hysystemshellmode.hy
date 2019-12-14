(require [wavesynlib.languagecenter.hy.utils [call= super-init]])

(import locale)
(setv -encoding (locale.getpreferredencoding) )
(import subprocess)
(import sys)
(import re)

(import [hy.contrib.hy-repr [hy-repr]])

(import [.basemode [ModeInfo BaseMode]])
(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])



(defclass SystemShell [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M!") 
    (setv -PREFIX-ARG-PATTERN (re.compile
r"(?P<exec_mode>[st]*)      # s for storage; t for threading.
(?:\((?P<stdin_var>.*)\))?  # the var name of which the content will be written into stdin."
        re.VERBOSE) )
    
    #@(classmethod
    (defn get-prefix [cls]
        (cls.-MODE-PREFIX) ) ) 
        
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (with [self.attribute-lock]
            (setv self.info (ModeInfo "system_shell" False self) ) ) ) 
            
    (defn --run-process [self code input]
        (setv PIPE subprocess.PIPE) 
        (setv p (subprocess.Popen code :shell True :stdin PIPE :stdout PIPE :stderr PIPE) ) 
        (setv [stdout stderr] (.communicate p :input input) ) 
        (print (.decode stdout -encoding "ignore") ) 
        (print (.decode stderr -encoding "ignore") :file sys.stderr) ) 
        
    (defn test [self code]
        (call= code .strip) 
        (if (and code (.startswith code self.-MODE-PREFIX) ) 
            self.info
        #_else
            False) ) 
            
    (defn run [self code &optional [input None] [store False] [thread False]]
        (comment "To-Do:
                Support store stdout & stderr;
                Support run in thread.") 
        (when (instance? str input) 
            (setv input (.encode input -encoding) ) )
        (.--run-process self code :input input) ) 
        
    (defn translate [self code]
        (comment "To-Do:
                #M!  default;
                #M!s store stdout & stderr;
                #M!t run in thread.") 
        (setv splited (.split code :maxsplit 1) ) 
        (when (< (len splited) 2) 
            (print "\nMode prefix and code should be splited by blank." :file sys.stderr) 
            (return) ) 
        (setv [prefix code] splited)
        (setv prefix-args (cut prefix (len self.-MODE-PREFIX) None) )
        (setv match-obj (re.match self.-PREFIX-ARG-PATTERN prefix-args) )
        (setv stdin-var (get match-obj "stdin_var") )
        (setv py-arg-list [(repr code)])
        (setv hy-arg-list [(hy-repr code)])
        (when stdin-var
            (.append py-arg-list f"input={stdin-var}") 
            (.append hy-arg-list f":input {stdin-var}") )
        (setv py-arg-str (.join ", " py-arg-list) )
        (setv expr-str f"{self.node-path}.run({py-arg-str})")
        (setv display-language self.root-node.lang-center.wavesynscript.display-language) 
        (setv display-str
            (if (= display-language "python") 
                expr-str
            #_else (do
                (setv hy-arg-str (.join " " hy-arg-list) )
                f"(.run {self.hy-node-path} {hy-arg-str})") ) ) 
        (, expr-str display-str) ) )