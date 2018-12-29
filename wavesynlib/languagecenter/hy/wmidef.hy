(import json)
(import [hy.models [HyExpression]])



(defn wqlrepr [arg]
    (json.dumps arg))


(defn handle-select [arg]
    (cond 
    [(instance? HyExpression arg) 
        arg]
    [(coll? arg) 
        (.join ", " arg)]
    [(symbol? arg)
        (str arg)]
    [True
        (str arg)]))


(defn handle-from [arg]
    (cond
    [(instance? HyExpression arg)
        arg]
    [(symbol? arg)
        (str arg)]
    [True 
        (str arg)]))


(defn handle-where [arg]
    (cond
    [(symbol? arg)
        (str arg)]
    [(coll? arg)
        (cond
        [(= (first arg) 'not)
            `(.format "(not {})" ~(handle-where (second arg)))]
        [(in (first arg) ['and 'or '<= '< '>= '> '!= '<> '= 'isa 'is 'like])
            `(.format "({} {} {})" 
                ~(-> arg (get 1) (handle-where)) 
                ~(-> arg (first) (str)) 
                ~(-> arg (get 2) (handle-where)))]
        [True
            arg])]
    [(instance? str arg)
        (wqlrepr arg)]
    [True 
        arg]))


(defmacro wql [&rest args]
    (setv clauses [])

    (setv dispatch {
        "select" 
            (fn [c] (.append clauses `(.format "{} {}" "SELECT" ~(handle-select c))))
        "from"
            (fn [c] (.append clauses `(.format "{} {}" "FROM" ~(handle-from c))))
        "where"
            (fn [c] (.append clauses `(.format "{} {}" "WHERE" ~(handle-where c))))})

    (for [[c0 c1] (partition args)]
        (setv c0 (.lower (str c0)))
        ((get dispatch c0) c1))
    `(.join " " [~@clauses]))

