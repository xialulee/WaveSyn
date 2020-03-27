(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [tkinter [Frame]])
(import [tkinter.ttk [Label]])



(defclass Group [Frame]
    (defn --init-- [self &rest args &kwargs kwargs]
        (super-init #* args #** kwargs)
        (unless (in "relief" kwargs)
            (assoc self "relief" "groove"))
        (unless (in "bd" kwargs)
            (assoc self "bd" 2))
        (setv label-name (Label self))
        (.pack label-name :side "bottom")
        (setv self.--label-name label-name))
        
    (defprop name
        #_getter
        (fn [self]
            (. self --label-name ["text"]))
        #_setter
        (fn [self name]
            (assoc self.--label-name "text" name))))
