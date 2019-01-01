(import math)
(import [sympy [*]])
(import [sympy.logic.boolalg [BooleanFalse BooleanTrue]])
(import uuid)



(defn -int-to-bits [i]
    (setv ord-0 (ord "0"))
    (gfor c (cut (.format "{:b}" i) None None -1) 
        (- (ord c) ord-0) ) )



(defn -full-adder [A B Cin]
    (,
        (reduce ^ [A B Cin]) 
        (| 
            (& A B) 
            (&
                Cin 
                (^ A B) ) ) ) )



(defclass BoolVector []
    (defn --init-- [self &optional name length field-names expressions integer]
        (unless name
            (setv 
                name
                    (.format 
                        "temp_boolvector_{}" 
                        (.replace (str (uuid.uuid1)) "-" "_")) ) )
        (when (and (is-not integer None) (is length None) ) 
            (setv length (math.ceil (math.log2 integer) ) ) )
        (cond
        [length 
            (if (is integer None)
                (setv 
                    self.--symbols 
                        (lfor k (range length)
                            (Symbol (.format "{}_{}" name k)) )
                    self.--field-names
                        []) 
            #_else
                (setv 
                    self.--symbols
                        (lfor k (-int-to-bits integer)
                            (if k True #_else False) )
                    self.--field-names
                        []) )]
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

    (defn --add-- [self y]
        (setv 
            exprs []
            C     False)
        (for [[A B] (zip-longest self y :fillvalue False)]
            (setv [S C] (-full-adder A B C) ) 
            (.append exprs S) ) 
        (.append exprs C) 
        (BoolVector :expressions exprs) )

    (defn --ne-- [self y]
        (when (integer? y)
            (setv y (BoolVector :integer y) ) )
        (.any (^ self y)) )

    (defn --eq-- [self y]
        (~ (!= self y)))

    (defn --not-- [self]
        (.elementwise self ~))

    (defn elementwise [self func &optional y]
        (when (and (coll? func) (!= (len self) (len func)))
            (raise (ValueError "The function list and self should have same length.")) )
        (unless (coll? func)
            (setv func (repeat func (len self)) ) )
        (if y
            (BoolVector :expressions (gfor [f a b] (zip-longest func self y :fillvalue False) (f a b)) ) 
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
        (| #* (gfor num domain 
            (& #* (gfor [bit var] (zip-longest (-int-to-bits num) self :fillvalue False)
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

