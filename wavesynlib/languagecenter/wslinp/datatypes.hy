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

    (defn --bool-- [self]
        False)

    (defn --str-- [self]
        "")
        
    (defn --add-- [self other]
        (.--op self + other)) 
        
    (defn --radd-- [self other]
        (.--op self + other :right True)) 

    (defn --iadd-- [self other]
        (.--add-- self other))
        
    (defn --sub-- [self other]
        (.--op self - other)) 
        
    (defn --rsub-- [self other]
        (.--op self - other :right True)) 

    (defn --isub-- [self other]
        (.--sub-- self other))
        
    (defn --mul-- [self other]
        (.--op self * other)) 
        
    (defn --rmul-- [self other]
        (.--op self * other :right True)) 

    (defn --imul-- [self other]
        (.--mul-- self other))

    (defn --pow-- [self other]
        (.--op self ** other))

    (defn --rpow-- [self other]
        (.--op self ** other :right True))

    (defn --ipow-- [self other]
        (.--pow-- self other))
        
    (defn --truediv-- [self other]
        (.--op self / other)) 
        
    (defn --rtruediv-- [self other]
        (.--op self / other :right True)) 

    (defn --itruediv-- [self other]
        (.--truediv-- self other))
        
    (defn --floordiv-- [self other]
        (.--op self // other)) 
    
    (defn --rfloordiv-- [self other]
        (.--op self // other :right True)) 

    (defn --ifloordiv-- [self other]
        (.--floordiv-- self other))
        
    (defn --mod-- [self other]
        (.--op self % other)) 
        
    (defn --rmod-- [self other]
        (.--op self % other :right True)) 
        
    (defn --imod-- [self other]
        (.--mod-- self other)))

