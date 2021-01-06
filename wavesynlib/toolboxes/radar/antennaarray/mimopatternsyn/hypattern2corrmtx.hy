(require [wavesynlib.languagecenter.hy.numpydef [
    init-numpydef 
    ↕ ↔
    ┇
    ⇦▦]])
(init-numpydef)

(import [wavesynlib.languagecenter.hy.numpydef [‖v]])
(require [wavesynlib.formulae.hyarray [▦→┅ ▦→┇]])
(require [wavesynlib.algorithms.hycommon [∑]])


(import [numpy [
    complex :as ℂ
    zeros atleast-1d real
    sin exp radians kron outer
    pi :as π]])

(import [cvxpy :as cp])

(import [itertools [
    combinations_with_replacement
    product]])

(setv jπ (* 1j π))


(defn matA [M θ]
"Make steering matrix.
M: The number of array elements.
θ: The angle samples (°)."
    (setv S slice)
    (setv θ (-> θ 
        (atleast-1d)
        (.view)
        (radians)))
    (▦→┅ θ)
    (setv sinθ (sin θ))
    (exp (* jπ #↕[0:M] sinθ)) )



(defn matP [M]
"Return a complex M²xM² permutation matrix which satisfies vec(R)=Jr.
M: The number of array elements."
    (setv M² (* M M))
    (setv M²xM² (, M² M²))
    (setv P (zeros M²xM² ℂ))

    (setv k 0)
    (setv addr-table {})
    (for [[q p] (combinations_with_replacement (range M) 2)]
        (assoc addr-table (, p q) k) 
        (+= k (if (= p q) 1 2) ) )

    (for [[q p] (product (range M) :repeat 2)]
        (setv row (+ (* q M) p))
        (setv addr (get addr-table (, (max p q) (min p q) ) ) )
        (setv addr+1 (inc addr))
        (if (= p q)
            (assoc P (, row addr) 1)
        #_else (do
            (assoc P (, row addr) 1) 
            (assoc P (, row addr+1) (if (> p q) 1j -1j) ) ) ) )
    P)



(defn matG [M angles magnitude]
    (setv N (len angles) )
    (setv A (matA M angles) ) 
    (setv P (matP M) ) 
    (setv G (
        ∑ #_< [a m] ∈ (zip A.T magnitude) #_> (do
            (▦→┇ a)
            (setv t (->> a
                (.conj) 
                (kron a) 
                (@ P.T) 
                (-) ) ) 
            (setv g #┇[m t])
            (. (outer g g) real) ) ) ) 
    (/ G N) )



(defn corrmtx2pattern [R angles]
    (setv Nₐ (len angles))
    (setv M (first R.shape) ) 
    (setv A (matA M angles) ) 
    (setv p (. (‖v A :weight R) real) )
    (/ p (max p) ) )



(defn make-problem [M Gamma]
    (setv ⪰ >>) ; Denote semi-definite
    (setv Γ Gamma) 
    (setv P (matP M) ) 
    (setv MxM (, M M) )
    (setv M²+1 (inc (* M M) ) )
    (setv R (cp.Variable MxM :hermitian True) ) 
    (setv ρ (cp.Variable (, M²+1) ) ) 
    (setv α (first ρ) ) 
    (setv r (get ρ (slice 1 None) ) )
    (setv ρᴴΓρ (cp.quad-form ρ Γ) )
    (, 
        (cp.Problem 
            (cp.Minimize ρᴴΓρ) 
            #_s.t. [
                (⪰ R 0)
                (>= α 0)
                (= (cp.vec R) (@ P r) ) 
                (-> R (cp.real) (cp.diag) (= 1) )]) 
        R) )
