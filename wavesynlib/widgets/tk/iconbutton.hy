(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [tkinter.ttk [Button]])
(import [PIL [ImageTk]])

(import [wavesynlib.fileutils.photoshop.psd [get-pil-image]])
(import [.utils.loadicon [load-icon]])



(defclass IconButton [Button]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs) 
        (setv self.--icon None)) 
        
    (defprop common-icon
        #_getter
        (fn [self]
            self.--icon)
        #_setter
        (fn [self icon]
            (assoc self "image"
                (setx self.--icon (load-icon icon :common True)))) ) )
