
(setv wavesynscript-name 'WAVESYNSCRIPT-CE006C7F-2A67-437D-9444-6F2E6D645AA3)

(defmacro init-wavesynscript-macros []
    `(import [wavesynlib.languagecenter.wavesynscript :as ~wavesynscript-name]))

(import [funcparserlib.parser [many]])
(import [hy.model-patterns [whole brackets SYM]])



(setv -lazy-binder-parser (whole [
    (many 
        (|
            (+ SYM SYM)
            (+ SYM (brackets SYM SYM))))]))

(defmacro BindLazyNode [&rest definition]
    (setv [nodes] (.parse -lazy-binder-parser definition) )
    (setv info-list 
        (lfor [node-name type-info] nodes
            (if (coll? type-info)
                [node-name [
                    :module-name (-> type-info first  str)
                    :class-name  (-> type-info second str)]]
            #_else
                [node-name [:class-object type-info]]) )) 
    `(do ~@(lfor [node-name type-info] info-list
        `(setv ~node-name 
            ((. ~wavesynscript-name ModelNode) 
                :is-lazy True
                ~@type-info)) ) ) )

