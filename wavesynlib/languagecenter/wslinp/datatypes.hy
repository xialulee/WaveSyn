(require [wavesynlib.languagecenter.hy.utils [super-init]])


(defclass TolNone []
    (defn --init-- [self]
        (super-init) ) 

    (defn --op [self op other &optional right]
        (setv value
            (cond
            [(numeric? other)
                0]
            [(string? other)
                ""]
            [True (raise (TypeError "Type not supported."))]) ) 
        (if right (op other value) (op value other)))
        
    (defn --add-- [self other]
        (.--op self + other)) 
        
    (defn --radd-- [self other]
        (.--op self + other :right True)) 
        
    (defn --sub-- [self other]
        (.--op self - other)) 
        
    (defn --rsub-- [self other]
        (.--op self - other :right True)) 
        
    (defn --mul-- [self other]
        (.--op self * other)) 
        
    (defn --rmul-- [self other]
        (.--op self * other :right True)) 
        
    (defn --truediv-- [self other]
        (.--op self / other)) 
        
    (defn --rtruediv-- [self other]
        (.--op self / other :right True)) 
        
    (defn --floordiv-- [self other]
        (.--op self // other)) 
    
    (defn --rfloordiv-- [self other]
        (.--op self // other :right True)) 
        
    (defn --mod-- [self other]
        (.--op self % other)) 
        
    (defn --rmod-- [self other]
        (.--op self % other :right True)) )


(defclass TolLocals [dict]
    (defn --init-- [self kwargs globals]
        (setv self.--globals globals)
        (super-init #** kwargs))
        
    (defn --getitem-- [self key]
        (cond
        [(in key self) 
            (get self key)]
        [(in key globals) 
            (get globals key)]
        [(in key --builtins--) 
            (get --builtins-- key)]
        [True
            (setv t (TolNone))
            (assoc self key t)
            t]) ) )
