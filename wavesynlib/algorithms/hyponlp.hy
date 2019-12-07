(require [wavesynlib.languagecenter.hy.numpydef [⇦▦ ▦⇦]])
(require [wavesynlib.formulae.hyarray [▦→┇]])
(require [wavesynlib.algorithms.hycommon [∑]])

(import [numpy.fft [
    fft  :as ℱ 
    ifft :as ℱ⁻¹]])
(import [numpy [abs diag exp 
    outer
    roll
    zeros]])



(defn 𝐔ₙ [n x]
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
    (setv 2N (* 2 N) )
    (setv F (ℱ x :n 2N ) ) 
    (ℱ⁻¹ (* F (.conj F) ) ) )


(defn objective [𝛗 Q]
    (setv |aǫ|² (-> 𝛗
        (* 1j)
        (exp)
        (autocorr)
        (get Q) 
        (abs²) ))
    (∑ |aǫ|²) )


(defn ∂aₙ/∂𝛗 [𝐬 n]
    (setv -n (- n) )
    (setv 𝐬* (.conj 𝐬) )
    (setv 𝐔ₙ𝐬 (𝐔ₙ n 𝐬) )
    (setv 𝐔ₙᵀ𝐬* (𝐔ₙ -n 𝐬*) )
    (comment "See Eq.44 in [1].")
    (setv t1 (* 1j 𝐬 𝐔ₙᵀ𝐬*) )
    (setv t2 (* -1j 𝐬* 𝐔ₙ𝐬) )
    (+ t1 t2) )


(defn gradient [𝛗 Q]
    (setv 𝐬 (exp (* 1j 𝛗) ) )
    (setv a (autocorr 𝐬) ) 
    (setv grad (
        ∑ #_< k ∈ Q #_> (do
            (setv aₖ* (-> a (get k) (.conj) ) )
            (setv ∂aₖ/∂𝛗 (∂aₙ/∂𝛗 𝐬 :n k) )
            (comment "See Eq.43 in [1].")
            (* aₖ* ∂aₖ/∂𝛗) ) ) ) 
    (* 2 grad.real) )


(defn ∂²aₙ/∂𝛗∂𝛗ᵀ [𝐬 n]
    (setv -n (- n))

    (setv Diag𝐬 (diag 𝐬) )
    (setv Diag𝐬* (.conj Diag𝐬))
    (setv 𝐔ₙDiag𝐬 (-> 𝐬 (⇦▦ ↔n:) (diag n)) )
    (setv Diag𝐔ₙ𝐬 (->> 𝐬 (𝐔ₙ n) (diag) ) )
    (setv 𝐔ₙᵀDiag𝐬* (-> 𝐬 (⇦▦ ↔0:-n) (diag -n)) )
    (setv Diag𝐔ₙᵀ𝐬* (->> 𝐬 (𝐔ₙ -n) (.conj) (diag) ) )

    (comment "See Eq.49 in [1].")
    (setv t1 (@ Diag𝐬* 𝐔ₙDiag𝐬) ) 
    (setv t2 (@ (- Diag𝐬*) Diag𝐔ₙ𝐬) ) 
    (setv t3 (@ Diag𝐬 𝐔ₙᵀDiag𝐬*) ) 
    (setv t4 (@ (- Diag𝐬) Diag𝐔ₙᵀ𝐬*) ) 
    (+ t1 t2 t3 t4) )


(defn hessian [𝛗 Q]
    (setv s (-> 𝛗 
        (* 1j) 
        (exp) ) ) 
    (setv a (autocorr s) ) 
    (setv H (
        ∑ #_< k ∈ Q #_> (do
            (setv ∂aₖ/∂𝛗 (∂aₙ/∂𝛗 s :n k) ) 
            (setv ∂²aₖ/∂𝛗∂𝛗ᵀ (∂²aₙ/∂𝛗∂𝛗ᵀ s :n k) )
            (setv aₖ* (-> a (get k) (.conj) ) )
            (comment "See Eq.48 in [1].")
            (+
                (outer ∂aₖ/∂𝛗 (.conj ∂aₖ/∂𝛗) ) 
                (* aₖ* ∂²aₖ/∂𝛗∂𝛗ᵀ) ) ) ) ) 
    (* 2 H.real) )



(comment "
[1] F.C. Li, Y.N. Zhao, X.L. Qiao. A waveform design method for suppressing
    range sidelobes in desired intervals. Signal Processing 96 (2014): 203-211.
")