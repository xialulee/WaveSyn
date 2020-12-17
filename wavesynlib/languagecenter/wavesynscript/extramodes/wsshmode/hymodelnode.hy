(require [wavesynlib.languagecenter.hy.utils [
    call= super-init defprop]])

(import locale)
(setv -encoding (locale.getpreferredencoding) )
(import subprocess)
(import sys)
(import re)
(import io)

(import [hy.contrib.hy-repr [hy-repr]])

(import [..basemode [ModeInfo BaseMode]])
(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting WaveSynScriptAPI ScriptCode code-printer]])

(import [.execute [run]])



(defn -get-leading-blanks [s]
    (setv t (.lstrip s) ) 
    (setv d (- (len s) (len t) ) ) 
    (cut s 0 d) )



(defclass WSSh [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M!") 
    (setv -PREFIX-ARG-PATTERN (re.compile
r"(?P<exec_mode>[stnf]*)      
# s for storage; 
# t for threading; 
# n for not displaying;
# f for using f-str as command.
(?:\[(?P<shell>.*)\])?
# Shell selection.
# Default shell will be used if not specified.
# [uow]: Select Ubuntu-on-Windows bash as shell.
(?:\((?P<stdin_var>.*)\))?  
# the var name of which the content will be written into stdin.
(?:\|(?P<return_var>\w+)=)?
# the var name of the run's (or run.new_thread_run's) return value."
        re.VERBOSE) )
    
    #@(classmethod
    (defn get-prefix [cls]
        cls.-MODE-PREFIX ) ) 
        
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (with [self.attribute-lock]
            (setv self.info (ModeInfo "wssh" False self) ) 
            (setv self.result {"stdout" "" "stderr" ""}) ) ) 
            
    (defn --run-process [self command input]
        ;(setv PIPE subprocess.PIPE) 
        ;(setv p (subprocess.Popen command :shell True :stdin PIPE :stdout PIPE :stderr PIPE) ) 
        ;(setv [stdout stderr] (.communicate p :input input) ) 
        ;(, 
            ;(.decode stdout -encoding "ignore") 
            ;(.decode stderr -encoding "ignore") ) 
        (setv 
            stdout (io.StringIO)
            stderr (io.StringIO))
        (setv returncode (run command :stdout stdout :stderr stderr) )
        (.seek stdout 0) 
        (.seek stderr 0)
        (, returncode (.read stdout) (.read stderr) ) )
        
    (defn test [self code]
        (if (.startswith (.lstrip code) self.-MODE-PREFIX) 
            self.info
        #_else
            False) ) 
            
    #@((WaveSynScriptAPI :thread-safe True)
    (defn run [self command &optional [display True] [input None] [store False]]
        (comment "To-Do:
                Support store stdout & stderr;
                Support run in thread.") 
        (setv result {
            "returncode" None 
            "stdout"     None 
            "stderr"     None})
        (assoc self.result "stdout" "")
        (assoc self.result "stderr" "")
        (when (instance? str input) 
            (setv input (.encode input -encoding) ) )
        (setv [returncode stdout stderr] (.--run-process self command :input input) ) 
        (assoc result "returncode" returncode)
        (when store
            (assoc result "stdout" stdout) 
            (assoc result "stderr" stderr) )
        (when display
            (print stdout) 
            (print stderr :file sys.stderr) ) 
        result ) )
        
    (defn -arg-parse [self code]
        (comment "To-Do:
                #M!  default;") 
        (setv [prefix-args code] (.-split-code self code) )
        (setv match-obj (re.match self.-PREFIX-ARG-PATTERN prefix-args) )
        (setv stdin-var  (get match-obj "stdin_var") )
        (setv exec-mode  (get match-obj "exec_mode") )
        (setv shell-name (get match-obj "shell"))
        (setv retvar     (get match-obj "return_var"))
        (setv arg-dict {"command" code}) 
        (when stdin-var
            (assoc arg-dict "input" (ScriptCode stdin-var) ) ) 
        (when (in "s" exec-mode) 
            (assoc arg-dict "store" True) )
        (when (in "t" exec-mode) 
            (comment 
                However, "thread" is not an argument.
                It serves as a flag indicating that 
                the command will run in a new thread.)
            (assoc arg-dict "thread" True) )
        (when (in "n" exec-mode) 
            (assoc arg-dict "display" False) )
        (when (in "f" exec-mode) 
            (assoc arg-dict "command" (ScriptCode (+ "f" (repr code) ) ) ) )
        (when retvar
            (assoc arg-dict "retvar" retvar))
        (when (= shell-name "uow")
            (setv command-prefix (if (in "f" exec-mode) "f" "") )
            (assoc arg-dict 
                "command" 
                (ScriptCode f"['bash', '-c', {command-prefix}{(repr code)}]") ) )
        arg-dict)  

    (defn translate [self code &optional verbose]
        (setv leading-blanks (-get-leading-blanks code) )
        (call= code .lstrip)
        (setv arg-dict (.-arg-parse self code) ) 

        (comment 
            "thread" is a flag rather than an arg)
        (setv is-thread (.pop arg-dict "thread" False) )
        (if is-thread
            (setv thread-code ".new_thread_run") 
        #_else
            (setv thread-code "") )

        (setv retvar (.pop arg-dict "retvar" "") )

        (setv arg-str    (Scripting.convert-args-to-str #** arg-dict) )
        (setv hy-arg-str (Scripting.hy-convert-args-to-str #** arg-dict) )

        (setv py-result 
            f"{leading-blanks}{self.node-path}.run{thread-code}({arg-str})" )
        (setv hy-result 
            f"{leading-blanks}(.run{(.replace thread-code \"_\" \"-\")} {self.hy-node-path} {hy-arg-str})")

        (when retvar
            (setv py-result f"{retvar} = {py-result}")
            (setv hy-result f"(setv {retvar} {hy-result})") )

        (setv result (, py-result hy-result) ) 
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
                (write f"'store=True' indicating that the contents of stdout & stderr are stored in the return value.\n" "TIP") ) )
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
