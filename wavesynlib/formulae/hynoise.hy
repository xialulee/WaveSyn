(import [numpy [exp complex128 sqrt :as √]])
(import [numpy.random [randn]])



(defn complex-gaussian [size &optional [σ² 1]]
    (setv size (if (coll? size) 
        size 
    #_else
        (, size) ) )
    (* (√ (/ σ² 2))
        (+ 
            (randn #* size)
            (* 1j (randn #* size)) ) ) ) 
