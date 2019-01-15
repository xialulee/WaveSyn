(require [macros [HYHDL-INIT]])
(HYHDL-INIT)



(MODULE PriorityEncoder [
    #_output code 
    #_output valid 
    #_input inp]

    (ALWAYS-COMB
        (setv 
            valid.next (IF-EXPR inp 1 0) 
            code.next  0) 
        (AP-EACH-BIT LSB-TO-MSB inp
            (IF-STMT IT
                (setv code.next INDEX-OF-IT) ) ) ) )


