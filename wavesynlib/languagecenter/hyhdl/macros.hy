(import [hy.contrib.walk [postwalk]])



(defmacro --HYHDL-STMT-RETVAL [] "HYHDL-STMT-RETVAL")



(defmacro HYHDL-INIT []
    `(do 
        (import [myhdl :as MYHDL-NAMESPACE]) 
        (require [wavesynlib.languagecenter.hyhdl.macros [*]]) ) )



(defmacro MODULE [&rest args]
    `(with-decorator MYHDL-NAMESPACE.block
        (defn ~@args (return (MYHDL-NAMESPACE.instances) ) ) ) ) 



(defmacro/g! ALWAYS-COMB [&rest args]
    `(with-decorator MYHDL-NAMESPACE.always-comb
        (defn ~g!comb-func [] ~@args) ) )



(defmacro/g! AP-EACH-BIT [direction sig &rest procs]
    (setv new-procs (postwalk
        (fn [item]
            (cond
            [(and (symbol? item) (= item 'IT) )
                `(get ~sig ~g!index)]
            [(and (symbol? item) (= item 'INDEX-OF-IT) )
                g!index]
            [True item]) ) 
        procs) ) 
            
    `(for [~g!counter (range (len ~sig))]
        ~(cond 
        [(= direction 'MSB-TO-LSB) 
            `(setv ~g!index (- (len ~sig) ~g!counter 1) )] 
        [(= direction 'LSB-TO-MSB)
            `(setv ~g!index ~g!counter)]
        [True
            (raise (ValueError "Unsupported Direction.") )])
        ~@new-procs) )



(defmacro IF-STMT [condition true-procs &optional false-procs]
    `(if ~condition (do
        ~true-procs
        (--HYHDL-STMT-RETVAL) ) 
    #_else ~(if false-procs `(do ~false-procs (--HYHDL-STMT-RETVAL) ) (--HYHDL-STMT-RETVAL) ) ) )



(defmacro IF-EXPR [&rest procs]
    `(if ~@procs) )



(defmacro SETBV [bv val]
    `(setv (cut bv None None) val) )



(defmacro NEXT [&rest args]
    (setv new-args [])
    (for [[lhs rhs] (partition args)]
        (doto new-args
            (.append `(. ~lhs next))
            (.append rhs) ) )
    `(setv ~@new-args) )

