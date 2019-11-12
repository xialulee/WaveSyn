(defmacro npget [arr &rest args]
    `(get ~arr (tuple ~args) ) )
    