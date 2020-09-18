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
        (.add-observer self.--timer (fn [&rest args &kwargs kwargs]
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




;import os

;from quantities import second

;from .dirindicator import DirIndicator



;class CWDIndicator(DirIndicator):
    ;def __init__(self, *args, **kwargs):
        ;self.__chdir_func = kwargs.pop('chdir_func', None)
        
        ;super().__init__(*args, **kwargs)
                        
        ;from wavesynlib.interfaces.timer.tk import TkTimer
        ;self.__timer = TkTimer(self, interval=0.5*second)
        ;self.__timer.add_observer(self)
        ;self.__timer.active = True
        
                                                              
    ;def update(self, *args, **kwargs): 
        ;'''Method "update" is called by Observable objects. 
;Here, it is called by the timer of CWDIndicator instance.
;Normally, no argument is passed.'''        
        ;cwd = os.getcwd()
        ;if not isinstance(cwd, str):
            ;cwd = cwd.decode(self._coding, 'ignore')
        ;if os.path.altsep is not None: # Windows OS
            ;cwd = cwd.replace(os.path.altsep, os.path.sep)
        ;if self._directory != cwd:
            ;self.change_dir(cwd, passive=True)
            

    ;def change_dir(self, dirname, passive=False):
        ;'''Change current working directory.
;dirname: new working directory,
;passive: False if the directory is changed by this widget,
         ;True if the directory is changed by other methods.
;'''
        ;if self.__chdir_func:
            ;self.__chdir_func(dirname, passive)
        ;else: # default change dir func
            ;os.chdir(dirname)  
        ;super().change_dir(dirname)          
