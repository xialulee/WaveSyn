(import [vispy [app]])
(import [vispy.gloo [
    clear Program set_viewport set_clear_color]])

(import [hysldef [to-glsl]])
(require [hysldef [VertexShader FragmentShader]])



(VertexShader vert
    (attribute vec3 pos)
    (main
        (setv gl_Position (vec4 pos 1.0))))



(FragmentShader frag
    (out vec4 frag_color)
    (main
        (setv frag_color (vec4 1.0 0.5 0.2 1.0))))



(defclass Canvas [app.Canvas]
    (defn --init-- [self]
        (.--init-- (super) :title "Test HySL" :size (, 512 512))
        (setv self.program 
            (Program 
                (second (to-glsl vert))
                (second (to-glsl frag))
                3))
        (assoc self.program "pos" 
            (, 
                (, 0.0 0.5 0.0) 
                (, -0.5 -0.5 0.0) 
                (, 0.5 -0.5 0.0)))
        (set_clear_color "white")
        (.show self)
        (set_viewport 0 0 512 512))
        
    (defn on-draw [self event]
        (clear :color True :depth True)
        (.draw self.program "triangle_strip"))
        
    (defn on-resize [self event]
        (setv center (/ (complex #* self.size) 2))
        (setv size (min self.size))
        (defn calc-origin [a]
            (/ (- a size) 2))
        (set_viewport 
            (calc-origin (get self.size 0)) 
            (calc-origin (get self.size 1))
            size
            size)))



(defmain [&rest args]
    (setv canvas (Canvas))
    (.run app))
    

