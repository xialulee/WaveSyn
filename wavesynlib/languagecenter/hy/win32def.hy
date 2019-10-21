(defmacro/g! import-func [dll-name &rest func-names]
    `(do
        (import [ctypes [windll :as ~g!windll]]) 
        ~@(lfor func-name func-names
            `(setv ~func-name (. ~g!windll ~dll-name ~func-name) ) ) ) )
