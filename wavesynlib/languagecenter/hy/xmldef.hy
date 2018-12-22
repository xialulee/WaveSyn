(defmacro tag [name &rest args]
    (setv len-args (len args))
    (cond 
    [(= 1 len-args)
        (setv [attr child] ["" (first args)])]
    [(= 2 len-args)
        (setv [attr child] args)]

    (if (symbol? name) (setv name (str name)))

    `(.join "" [ 
        (.format "<{}{}>" 
            ~name
            (if-not ~attr
                ""
            ;else
            ((fn []
                (.join "" (gfor [key val] (partition ~attr) (do
                    (if (keyword? key) 
                        (setv key (name key)))
                    (.format " {}=\"{}\"" key val)))))))) 
        (str.join "\n" ~child) 
        (.format "</{}>" ~name)]))

