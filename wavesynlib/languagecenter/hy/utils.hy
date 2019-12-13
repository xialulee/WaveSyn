(require [hy.extra.anaphoric [*]])
(import [hy.contrib.walk [postwalk]])



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



(defmacro modify-as [target alias &rest procs]
    `(setv ~target (do ~@(postwalk 
        (fn [item]
            (if (and (symbol? item) (= item alias))
                target
            #_else
                item))
        procs))))



(defmacro call= [obj f]
    `(setv ~obj (~f ~obj)))



(defmacro dyn-setv [&rest args]
    `(do ~@(gfor [name sexpr] (partition args)
        `(assoc (locals) (mangle ~name) ~sexpr) ) ) )

(defmacro dyn-defn [name args &rest body]
    `(assoc (locals) (mangle ~name) (fn ~args ~@body)))

(defmacro dyn-defprop [name getter &optional setter]
    (setv sexpr `(property ~getter))
    (when setter (setv sexpr `(.setter ~sexpr ~setter)))
    `(assoc (locals) (mangle ~name) ~sexpr))

(defmacro defprop [name getter &optional setter]
    `(do
        (require wavesynlib.languagecenter.hy.utils)
        (wavesynlib.languagecenter.hy.utils.dyn-defprop ~(str name) ~getter ~setter)))



(defmacro freeze [vars func]
    (setv arglist
        (list (chain
            ['&optional]
            (gfor var vars [var var]))))
    (if (= (first func) 'defn) (do 
        (.pop func 0)
        (setv func-name (first func))
        (setv (. func [0]) 'fn)
        `(setv ~func-name ((fn ~arglist ~func))))
    #_else
        `((fn ~arglist ~func))))



(defmacro bit-names [&rest names]
    `(setv ~@(flatten
        (gfor [idx name] (enumerate names)
            :if (!= name 'None)
            [name (<< 1 idx)]))))



(defmacro/g! on-exit [&rest exprs]
    `(do
        (setv ~g!mod (--import-- "atexit") )
        (setv ~g!reg (getattr ~g!mod "register") ) 
        (~g!reg (fn []
            ~@exprs) ) 
        None) )



(defmacro super-init [&rest args]
    `(.--init-- (super) ~@args) )



(defmacro make-slots [&rest args]
    (setv args (gfor arg args (mangle arg) ) )
    `(setv --slots-- (, ~@args) ) )
