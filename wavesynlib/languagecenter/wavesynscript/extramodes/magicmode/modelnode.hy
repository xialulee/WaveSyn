(require [hy.contrib.loop [loop]])
(require [wavesynlib.languagecenter.hy.utils [
    call= super-init ]])

(import re)
(import importlib)

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
        cls.-MODE-PREFIX ) ) 
        
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
        (.insert args 0 name) 
        (setv mod 
            (importlib.import-module 
                f".commands.{name}"
                :package 
                    (first (.rsplit self.--module-- 
                        :sep "." :maxsplit 1) ) ) ) 
        (setv main mod.main) 
        (main self.root-node args) ) 

    (defn -arg-parse [self code]
        (setv [prefix-args code] (.-split-code self code) )
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
            (write "The translated code is given as follows\n" "TIP") 
            (write f"{(get result lang-index)}\n" "HISTORY") ) 
        result) 
            
    (defn execute [self code]) )
