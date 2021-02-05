(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [pathlib [Path]])
(import [tkinter.ttk [Button]])
(import [PIL [ImageTk]])

(import [.utils.loadicon [load-icon]])



(defclass IconButton [Button]
    (defn --init-- [self &rest args &kwargs kwargs]
        (setv icon (.pop kwargs "image" None) )
        (when icon
            (when (instance? (, Path str) icon)
                (setv icon (load-icon icon :common True)))
            (assoc kwargs "image" icon))
        (super-init #* args #** kwargs) 
        (setv self.--icon icon) )
        
    (defprop common-icon
        #_getter
        (fn [self]
            self.--icon)
        #_setter
        (fn [self icon]
            (assoc self "image"
                (setx self.--icon (load-icon icon :common True)))) ) )
