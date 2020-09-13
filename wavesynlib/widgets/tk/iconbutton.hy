(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [tkinter.ttk [Button]])
(import [PIL [ImageTk]])

(import [wavesynlib.fileutils.photoshop.psd [get-pil-image]])



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
            (import [wavesynlib.languagecenter.wavesynscript [Scripting]])
            (setv root-node Scripting.root-node)
            (setv path (.get-gui-image-path root-node icon)) 
            (if (= (last (.split icon ".")) "psd") (do
                (with [psd-file (open path "rb")]
                    (setv pil-image (first (get-pil-image psd-file))) 
                    (setv self.--icon (ImageTk.PhotoImage :image pil-image)) ) ) 
            #_else (do
                (setv self.--icon (ImageTk.PhotoImage :file path)))) 
            (assoc self "image" self.--icon)) ) )
