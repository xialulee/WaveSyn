(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import [datatypes [TolNone]])
(import [translator [translate]])


(defclass TolLocals [dict]
    (defn --init-- [self kwargs engine]
        (setv self.--engine engine)
        (super-init #** kwargs))
        
    (defn --getitem-- [self key]
        (setv engine self.--engine)
        (setv globals engine.globals)
        (setv umkey (unmangle key))
        (when (.startswith umkey "$")
            (if (= 1 (len umkey))
                ; To-do: return the get field function.
                (return None)
            #_else (do
                (setv field-index (cut umkey 1))
                (if (.isnumeric field-index) (do
                    (setv field-index (int field-index))
                    (unless field-index 
                        (return self.--engine.buffer)))))))
        (cond
        [(in key self) 
            (.get (super) key)]
        [(in key globals) 
            (get globals key)]
        [(in key --builtins--) 
            (get --builtins-- key)]
        [True
            (setv t (TolNone))
            (assoc self key t)
            t]) ) )


(defclass Engine []
    (defn --init-- [self]
        (super-init)
        (setv self.globals {})
        (setv self.locals (TolLocals {"engine" self} self))
        (setv self.--file None)
        (setv self.buffer ""))

    (defn load-next-record [self]
        (setv file self.--file)
        (unless file (return False))
        (try
            (setv self.buffer (-> file (next) (.strip)))
        (except [StopIteration]
            (return False)))
        True)
        
    (defn run [self file code-str]
        (setv self.--file file)
        (-> code-str (translate) (eval self.locals))))
