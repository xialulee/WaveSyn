(defn -args-to-dict [args]
    (setv retval {})
    (for [[key value] (partition args)]
        (if (keyword? key)
            (setv key (name key)))
        (assoc retval key value))
    retval)



(defn -sexpr-to-dict [sexpr]
    (setv retval {})
    (assoc retval "class" (first sexpr))
    (assoc retval "name" (-> sexpr (second) (str) (mangle)))
    (for [item (nth sexpr 2)]
        (setv tag (-> item (first) (str)))
        (cond 
            [(in tag ["pack" "grid" "setattr" "config"])
                (assoc retval tag (-args-to-dict (rest item)))]
            [(= tag "child") 
                (if (not-in "children" retval)
                    (assoc retval "children" []))
                (.append 
                    (get retval "children") 
                    (-sexpr-to-dict (-> item (rest) (list))))]
            [True (assoc retval tag (second item))]))
    retval)



(defmacro widget [type- id- desc]
    (setv widget-desc (-sexpr-to-dict [type- id- desc]))
    `(setv ~id- ~widget-desc))


