(defn text-decoration [text arg]
    (setv arg (str arg))
    (setv deco {
        "strikethrough" "\u0335"
        "overline"      "\u0305"
        "underline"     "\u0332"})
    (.join "" 
        (interleave 
            text 
            (* (get deco arg) (len text) ) ) ) )


