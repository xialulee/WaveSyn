(require [hy.extra.anaphoric [*]])
(import json)



(setv -op-map {
    "Plus"     '+
    "Times"    '*
    "Power"    '**
    "Rational" '/
})



(defn list-to-expr [json-obj arg-set]
    (setv head (get -op-map (first json-obj) ) )
    (setv tail 
        (ap-map (
            cond
                [(instance? list it)
                    (list-to-expr it arg-set)]
                [(instance? str it)
                    (.add arg-set it)
                    (HySymbol it)]
                [True
                    it]) 
            (rest json-obj) ) )
    `(~head ~@tail) )



(defn create-func [json-str]
    (setv json-obj (json.loads json-str) )
    (setv arg-set (set []) ) 
    (setv expr (list-to-expr json-obj arg-set) )
    (fn [&kwargs kwargs]
        (ap-each arg-set (assoc (locals) it (get kwargs it) ) ) 
        (eval expr) ) )
