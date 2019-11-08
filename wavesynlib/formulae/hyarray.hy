(import [numpy [abs exp sin angle :as ∠ pi :as π]])



(defmacro TO-ROW [v]
    `(setv (. ~v shape) (, 1 -1) ) )

(defmacro TO-COLUMN [v]
    `(setv (. ~v shape) (, -1 1) ) )



(defn steering [p θ λ]
    (-= p (first p.flat) ) 
    (TO-COLUMN p) 
    (TO-ROW θ) 
    (setv Δ (* (abs p) (sin (- θ (∠ p))) ) )
    (exp (* 2j π Δ (/ 1 λ) ) ) )

