(require [wavesynlib.formulae.hyarray [TO-COLUMN]])

(import [numpy.fft [fft ifft]])
(import [numpy [abs diag exp 
    hstack
    outer
    roll
    sum :as ∑
    zeros]])



(defn shift [x d]
    (cond 
    [(zero? d) (setv x (.copy x))]
    [(pos? d) 
        (setv x (roll x d)) 
        (assoc x (slice 0 d) 0)] 
    [(neg? d) 
        (setv x (.copy x))
        (setv -d (- d))
        (assoc x (slice 0 -d) 0) 
        (setv x (roll x d))])
    x)



(defn autocorr [x]
    (setv N (len x) )
    (setv F (fft x (* N 2) ) ) 
    (ifft (* F (.conj F) ) ) )


(defn objective [φ Q]
    (setv |aǫ|² (-> φ
        (* 1j)
        (exp)
        (autocorr)
        (get Q) 
        (abs) 
        (** 2) ))
    (∑ |aǫ|²) )


(defn ∂aₙ/∂φ [s n]
    (setv [S END] [slice None])
    (setv -n (- n) )
    (setv t1 (* 1j s (-> s (shift n) (.conj) ) ) )
    (setv t2 (* -1j (.conj s) (shift s :d -n) ) )
    (+ t1 t2) )


(defn gradient [φ Q]
    (setv s (exp (* 1j φ) ) )
    (setv a (autocorr s) ) 
    (setv grad (
        ∑ (gfor k Q
            (*
                (-> a (get k) (.conj) ) 
                (∂aₙ/∂φ s :n k) ) )
        :axis 0) ) 
    (* 2 grad.real) )


(defn ∂²aₙ/∂φ² [s n]
    (setv -n (- n))
    (setv [S END] [slice None])
    (setv t1 (@
        (-> s (.conj) (diag))
        (-> s (get (S n END)) (diag n)) ) ) 
    (setv t2 (@
        (-> s (.conj) (diag) (* -1) ) 
        (-> s (shift -n) (diag) ) ) ) 
    (setv t3 (@
        (diag s) 
        (-> s (get (S 0 -n)) (diag -n) ) ) ) 
    (setv t4 (@
        (-> s (diag) (* -1) ) 
        (-> s (shift n) (.conj) (diag) ) ) ) 
    (+ t1 t2 t3 t4) )


(defn hessian [φ Q]
    (setv s (-> φ 
        (* 1j) 
        (exp) ) ) 
    (setv a (autocorr s) ) 
    (setv ∑ sum)
    (setv H (
        ∑ (gfor k Q
            (do
                (setv d (∂aₙ/∂φ s :n k) ) 
                (+
                    (outer d (.conj d) ) 
                    (* 
                        (-> a (get k) (.conj))
                        (∂²aₙ/∂φ² s :n k) ) ) ) ) ) ) 
    (* 2 H.real) )
