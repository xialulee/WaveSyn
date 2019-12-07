(require [wavesynlib.languagecenter.hy.numpydef [⇦▦ ▦⇦]])
(require [wavesynlib.formulae.hyarray [TO-COLUMN]])
(require [wavesynlib.algorithms.hycommon [∑]])

(import [numpy.fft [fft ifft]])
(import [numpy [abs diag exp 
    outer
    roll
    zeros]])



(defn Uₙ [n x]
"The upper shift operator. See Eq.8 in [1]."
    (setv n (- n))
    (cond 
    [(zero? n) (setv x (.copy x))]
    [(pos? n) 
        (setv x (roll x n)) 
        (▦⇦ x ↔0:n 0) ] 
    [(neg? n) 
        (setv x (.copy x))
        (setv -n (- n))
        (▦⇦ x ↔0:-n 0)
        (setv x (roll x n))])
    x)



(defn abs² [x]
    (+ (** x.real 2) (** x.imag 2) ) )



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
        (abs²) ))
    (∑ |aǫ|²) )


(defn ∂aₙ/∂φ [s n]
    (setv -n (- n) )
    (setv s* (.conj s) )
    (setv Uₙs (Uₙ n s) )
    (setv Uₙᵀs* (Uₙ -n s*) )
    (comment "See Eq.44 in [1].")
    (setv t1 (* 1j s Uₙᵀs*) )
    (setv t2 (* -1j s* Uₙs) )
    (+ t1 t2) )


(defn gradient [φ Q]
    (setv s (exp (* 1j φ) ) )
    (setv a (autocorr s) ) 
    (setv grad (
        ∑ #_< k ∈ Q #_> (do
            (setv aₖ* (-> a (get k) (.conj) ) )
            (setv ∂aₖ/∂φ (∂aₙ/∂φ s :n k) )
            (comment "See Eq.43 in [1].")
            (* aₖ* ∂aₖ/∂φ) ) ) ) 
    (* 2 grad.real) )


(defn ∂²aₙ/∂φ∂φᵀ [s n]
    (setv -n (- n))
    (setv [S END] [slice None])

    (setv Diag_s (diag s) )
    (setv Diag_s* (.conj Diag_s))
    (setv UₙDiag_s (-> s (⇦▦ ↔n:) (diag n)) )
    (setv Diag_Uₙs (->> s (Uₙ n) (diag) ) )
    (setv UₙᵀDiag_s* (-> s (⇦▦ ↔0:-n) (diag -n)) )
    (setv Diag_Uₙᵀs* (->> s (Uₙ -n) (.conj) (diag) ) )

    (comment "See Eq.49 in [1].")
    (setv t1 (@ Diag_s* UₙDiag_s) ) 
    (setv t2 (@ (- Diag_s*) Diag_Uₙs) ) 
    (setv t3 (@ Diag_s UₙᵀDiag_s*) ) 
    (setv t4 (@ (- Diag_s) Diag_Uₙᵀs*) ) 
    (+ t1 t2 t3 t4) )


(defn hessian [φ Q]
    (setv s (-> φ 
        (* 1j) 
        (exp) ) ) 
    (setv a (autocorr s) ) 
    (setv H (
        ∑ #_< k ∈ Q #_> (do
            (setv ∂aₖ/∂φ (∂aₙ/∂φ s :n k) ) 
            (setv ∂²aₖ/∂φ∂φᵀ (∂²aₙ/∂φ∂φᵀ s :n k) )
            (setv aₖ* (-> a (get k) (.conj) ) )
            (comment "See Eq.48 in [1].")
            (+
                (outer ∂aₖ/∂φ (.conj ∂aₖ/∂φ) ) 
                (* aₖ* ∂²aₖ/∂φ∂φᵀ) ) ) ) ) 
    (* 2 H.real) )



(comment "
[1] F.C. Li, Y.N. Zhao, X.L. Qiao. A waveform design method for suppressing
    range sidelobes in desired intervals. Signal Processing 96 (2014): 203-211.
")