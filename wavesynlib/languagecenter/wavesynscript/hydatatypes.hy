(require [hy.extra.anaphoric [%]])
(require [wavesynlib.languagecenter.hy.utils [defprop dyn-setv]])



(defclass Constant []
"Constant type of wavesynscript."
    [--slots-- (, "__name" "__value" "__doc")
     --cache   {}]
    
    (defn --new-- [cls name &optional value doc]
        (if (in name cls.--cache) (do
            (setv c (. cls --cache [name]) ) 
            (if (!= value c.value) 
                (raise (ValueError "This constant has already been initialized with a different value.") ) ) 
            c) 
        #_else
            (.--new-- object cls) ) ) 
            
    (defn --init-- [self name &optional value doc]
        (unless (in name self.--cache) 
            (setv
                self.--name  name
                self.--value value
                self.--doc   doc
                (. self --cache [name]) self) ) ) 
                
    (defprop name 
        #_getter
        #%(. %1 --name) ) 
        
    (defprop value
        #_getter
        #%(. %1 --value) ) 
        
    (defprop doc
        #_getter
        #%(. %1 --doc) ) 
        
    (defn help [self] (print self.doc) ) )



(defclass Constants []
    (setv --name-value-pairs (,
        (, "KEYSYM-MODIFIERS" #{
            "Alt_L"     "Alt_R"
            "Control_L" "Control_R"
            "Shift_L"   "Shift_R" })
        (, "KEYSYM-CURSORKEYS" #{
            "KP_Prior" "KP_Next"  "KP_Home" "KP_End" 
            "KP_Left"  "KP_Right" "KP_Up"   "KP_Down" 
            "Left"     "Right"    "Up"      "Down" 
            "Home"     "End"      "Next"    "Prior"}) ) )

    (for [[name value] --name-value-pairs]
        (dyn-setv name (Constant name value) ) )
            
    #@(classmethod
    (defn append-new-constant [cls name &optional value doc]
        (setattr cls name (Constant name value doc) ) ) ) )
