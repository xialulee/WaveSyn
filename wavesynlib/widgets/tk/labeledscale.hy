(require [wavesynlib.languagecenter.hy.utils [super-init defprop]])

(import [tkinter [Frame]])
(import [tkinter.ttk [Label Scale]])


(defclass LabeledScale [Frame]
    (defn --init-- [self &rest args &kwargs kwargs]
        (setv 
            from-            (.pop kwargs "from_")
            to               (.pop kwargs "to")
            name             (.pop kwargs "name" "")
            formatter        (.pop kwargs "formatter" str)
            self.--formatter formatter)
        (super-init #* args #** kwargs)

        (.pack 
            (setx self.--name-label (Label self :text name))
            :side "left")

        (.pack 
            (setx self.--scale 
                (Scale self 
                    :from-   from- 
                    :to      to 
                    :command self.-on-change))
            :side   "left"
            :fill   "x"
            :expand "yes")

        (.pack
            (setx self.--value-label (Label self))
            :side "left"))
            
            
    (defn -on-change [self val]
        (assoc self.--value-label "text" (.--formatter self val)))
        
        
    (defn get [self]
        (.get self.--scale))
        
        
    (defn set [self val]
        (.set self.--scale val))


    (defprop name
        #_getter
        (fn [self] 
            (.get self.--name-label "text"))
        #_setter
        (fn [self val] 
            (assoc self.--name-label "text" val)))
        
        
    (defprop scale-value
        #_getter
        (fn [self] 
            (.get self))
        #_setter
        (fn [self val] 
            (.set self val))) 
            
            
    (defprop value-formatter
        #_getter
        (fn [self] 
            self.--formatter) 
        #_setter
        (fn [self val] 
            (setv self.--formatter val))))
