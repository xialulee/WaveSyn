(defmacro npget [arr &rest args]
    `(get ~arr (tuple ~args) ) )


(defmacro getrows [arr sel]
    `(get ~arr (tuple [~sel (slice None) ]) ) )


(defmacro getcols [arr sel]
    `(get ~arr (tuple [(slice None) ~sel]) ) )
    