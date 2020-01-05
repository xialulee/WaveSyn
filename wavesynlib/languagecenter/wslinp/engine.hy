(require [wavesynlib.languagecenter.hy.utils [super-init]])

(import [.datatypes [TolNone]])
(import [.translator [translate]])


(defclass TolLocals [dict]
    (defn --init-- [self kwargs engine]
        (setv self.--engine engine)
        (super-init #** kwargs))

    (defn --setitem-- [self key value]
        (setv engine self.--engine)
        (if (in key engine.linp-builtins) (do
            (assoc engine.linp-builtins key value))
        #_else (do
            (.--setitem-- (super) key value))))
        
    (defn --getitem-- [self key]
        (setv engine self.--engine)
        (setv globals engine.globals)
        (setv umkey (unmangle key))
        (when (.startswith umkey "$")
            (if (= 1 (len umkey))
                (return engine.get-field)
            #_else (do
                (setv field-index (cut umkey 1))
                (if (.isnumeric field-index) (do
                    (setv field-index (int field-index))
                    (unless field-index 
                        (return self.--engine.buffer))
                    (try
                        (return (get self.--engine.fields (dec field-index)))
                    (except [IndexError]
                        (return ""))))
                #_else (do
                    (setv field-index (+ 0 (get self field-index)))
                    (return (.get-field engine field-index)))))))
        (cond
        [(in key self) 
            (.get (super) key)]
        [(in key engine.linp-builtins)
            (.get engine.linp-builtins key)]
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
        (setv self.linp-builtins {
            "NF"  0
            "NR"  0
            "OFS" " "
            "ORS" "\n"
            "print" (fn [&rest args &kwargs kwargs]
                (setv sep (.get kwargs "sep" (.get self.linp-builtins "OFS")))
                (setv end (.get kwargs "end" (.get self.linp-builtins "ORS")))
                (print #* args :sep sep :end end))            
            "printf" (fn [fmt &rest args]
                (print (% fmt args) :end ""))})
        (setv self.locals (TolLocals {"engine" self} self))
        (setv self.file None)
        (setv self.buffer "")
        (setv self.fields []))

    (defn load-next-record [self]
        (setv file self.file)
        (unless file (return False))
        (try
            (setv self.buffer (-> file (next) (.strip)))
            (setv self.fields (.split self.buffer))
            (assoc self.linp-builtins "NF" (len self.fields))
            (+= (. self linp-builtins ["NR"]) 1)
        (except [StopIteration]
            (return False)))
        True)

    (defn get-field [self key]
        (unless key
            (return self.buffer))
        (try
            (return (get self.fields (dec key)))
        (except [IndexError]
            (return ""))))
        
    (defn run [self code-str file]
        (setv self.file file)
        (assoc self.linp-builtins "NR" 0)
        (-> code-str (translate) (eval self.locals))))
