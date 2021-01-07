(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import os)

(import [quantities [second]])

(import [.dirindicator [DirIndicator]])
(import [wavesynlib.interfaces.timer.tk [TkTimer]])



(defclass CWDIndicator [DirIndicator]
    (defn --init-- [self &rest args &kwargs kwargs]
        (setv self.--chdir-func (.pop kwargs "chdir_func" None))
        (super-init #* args #** kwargs)
        (setv self.--timer (TkTimer self :interval (* 0.5 second)))
        (.add-observer self.--timer (fn [event]
            (setv cwd (os.getcwd))
            (unless (instance? str cwd)
                (setv cwd (.decode cwd self.-coding "ignore")))
            (when (is-not os.path.altsep None) 
                (comment "Windows OS")
                (setv cwd (.replace cwd os.path.altsep os.path.sep)))
            (when (!= self.-directory cwd)
                (.change-dir self cwd :passive True))))
        (setv self.--timer.active True))
                
    (defn change-dir [self dirname &optional [passive False]]
        (if self.--chdir-func (do
            (.--chdir-func self dirname passive)) 
        #_else (do
            (os.chdir dirname)))
        (.change-dir (super) dirname)))



