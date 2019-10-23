(import [hy.contrib.walk [postwalk]])
(import [copy [copy]])



(defn -generate-cond-expr [conditions &optional tag-name]
    `(when 
        (and 
            ~@(chain
                (if tag-name
                    [`(= tag ~(str tag-name) )]
                #_else
                    []) 
                (gfor [key val] (.items conditions) 
                    `(= (getattr self ~f"_flag_in_{key}" 0) ~val) ) ) ) ) )



(defn -handle-match [tag-name procs enter-list leave-list data-list &optional conditions]
    (unless conditions
        (setv conditions {tag-name 0}) )
    (setv new-cond (copy conditions) )
    (assoc new-cond tag-name (inc (.get new-cond tag-name 0) ) )
    (setv cond-expr (-generate-cond-expr conditions tag-name) )
    (setv new-cond-expr (-generate-cond-expr new-cond tag-name) ) 

    (.append procs (HyExpression `(enter 
        (setattr self 
            ~f"_flag_in_{tag-name}"
            (inc (getattr self ~f"_flag_in_{tag-name}" 0) ) ) ) ) )

    (.append procs (HyExpression `(leave
        (setattr self 
            ~f"_flag_in_{tag-name}"
            (dec (getattr self f"_flag_in_{tag-name}") ) ) ) ) )

    (for [proc procs]
        (cond 
        [(= 'enter (first proc))
            (.append enter-list
                (HyExpression (chain
                    cond-expr
                    [`((fn [] ~@(rest proc) ))] ) ) )]
        [(= 'leave (first proc))
            (.append leave-list
                (HyExpression (chain
                    new-cond-expr
                    [`((fn [] ~@(rest proc) ) )]) ) )]
        [(= 'match (first proc))
            (-handle-match (second proc) (cut proc 2 None) enter-list leave-list data-list new-cond)]
        [(= 'data (first proc))
            (.append data-list
                (HyExpression (chain
                    (-generate-cond-expr new-cond)
                    [`((fn [] ~@(rest proc) ))] ) ) ) ]) ) )



(defmacro/g! traveller [name &rest processes]
    (setv shared-vars []
          var-names []
          enter-procs []
          leave-procs []
          data-procs []
          finish-proc None)

    (for [proc processes]
        (setv proc (postwalk (
            fn [item]
                (cond 
                [(symbol? item)
                    (setv dot-pos  (.find item ".")
                          sym-rest "")
                    (when (pos? dot-pos)
                        (setv sym-rest (cut item (inc dot-pos) None)
                              item     (cut item 0 dot-pos)))
                    (if (in item var-names)
                        (HySymbol (.join "" [
                            "self.-shared-"
                            item
                            (if sym-rest (+ "." sym-rest) "")]))
                    #_else
                        item)]
                [True item])) 
            proc))

        (setv inst (first proc))
        (cond 
        [(= 'shared inst) 
            (for [[var-name var-value] (-> proc (rest) (partition))]
                (shared-vars.append (, (str var-name) var-value))
                (var-names.append var-name))]
        [(= 'finish inst) 
            (setv actions (cut proc 1 None))
            (setv finish-proc `((fn [] ~@actions)))]
        [(= 'match inst)
            (-handle-match (second proc) (cut proc 2 None) enter-procs leave-procs data-procs)]))

    `(setv ~name ((fn []
        (import html.parser)
        (defclass ~g!Traveller [html.parser.HTMLParser]
            (defn --init-- [self]
                (.--init-- (super))
                (for [[name val] [~@shared-vars]] 
                    (setattr self (mangle f"-shared-{name}") val) ) )
            ~(if enter-procs
                `(defn handle-starttag [self tag attrs]
                    ~@enter-procs))
            ~(if leave-procs
                `(defn handle-endtag [self tag]
                    ~@leave-procs))
            ~(if data-procs
                `(defn handle-data [self data]
                    ~@data-procs))
            (defn -get-result [self]
                ~finish-proc))
        (fn [code]
            (setv obj (~g!Traveller))
            (obj.feed code)
            (obj.-get-result)) )) ) )

