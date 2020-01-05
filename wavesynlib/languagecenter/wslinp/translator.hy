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
            (.extend loopbody (rest item))]
        [(instance? HyExpression head)
            (setv do-clauses '(do))
            (setv else-clauses '(do))
            (for [clause (rest item)]
                (if (= "else" (first clause))
                    (.extend else-clauses (rest clause))
                #_else
                    (.append do-clauses clause)))
            (.append loopbody `(if ~head ~do-clauses ~else-clauses))]))
    `(do 
        ~begin 
        (while (.load-next-record engine)
            ~loopbody)
        ~end))
