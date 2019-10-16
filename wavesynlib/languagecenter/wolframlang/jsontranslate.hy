(require [hy.extra.anaphoric [*]])
(import json)



(setv -op-map {
    "Plus"     '+
    "Times"    '*
    "Power"    '**
    "Rational" '/
})



(defn list-to-expr [json-obj arg-set]
    (setv items [(get -op-map (first json-obj))]) 
    (for [i (rest json-obj) ]
        (cond 
        [(instance? list i) 
            (.append items (list-to-expr i arg-set) )]
        [(instance? str i)
            (.append items (HySymbol i) )
            (.add arg-set i)] 
        [True 
            (.append items i)] ) ) 
    `(~@items) )



(defn create-func [json-str]
    (setv json-obj (json.loads json-str) )
    (setv arg-set (set []) ) 
    (setv expr (list-to-expr json-obj arg-set) )
    (fn [&kwargs kwargs]
        (ap-each arg-set (assoc (locals) it (get kwargs it) ) ) 
        (eval expr) ) )
