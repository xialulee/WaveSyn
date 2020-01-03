(defn translate [code-str]
    (setv code-str f"[{code-str}]") 
    (setv code-list (read-str code-str))
    (setv begin    '(do))
    (setv end      '(do))
    (setv loopbody '(do))
    (for [item code-list]
        (setv head (first item))
        (cond
        [(= 'BEGIN head)
            (.extend begin (rest item))]
        [(= 'END head)
            (.extend end (rest item))]
        [(= '% head)
            (.extend loopbody (rest item))]))
    `(do 
        ~begin 
        (while (.load-next-record engine)
            ~loopbody)
        ~end))
