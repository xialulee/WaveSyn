(require [hy.contrib.loop [loop]])
(require [wavesynlib.languagecenter.hy.utils [
    call= super-init ]])

(import re)

(import [wavesynlib.languagecenter.wavesynscript [
    ModelNode Scripting ScriptCode code-printer]])
(import [.pattern [command-pattern arg-pattern]])
(import [..basemode [BaseMode ModeInfo]])


(defn -get-leading-blanks [s]
    (setv t (.lstrip s) ) 
    (setv d (- (len s) (len t) ) ) 
    (cut s 0 d) )


(defn command-parse [command]
    (call= command .lstrip) 
    (setv m (re.match command-pattern command) ) 
    (setv name (get m 0) ) 
    (setv command (cut command (len name) ) ) 
    (setv args 
        (loop [[result []] [left command]]
            (call= left .lstrip)
            (setv m (re.match arg-pattern left) )
            (if (none? m) 
                result
            #_else (do
                (setv arg (get m 0) ) 
                (.append result arg) 
                (setv left (cut left (len arg) ) ) 
                (recur result left) ) ) ) ) 
    (, name args) )



(defclass Magic [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M%") 
    (setv -PREFIX-ARG-PATTERN (re.compile
r"(?P<exec_mode>[f]*)" re.VERBOSE))

    #@(classmethod
    (defn get-prefix [cls]
        (cls.-MODE-PREFIX) ) ) 
        
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (with [self.attribute-lock]
            (setv self.info (ModeInfo "magic" False self) ) ) ) 
            
    (defn test [self code]
        (if (.startswith (.lstrip code) self.-MODE-PREFIX) 
            self.info
        #_else
            False) ) 
            
    (defn run [self command]
        (setv [name args] (command-parse command) ) 
        (print name args) ) 

    (defn -arg-parse [self code]
        (setv splited (.split code :maxsplit 1) ) 
        (when (< (len splited) 2) 
            (raise (SyntaxError "Mode prefix and code should be splited by blank.") ) ) 
        (setv [prefix code] splited) 
        (setv prefix-args (cut prefix (len self.-MODE-PREFIX) ) ) 
        (setv match-obj (re.match self.-PREFIX-ARG-PATTERN prefix-args) ) 
        (setv exec-mode (get match-obj "exec_mode") ) 
        (setv result {"command" code}) 
        (when (in "f" exec-mode) 
            (assoc result "command" (ScriptCode (+ "f" (repr code) ) ) ) ) 
        result)
    
    (defn translate [self code &optional verbose]
        (setv leading-blanks (-get-leading-blanks code) ) 
        (call= code .lstrip) 
        (setv arg-dict (.-arg-parse self code) )
        (setv
            arg-str    (Scripting.convert-args-to-str #** arg-dict) 
            hy-arg-str (Scripting.hy-convert-args-to-str #** arg-dict) )
        (, 
            f"{leading-blanks}{self.node-path}.run({arg-str})"
            f"{leading-blanks}(.run {self.hy-node-path} {hy-arg-str})") ) 
            
    (defn execute [self code]) )
