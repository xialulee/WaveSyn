(require [hy.extra.anaphoric [*]])
(import math)



(setv constant-dict (dict
    :pi math.pi))



(defmacro VertexShader [name &rest args]
    `(setv ~name (dict
        :objtype "vertex shader"
        :expr-coll (quote ~args))))



(defmacro FragmentShader [name &rest args]
    `(setv ~name (dict
        :objtype "fragment shader"
        :expr-coll (quote ~args))))



(defmacro Function [rettype name args &rest expr-coll]
    `(setv ~name (dict 
        :objtype "function"
        :rettype (quote ~rettype)
        :name (quote ~name)
        :args (quote ~args)
        :expr-coll (quote ~expr-coll))))



(defn translate-expr [indent expr]
    (setv [head tail] [(-> expr first str) (rest expr)])
    (setv func (.get dispatch-dict head (fn [indent args] (translate-call indent args head))))
    (func indent tail))



(defn translate-expr-coll [indent expr-coll]
    (setv code-list [])
    (for [expr expr-coll]
        (.append code-list (translate-expr indent expr)))
    (.join "\n" code-list))



(defn translate-call [indent args func-name]
    (setv code-list [])
    (for [arg args]
        (.append code-list
            (if (coll? arg)
                (translate-expr 0 arg)
            #_else
                (str arg))))
    (.format "{}{}({})"
        (* " " indent)
        func-name
        (.join ", " code-list)))



(defn translate-arithmetic [indent args op]
    (setv code-list [])
    (for [expr args]
        (.append code-list
            (if (coll? expr)
                (.format "({})" (translate-expr 0 expr))
            #_else
                (str expr))))
    (.format "{}({})"
        (* " " indent)
        (.join op code-list)))



(defn translate-comp [indent args op]
    (setv args (list args))
    (setv middle (cut args 1 -1))
    (setv middle (flatten (zip middle middle)))
    (setv args (flatten [
        (first args)
        middle
        (last args)]))
    (setv code-list [])
    (for [[left right] (partition args)]
        (.append code-list (.format "({} {} {})" left op right)))
    (.format "({})" (.join " && " code-list)))



(defn translate-var [indent args]
    (setv code-list [])
    (for [[type- name] (partition args)]
        (setv initval (if (coll? name)
            (+ " = " (if (coll? (second name))
                (translate_expr 0 (second name))
                (str (second name))))
            ""))
        (setv name (if (coll? name) (first name) name))
        (.append code-list (.format "{}{} {}{};" (* " " indent) type- name initval)))
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



(defn translate-constant [indent args]
    (setv arg (-> args first str))
    (str (get constant-dict arg)))



(defn translate-main [indent expr-coll]
    (setv code-list [(+ (* " " indent) "void main(){")])
    (.append code-list (translate-expr-coll (+ indent 4) expr-coll))
    (.append code-list (+ (* " " indent) "}"))
    (.join "\n" code-list))



(defn translate-hashdefine [indent args]
    (setv [name expr] args)
    (if (coll? expr)
        (.format "{}#define {} {}" (* " " indent) name (translate-expr 0 expr))
    #_else
        (.format "{}#define {} {}" (* " " indent) name expr)))



(defn translate-return [indent arg]
    (setv expr (first arg))
    (if (coll? expr)
        (setv expr-str (translate-expr 0 expr))
    #_else
        (setv expr-str (str expr)))
    (.format "{}return {};" (* " " indent) expr-str))



(defn translate-if [indent args]
    (setv code-list [])
    (setv args (list args))
    (if (= (len args) 2) (.append args None))
    (setv [condition expr-true expr-false] args)
    (if (coll? condition)
        (setv condstr (.format "if ({}){{" (translate-expr 0 condition)))
    #_else
        (setv condstr (.format "if ({}){{" (str condition))))
    (setv condstr (+ (* " " indent) condstr))
    (.append code-list condstr)
    (setv newindent (+ indent 4))
    (.append code-list (translate-expr newindent expr-true))
    (if expr-false (do
        (.append code-list (.format "{}}}else{{" (* " " indent)))
        (.append code-list (translate-expr newindent expr-false))
        (.append code-list (.format "{}}}" (* " " indent))))
    #_else   
        (.append code-list (.format "{}}}" (* " " indent))))
    (.join "\n" code-list))



(setv dispatch-dict {
    "attribute" (fn [indent args] (translate-pipe-vars indent args "attribute"))
    "uniform"   (fn [indent args] (translate-pipe-vars indent args "uniform"))
    "input"     (fn [indent args] (translate-pipe-vars indent args "in"))
    "output"    (fn [indent args] (translate-pipe-vars indent args "out"))
    "var"       translate-var
    "constant"  translate-constant
    "@define"   translate-hashdefine
    "vec2"      (fn [indent args] (translate-vec indent args "2" ""))
    "vec3"      (fn [indent args] (translate-vec indent args "3" ""))
    "vec4"      (fn [indent args] (translate-vec indent args "4" ""))
    "setv"      translate-setv
    "+"         (fn [indent args] (translate-arithmetic indent args " + "))
    "-"         (fn [indent args] (translate-arithmetic indent args " - "))
    "*"         (fn [indent args] (translate-arithmetic indent args " * "))
    "/"         (fn [indent args] (translate-arithmetic indent args " / "))
    "<"         (fn [indent args] (translate-comp indent args " < "))
    "<="        (fn [indent args] (translate-comp indent args " <= "))
    ">"         (fn [indent args] (translate-comp indent args " > "))
    ">="        (fn [indent args] (translate-comp indent args " >= "))
    "="         (fn [indent args] (translate-comp indent args " == "))
    "!="        (fn [indent args] (translate-comp indent args " != "))
    "return"    translate-return
    "if"        translate-if
    "main"      translate-main})



(defn to-glsl [codeobj]
    (setv code-list [])
    (cond 
        [(= (get codeobj "objtype") "function")
            (setv arg-list [])
            (for [[type- name] (partition (get codeobj "args"))]
                (arg-list.append (.format "{} {}" type- name)))
            (.append code-list 
                (.format "{} {}({}){{" 
                    (get codeobj "rettype")
                    (get codeobj "name")
                    (.join ", " arg-list)))
            (.append code-list
                (translate-expr-coll 4 (get codeobj "expr_coll")))
            (.append code-list "}")
            (return (.join "\n" code-list))]
        [(in (get codeobj "objtype") ["vertex shader" "fragment shader"])
            (.append code-list "#version 420\n")
            (.append code-list (translate-expr-coll 0 (get codeobj "expr_coll")))
            (return (.join "\n" code-list))]
        ))



(defmain [&rest args]
    (VertexShader vert 
        (attribute 
            vec3 pos 
            vec4 color)
        (main
            (var float [d (distance x y)])
            (setv gl_Position (vec4 pos 1.0))))
    (print (to-glsl vert))
    
    (FragmentShader frag
        (@define PI (constant pi))
        (output vec4 frag_color)
        (main
            (setv frag_color (vec4 1.0 0.5 0.2 1.0))))
    (print (to-glsl frag))
    
    (Function float hit_circle [vec2 xy vec2 center float radius float tol]
        (var 
            float [d (distance center xy)]
            float [lower (- radius tol)]
            float [upper (+ radius tol)])
        (if (<= lower d upper)
            (return (/ (- tol (abs (- d radius))) tol))
        #_else
            (return 0)))
    (print (to-glsl hit_circle)))

