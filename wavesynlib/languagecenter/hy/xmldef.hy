(defmacro tag [name &rest args]
    (setv len-args (len args))
    (cond 
    [(= 1 len-args)
        (setv [attr children] ["" (first args)])]
    [(= 2 len-args)
        (setv [attr children] args)])

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
        (str.join "\n" ~children) 
        (.format "</{}>" ~name)]))

