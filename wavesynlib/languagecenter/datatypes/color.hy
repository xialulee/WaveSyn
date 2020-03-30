(import colorsys)



(defclass WaveSynColor []
    (defn --init-- [self &optional rgb yiq hls hsv]
        (when rgb 
            (setv self.--rgb rgb) 
            (return))
        (when yiq 
            (setv self.--rgb (colorsys.yiq_to_rgb #* yiq))
            (return))
        (when hls 
            (setv self.--rgb (colorsys.hls_to_rgb #* hls))
            (return))
        (when hsv
            (setv self.--rgb (colorsys.hsv_to_rgb #* hsv))
            (return)))
            
    (defn to-hexstr [self]
        (.format
            "#{:02x}{:02x}{:02x}"
            #*
            (gfor x self.--rgb (int (* x 255)))))
            
    (defn to-tk [self]
        (.to-hexstr self))
        
    (defn to-matplotlib [self]
        self.--rgb)
        
    (defn from-photoshop-hsv [self hsv]
        (setv H (/ (get hsv 0) 360) ) 
        (setv S (/ (get hsv 1) 100) )
        (setv V (/ (get hsv 2) 100) ) 
        (setv self.--rgb (colorsys.hsv-to-rgb H S V) ) 
        self) 
        
    (defn to-photoshop-hsv [self]
        (setv hsv (colorsys.rgb-to-hsv self.--rgb))
        (setv H (int (* (get hsv 0) 360)) )
        (setv S (int (* (get hsv 1) 100)) ) 
        (setv V (int (* (get hsv 2) 100)) ) 
        (, H S V)) )

    