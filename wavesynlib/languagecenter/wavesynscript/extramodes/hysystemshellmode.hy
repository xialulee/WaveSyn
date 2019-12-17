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
    ModelNode Scripting WaveSynScriptAPI ScriptCode code-printer]])



(defn -get-leading-blanks [s]
    (setv t (.lstrip s) ) 
    (setv d (- (len s) (len t) ) ) 
    (cut s 0 d) )



(defclass SystemShell [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M!") 
    (setv -PREFIX-ARG-PATTERN (re.compile
r"(?P<exec_mode>[stnf]*)      
# s for storage; 
# t for threading; 
# n for not displaying;
# f for using f-str as command.
(?:\((?P<stdin_var>.*)\))?  
# the var name of which the content will be written into stdin."
        re.VERBOSE) )
    
    #@(classmethod
    (defn get-prefix [cls]
        cls.-MODE-PREFIX ) ) 
        
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
        (if (.startswith (.lstrip code) self.-MODE-PREFIX) 
            self.info
        #_else
            False) ) 
            
    #@(WaveSynScriptAPI 
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
        (setv [prefix-args code] (.-split-code self code) )
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
        (when (in "f" exec-mode) 
            (assoc arg-dict "command" (ScriptCode (+ "f" (repr code) ) ) ) )
        arg-dict) 

    (defn translate [self code &optional verbose]
        (setv leading-blanks (-get-leading-blanks code) )
        (call= code .lstrip)
        (setv arg-dict (.-arg-parse self code) ) 
        (setv arg-str    (Scripting.convert-args-to-str #** arg-dict) )
        (setv hy-arg-str (Scripting.hy-convert-args-to-str #** arg-dict) )
        (setv result (,
            f"{leading-blanks}{self.node-path}.run({arg-str})" 
            f"{leading-blanks}(.run {self.hy-node-path} {hy-arg-str})") ) 
        (when verbose
            (setv write self.root-node.stream-manager.write) 
            (setv lang-index 
                (if (= self.root-node.lang-center.wavesynscript.display-language "python") 
                    0
                #_else
                    1) )
            (write "The translated code is given as follows:\n" "TIP")
            (write f"{(get result lang-index)}\n" "HISTORY")
            (when (.get arg-dict "store" "")
                (write f"'store=True' indicating that the contents of stdout & stderr are stored in
{self.node-path}.result\n" "TIP") ) )
        result)

    (defn execute [self code]
        (call= code .lstrip)
        (try 
            (setv arg-dict (.-arg-parse self code) ) 
        (except [err SyntaxError]
            (print) 
            (print err :file sys.stderr) 
            (return) ) )
        (with [(code-printer True)]
            (.run self #** arg-dict) ) ) ) 
