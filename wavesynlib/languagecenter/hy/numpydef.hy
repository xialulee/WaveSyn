(import [numpy [sum matrix array]])


(defn -isnum [x]
    (try
        (int x)
    (except []
        (return False) ) ) 
    (return True) )


(defn -symbol-to-slice [sym]
    (cond 
    [(and (symbol? sym) (in (first sym) "↔↕"))
        (setv sym (get sym (slice 1 None) ) ) 
        (setv items (.split sym ":") )
        (setv items 
            (map (fn [x] 
                (cond 
                [(= x "") 'None] 
                [(-isnum x) (int x)]
                [True (HySymbol x)]) ) 
            items) ) 
        (setv items (list items))
        (.extend items ['None 'None 'None])
        (setv items (get items (slice None 3) ) )
        `(slice #* [~@items])]
    [True sym]) )



(defmacro npget [arr &rest args]
    (setv args (list (map -symbol-to-slice args) ) )
    `(get ~arr (tuple ~args) ) )


(defmacro npassoc [arr &rest args]
    (setv val (last args) ) 
    (setv args (get args (slice 0 -1) ) ) 
    (setv args (list (map -symbol-to-slice args) ) ) 
    `(assoc ~arr (tuple ~args) ~val) )


(defmacro getrows [arr sel]
    (setv sel (-symbol-to-slice sel) )
    `(get ~arr (tuple [~sel (slice None) ]) ) )


(defmacro getcols [arr sel]
    (setv sel (-symbol-to-slice sel) )
    `(get ~arr (tuple [(slice None) ~sel]) ) )


(defn ‖v [A &optional weight]
    (if (instance? matrix A) (setv A (array A) ) )
    (if (instance? matrix weight) (setv weight (array weight) ) )
    (setv B 
        (if (not? weight None)
            (@ weight A) 
        #_else
            A) ) 
    (setv C (* (.conj A) B) ) 
    (sum C :axis 0) )
    