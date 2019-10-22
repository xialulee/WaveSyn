(defmacro/g! BindLazyNode [&rest args]
    `(do
        (import [wavesynlib.languagecenter.wavesynscript [ModelNode :as ~g!ModelNode]]) 
        ~@(lfor [target module klass] (partition args 3)
            `(setv ~target (~g!ModelNode 
                :is-lazy True
                :module-name ~(str module) 
                :class-name ~(str klass) ) ) ) ) )
