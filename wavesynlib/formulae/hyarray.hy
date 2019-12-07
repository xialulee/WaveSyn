(require [wavesynlib.languagecenter.hy.utils [call=]])

(import [numpy [abs atleast-1d exp sin angle :as ∠ pi :as π]])



(defmacro ▦→┅ [v]
    `(setv (. ~v shape) (, 1 -1) ) )

(defmacro ▦→┇ [v]
    `(setv (. ~v shape) (, -1 1) ) )



(defn steering [p θ λ]
    (setv θ (-> θ (atleast-1d) (.view) ) )
    (-= p (first p.flat) ) 
    (▦→┇ p) 
    (▦→┅ θ) 
    (setv Δ (* (abs p) (sin (- θ (∠ p))) ) )
    (exp (* 2j π Δ (/ 1 λ) ) ) )

