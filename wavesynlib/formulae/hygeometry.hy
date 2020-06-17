(defn calc-fit-rect [screen-size image-size &optional return-float]
    (setv 
        [sw sh] screen-size
        [iw ih] image-size
        sratio  (/ sw sh)
        iratio  (/ iw ih)
        cx      (/ sw 2)
        cy      (/ sh 2))
    
    (if (> iratio sratio) (do
        (setv 
            scale (/ sw iw)
            nh    (* ih scale)
            x     0
            y      (- cy (/ nh 2))
            w     sw
            h     nh)
    ) #_else (do
        (setv 
            scale (/ sh ih)
            nw    (* iw scale)
            x     (- cx (/ nw 2))
            y     0
            w     nw
            h     sh)
    ))
    
    (setv result [x y w h])
    
    (unless return-float
        (setv result (lfor i result (int i))))
        
    result)
