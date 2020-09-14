(import [PIL [ImageTk]])
(import [wavesynlib.fileutils.photoshop.psd [get-pil-image]])


(defn load-icon [path &optional [common False]]
    (when common
        (import [wavesynlib.languagecenter.wavesynscript [Scripting]]) 
        (setv path (.get-gui-image-path Scripting.root-node path)) ) 
    (if (= (last (.split path ".")) "psd") (do
        (with [psd-file (open path "rb")]
            (setv 
                pil-image (first (get-pil-image psd-file))
                result    (ImageTk.PhotoImage :image pil-image))))
    #_else (do
        (setv result (ImageTk.PhotoImage :file path))))
    result)