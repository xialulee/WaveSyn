(import [functools [partial]])



(defn check-value [d i P s S v V W func]
    (try
        (func P) 
        (return True) 
    (except [ValueError]
        (return False) ) ) )


(defclass ValueChecker []
    (defn --init-- [self root]
        (setv self.--root root) 
        (setv 
            self.check-int (, 
                (.register root 
                    (partial check-value :func (fn [v]
                        (when (or (= v "") (= v "-"))
                            (return)) 
                        (int v))))
                "%d" "%i" "%P" "%s" "%S" "%v" "%V" "%W") 
            self.check-float (,
                (.register root
                    (partial check-value :func (fn [v]
                        (when (in v (, "" "-" "-."))
                            (return))
                        (float v)))) 
                "%d" "%i" "%P" "%s" "%S" "%v" "%V" "%W") 
            self.check-positive-float (,
                (.register root
                    (partial check-value :func (fn [v]
                        (when (in v (, "" "+" "." "+."))
                            (return))
                        (when (<= (float v) 0)
                            (raise ValueError)))))
                "%d" "%i" "%P" "%s" "%S" "%v" "%V" "%W")
            self.check-nonnegative-float (,
                (.register root
                    (partial check-value :func (fn [v]
                        (when (in v (, "" "+" "." ".+"))
                            (return))
                        (when (< (float v) 0)
                            (raise ValueError)))))
                "%d" "%i" "%P" "%s" "%S" "%v" "%V" "%W"))))



;def check_value(d, i, P, s, S, v, V, W, func):
    ;try:
        ;func(P)
        ;return True
    ;except ValueError:
        ;return True if P == '' or P == '-' else False
        
        
;def check_positive_float(d, i, P, s, S, v, V, W):
    ;try:
        ;assert float(P) > 0
        ;return True
    ;except (ValueError, AssertionError):
        ;return True if P=='' else False
    
    
    
;def check_nonnegative_float(d, i, P, s, S, v, V, W):
    ;try:
        ;assert float(P) >= 0
        ;return True
    ;except (ValueError, AssertionError):
        ;return True if P=='' else False
    
        

;class ValueChecker:
    ;def __init__(self, root):
        ;self.__root = root
        ;self.check_int = (root.register(partial(check_value, func=int)),
                            ;'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        ;self.check_float = (root.register(partial(check_value, func=float)),
                            ;'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        ;self.check_positive_float = (root.register(check_positive_float),
                                     ;'%d', '%i', '%P', '%s', '%S', '%v', 
                                     ;'%V', '%W')
        ;self.check_nonnegative_float = (root.register(check_nonnegative_float),
                                     ;'%d', '%i', '%P', '%s', '%S', '%v', 
                                     ;'%V', '%W')