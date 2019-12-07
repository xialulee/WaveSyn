(import [numpy [atleast-1d exp sqrt :as √]])
(import [numpy.random [randn]])



(defn complex-gaussian [size &optional [σ² 1]]
    (setv size (atleast-1d size) )
    (* (√ (/ σ² 2))
        (+ 
            (randn #* size)
            (* 1j (randn #* size)) ) ) ) 
