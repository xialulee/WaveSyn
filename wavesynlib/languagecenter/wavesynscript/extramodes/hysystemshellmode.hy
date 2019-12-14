(require [wavesynlib.languagecenter.hy.utils [call= super-init]])

(import locale)
(setv -encoding (locale.getpreferredencoding) )
(import subprocess)
(import sys)

(import [hy.contrib.hy-repr [hy-repr]])

(import [.basemode [ModeInfo BaseMode]])
(import [wavesynlib.languagecenter.wavesynscript [ModelNode]])



(defclass SystemShell [ModelNode BaseMode]
    (setv -MODE-PREFIX "#M!") 
    
    #@(classmethod
    (defn get-prefix [cls]
        (cls.-MODE_PREFIX) ) ) 
        
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (with [self.attribute-lock]
            (setv self.info (ModeInfo "system_shell" False self) ) ) ) 
            
    (defn --run-process [self code]
        (setv PIPE subprocess.PIPE) 
        (setv p (subprocess.Popen code :shell True :stdin PIPE :stdout PIPE :stderr PIPE) ) 
        (setv [stdout stderr] (.communicate p) ) 
        (print (.decode stdout -encoding "ignore") ) 
        (print (.decode stderr -encoding "ignore") :file sys.stderr) ) 
        
    (defn test [self code]
        (call= code .strip) 
        (if (and code (.startswith code self.-MODE-PREFIX) ) 
            self.info
        #_else
            False) ) 
            
    (defn run [self code &optional [store False] [thread False]]
        (comment "To-Do:
                Support store stdout & stderr;
                Support run in thread.") 
        (.--run-process self code) ) 
        
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
        (setv display-language self.root-node.lang-center.wavesynscript.display-language) 
        (setv expr-str f"{self.node-path}.run({(repr code)})")
        (setv display-str
            (if (= display-language "python") 
                expr-str
            #_else
                f"(.run {self.hy-node-path} {(hy-repr code)})") ) 
        (, expr-str display-str) ) )