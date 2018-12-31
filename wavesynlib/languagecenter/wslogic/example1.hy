(require [macros [defvars]])

(import [sympy [*]])
(import [sympy.logic.inference [satisfiable]])
(import [hydef [BoolVector]])



(defmain [&rest args]
    (defvars A B C D)
    ; We have four suspects A, B, C, and D.
    ; A = True means A is the criminal. 
    (setv suspects (BoolVector :expressions [A B C D]))
    ; The statements of these four suspects are:
    ; A: I am not guilty.
    ; B: D is guilty.
    ; C: B is guilty.
    ; D: B is lying.
    (setv statements (BoolVector :expressions [(~ A) D B (~ D)])) 
    (print 
        (list 
            (satisfiable 
                (& 
                    ; Only one of them is guilty.
                    (.card suspects 1) 
                    ; Only one statement is True.
                    (.card statements 1)) 
                :all-models True)) ) )


