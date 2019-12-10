(require [hy.extra.anaphoric [%]])
(require [wavesynlib.languagecenter.hy.utils [defprop]])



(defclass Constant []
"Constant type of wavesynscript."
    [--slots-- (, "__name" "__value" "__doc")
     --cache   {}]
    
    (defn --new-- [cls name &optional value doc]
        (if (in name cls.--cache) (do
            (setv c (. cls --cache [name]) ) 
            (if (!= value c.value) 
                (raise (ValueError "This constant has already been initialized with a different value.") ) ) 
            c) 
        #_else
            (.--new-- object cls) ) ) 
            
    (defn --init-- [self name &optional value doc]
        (unless (in name self.--cache) 
            (setv
                self.--name  name
                self.--value value
                self.--doc   doc
                (. self --cache [name]) self) ) ) 
                
    (defprop name 
        #_getter
        #%(. %1 --name) ) 
        
    (defprop value
        #_getter
        #%(. %1 --value) ) 
        
    (defprop doc
        #_getter
        #%(. %1 --doc) ) 
        
    (defn help [self] (print self.doc) ) )
