(require [hy.extra.anaphoric [*]])


(defmacro VertexShader [name &rest args]
    (setv code ["vertex shader" args])
    `(setv ~name (quote ~code)))



(defmacro FragmentShader [name &rest args]
    (setv code ["fragment shader" args])
    `(setv ~name (quote ~code)))



(defn translate-expr [indent expr]
    (setv [head tail] [(-> expr first str) (rest expr)])
    (setv func (get dispatch-dict head))
    (func indent tail))



(defn translate-expr-coll [indent expr-coll]
    (setv code-list [])
    (for [expr expr-coll]
        (.append code-list (translate-expr indent expr)))
    (.join "\n" code-list))



(defn translate-pipe-vars [indent args prefix]
    (setv var-list [])
    (for [[type- name] (partition args)]
        (.append var-list (.format "{}{} {} {};" (* " " indent) prefix type- name)))
    (.join "\n" var-list))



(defn translate-setv [indent args]
    (setv code-list [])
    (for [[name value] (partition args)]
        (if (coll? value)
            (setv value (translate-expr 0 value)))
        (.append code-list (.format "{}{} = {};" (* " " indent) name value)))
    (.join "\n" code-list))



(defn translate-vec [indent args dimension type-]
    (setv suffix 
        (cond
            [(= type- "") "f"]))
    (setv args (list args))
    (for [[idx arg] (enumerate args)]
        (if (instance? float arg)
            (assoc args idx (.format "{}{}" arg suffix))))
    (.format "{}{}{}({})" 
        "vec" 
        dimension 
        type- 
        (.join ", " args)))



(defn translate-main [indent expr-coll]
    (setv code-list [(+ (* " " indent) "void main(){")])
    (.append code-list (translate-expr-coll (+ indent 4) expr-coll))
    (.append code-list (+ (* " " indent) "}"))
    (.join "\n" code-list))



(setv dispatch-dict {
    "attribute" (fn [indent args] (translate-pipe-vars indent args "attribute"))
    "out"       (fn [indent args] (translate-pipe-vars indent args "out"))
    "vec3"      (fn [indent args] (translate-vec indent args "3" ""))
    "vec4"      (fn [indent args] (translate-vec indent args "4" ""))
    "setv"      translate-setv
    "main"      translate-main})



(defn to-glsl [code]
    (setv shader-type (first code))
    (setv code-str (translate-expr-coll 0 (second code)))
    (setv code-str (+ "#version 420\n" code-str))
    [shader-type code-str])



(defmain [&rest args]
    (VertexShader vert 
        (attribute 
            vec3 pos 
            vec4 color)
        (main
            (setv gl_Position (vec4 pos 1.0))))
    (print (second (to-glsl vert)))
    
    (FragmentShader frag
        (out vec4 frag_color)
        (main
            (setv frag_color (vec4 1.0 0.5 0.2 1.0))))
    (print (second (to-glsl frag))))

