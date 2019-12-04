(import [numpy [sum matrix array]])



(defmacro npget [arr &rest args]
    `(get ~arr (tuple ~args) ) )


(defmacro getrows [arr sel]
    `(get ~arr (tuple [~sel (slice None) ]) ) )


(defmacro getcols [arr sel]
    `(get ~arr (tuple [(slice None) ~sel]) ) )


(defn ‖v [A &optional weight]
    (if (instance? matrix A) (setv A (array A) ) )
    (if (instance? matrix weight) (setv weight (array weight) ) )
    (setv B 
        (if (not? weight None)
            (@ weight A) 
        #_else
            A) ) 
    (setv C (* (.conj A) B) ) 
    (sum C :axis 0) )
    