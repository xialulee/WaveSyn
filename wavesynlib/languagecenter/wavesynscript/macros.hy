
(setv wavesynscript-name 'WAVESYNSCRIPT-CE006C7F-2A67-437D-9444-6F2E6D645AA3)

(defmacro init-wavesynscript-macros []
    `(import [wavesynlib.languagecenter.wavesynscript :as ~wavesynscript-name]))

(import [funcparserlib.parser [many]])
(import [hy.model-patterns [whole brackets SYM]])



(setv -lazy-binder-parser (whole [
    (many 
        (| 
            (brackets SYM SYM) 
            (brackets SYM SYM SYM))) ]))

(defmacro BindLazyNode [&rest definition]
    (setv [nodes] (.parse -lazy-binder-parser definition) )
    (setv info-list 
        (lfor [node-name #* type-info] nodes
            :setv info-len (len type-info)
            (if (= 1 info-len)
                [node-name [:class-object (first type-info)]]
            #_else
                [node-name [
                    :module-name (-> type-info first  str)
                    :class-name  (-> type-info second str)]]) )) 
    `(do ~@(lfor [node-name type-info] info-list
        `(setv ~node-name 
            ((. ~wavesynscript-name ModelNode) 
                :is-lazy True
                ~@type-info)) ) ) )

