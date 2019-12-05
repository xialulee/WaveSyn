

(defmacro ∑ [&rest args]
    (setv N (len args) )
    (cond
    [(= N 1) 
        (setv obj (first args) ) 
        `(sum ~obj)]
    [(= N 4)
        (setv [var S formula] [(first args) (get args 2) (last args)]) 
        `(sum (gfor ~var ~S ~formula))]) )
