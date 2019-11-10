(import [numpy [exp complex128]])
(import [numpy.random [randn]])



(defn complex-gaussian [size &optional [σ² 1]]
    (setv a (** (/ σ² 2) 0.5) ) 
    (* a 
        (+ 
            (randn #* size)
            (* 1j (randn #* size)) ) ) ) 
