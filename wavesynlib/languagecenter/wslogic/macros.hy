(defmacro defvars [&rest args]
    `(setv [~@args] ((fn []
        (import sympy)
        (sympy.symbols ~(.join "," (gfor arg args (str arg)) )) ))))

