(require [hy.extra.anaphoric [*]])



(setv -op-priority {
    '< 0
    '<= 0
    '> 0
    '>= 0
    '= 0
    '!= 0
    'is 0
    'is-not 0
    'in 0
    'not-in 0
    'instance-of 0
    '+ 1
    '- 1
    '* 2
    '@ 2
    '/ 2
    '// 2
    '% 2
    '** 3})


(defn infix-to-prefix [expr]
    (if-not (instance? HyExpression expr)
        (return expr))

    (defn dget [d k]
        (if (coll? k) 
	    ; HyExpression is not hashable
            ; hence cannot be used as dict.get
            ; default value.
            Inf
            (d.get k Inf)))

    (setv priority-list
        (list (ap-map (dget -op-priority it) expr)))

    (if (all (ap-map (= it Inf) priority-list))
        (return expr))

    (setv lowest-index (-> priority-list
        (min)
        (priority-list.index)))
    (setv lowest-op (get expr lowest-index))

    (if (= lowest-op 'instance-of)
        (setv lowest-op 'isinstance))

    (defn len1 [expr]
        (if (= 1 (len expr))
            (first expr)
            expr))

    (setv left-expr (-> expr (cut 0 lowest-index) len1))
    (setv right-expr (-> expr (cut (inc lowest-index) None) len1))
    (setv retval '())
    (retval.append lowest-op)
    (retval.extend (map infix-to-prefix 
        [left-expr right-expr]))
    retval)



(defmacro infix [expr] (infix-to-prefix expr))

