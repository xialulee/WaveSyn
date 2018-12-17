
(defmacro/g! traveller [name processes]
    (setv shared-vars []
          var-names []
          enter-procs []
          leave-procs []
          data-procs []
          finish-proc None)

    (defn subs-vars [li]
        (for [k (-> li (len) (range))]
            (setv item (get li k))
            (cond 
                [(symbol? item) 
                    (setv dot-pos (.find item ".")
                          sym-rest "")
                    (if (> dot-pos 0) 
                        (setv sym-rest (cut item (inc dot-pos) None)
                              item (cut item 0 dot-pos)))
                    (if (in item var-names) 
                        (setv (get li k) (HySymbol (
                            .join "" [
                                "self.-" 
                                item 
                                (if sym-rest (+ "." sym-rest) "")]))))]
                [(coll? item) (subs-vars item)])))

    (for [proc processes]
        (subs-vars proc)
        (setv inst (first proc))
        (cond [(= 'shared inst) 
                  (for [[var-name var-value] (-> proc (rest) (partition))]
                      (shared-vars.append (, (str var-name) var-value))
                      (var-names.append var-name))]
              [(= 'on-data inst) 
                  (setv actions (cut proc 1 None))
                  (data-procs.append `((fn [] ~@actions)))]
              [(= 'on-finish inst) 
                  (setv actions (cut proc 1 None))
                  (setv finish-proc `((fn [] ~@actions)))]
              [(in inst ['on-enter 'on-leave]) (do 
                  (setv tag-name (-> proc (get 1) (str)))
                  (setv expr `(= tag ~tag-name))
                  (setv actions (cut proc 2 None))
                  (if (= inst 'on-enter) 
                      (setv target enter-procs) 
                  ; else
                      (setv target leave-procs))
                  (target.append `(if ~expr ((fn [] ~@actions)))))]))

    `(setv ~name ((fn []
        (import html.parser)
        (defclass ~g!Traveller [html.parser.HTMLParser]
            (defn --init-- [self]
                (.--init-- (super))
                (for [[name val] [~@shared-vars]] 
                    (setattr self (mangle (+ "-" name)) val)))
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

