(import [sympy [*]])
(import [sympy.logic.boolalg [BooleanFalse BooleanTrue]])
(import uuid)



(defclass BoolVector []
    (defn --init-- [self &optional name length field-names expressions]
        (unless name
            (setv 
                name
                    (.format 
                        "temp_boolvector_{}" 
                        (.replace (str (uuid.uuid1)) "-" "_")) ) )
        (cond
        [length 
            (setv 
                self.--symbols 
                    (lfor k (range length)
                        (Symbol (.format "{}_{}" name k)) )
                self.--field-names
                    [])]
        [expressions
            (setv 
                self.--symbols     (list expressions)
                self.--field-names [])]
        [field-names
            (setv 
                self.--symbols
                    (lfor field-name field-names
                        (Symbol (.format "{}_{}" name field-name)) ) 
                self.--field-names field-names)]) )

    (defn --len-- [self]
        (len self.--symbols))

    (defn --iter-- [self]
        (iter self.--symbols))

    (defn --getitem-- [self n]
        (cond
        [(integer? n)
            (. self --symbols [n])]
        [(keyword? n)
            (get self.--symbols (.index self.--field-names (name n)))]
        [(string? n)
            (get self.--symbols (.index self.--field-names n))]
        [True
            (raise IndexError)]) )

    (defn --and-- [self y]
        (.elementwise self & y))

    (defn --xor-- [self y]
        (.elementwise self ^ y))

    (defn --or-- [self y]
        (.elementwise self | y))

    (defn --ne-- [self y]
        (.any (^ self y)) )

    (defn --eq-- [self y]
        (~ (!= self y)))

    (defn --not-- [self]
        (.elementwise self ~))

    (defn elementwise [self func &optional y]
        (when (and (coll? func) (!= (len self) (len func)))
            (raise (ValueError "The function list and self should have same length.")) )
        (when (and y (!= (len self) (len y)))
            (raise (ValueError "The two vectors should have same length.")) )

        (unless (coll? func)
            (setv func (repeat func (len self)) ) )
        (if y
            (BoolVector :expressions (gfor [f a b] (zip func self y) (f a b)) ) 
        #_else
            (BoolVector :expressions (gfor [f a] (zip func self) (f a) ))) )

    (defn any [self] 
        (| #* self.--symbols) )

    (defn card [self n]
        (setv length (len self))
        (| #* (gfor comb (combinations (range length) n) 
            (& #* (gfor [index symbol] (enumerate self.--symbols)
                (if (in index comb)
                    symbol
                #_else
                    (~ symbol) ) ) ) ) ) ) 
                    
    (defn within-domain [self domain]
        (setv ord-0 (ord "0"))
        (setv fstr (.join "" ["{:0" (str (len self)) "b}"]))
        (defn chr-to-num [chr]
            (- (ord chr) ord-0) )
        (defn reverse [s]
            (cut s None None -1) )
        (defn binlist [num]
            (gfor bit (reverse (.format fstr num)) 
                (chr-to-num bit) ) )
        (| #* (gfor num domain 
            (& #* (gfor [bit var] (zip (binlist num) self)
                (if bit
                    var
                #_else
                    (~ var) ) ) ) ) ) ) 

    (defn different-from [self &rest others]
        (& #* (gfor other others 
            (!= self other) ) ) )
                    
    (defn subs [self d &optional output-format]
        (setv result (gfor item self 
            (.subs item d) ) ) 
        (defn convert-int [v]
            (cond
            [(instance? BooleanFalse v) 0]
            [(instance? BooleanTrue v)  1]
            [True (raise (ValueError "Cannot convert to int."))]))
        (cond
        [(= output-format int)
            (+ #* (gfor [power item] (enumerate result) 
                (if (convert-int item) 
                    (** 2 power) 
                #_else
                    0) ))]
        [(= output-format None)
            (BoolVector :expressions result)]) ) ) 



(defn all-different [&rest args]
    (& #* (gfor [x y] (combinations args 2)
        (!= x y) ) ) )

