(import [hydef [BoolVector -pycosat-itersolve]])
(import [sympy.logic.inference [satisfiable]])
(import [pycosat [itersolve]])


(defmain [&rest args]
    (setv 
        Alabama     (BoolVector :length 2)
        Mississippi (BoolVector :length 2)
        Georgia     (BoolVector :length 2)
        Tennessee   (BoolVector :length 2)
        Florida     (BoolVector :length 2))

    (setv expr (&
        (.different-from Florida Georgia Alabama)
        (.different-from Georgia Florida Tennessee Alabama)
        (.different-from Tennessee Mississippi Alabama Georgia)
        (.different-from Alabama Tennessee Mississippi Florida Georgia)
        (.different-from Mississippi Tennessee Alabama)
        #* 
        (gfor state [Alabama Mississippi Georgia Tennessee Florida]
            (.within-domain state [0 1 2]) ) ) )

    (for [result (-pycosat-itersolve expr)]
        (print
            "Alabama"     (.subs Alabama result int) 
            "Mississippi" (.subs Mississippi result int)
            "Georgia"     (.subs Georgia result int)
            "Tennessee"   (.subs Tennessee result int)
            "Florida"     (.subs Florida result int) ) ) )
        
