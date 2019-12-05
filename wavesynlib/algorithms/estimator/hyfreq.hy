(require [wavesynlib.languagecenter.hy.numpydef [npget getrows getcols]])
(require [wavesynlib.languagecenter.hy.utils [call=]])
(require [wavesynlib.algorithms.hycommon [∑]])


(import [numpy [array arange correlate r_ 
    roots trace atleast-1d exp zeros eye
    unravel-index einsum full
    inf   :as ∞
    angle :as ∠ 
    pi    :as π]])
(import [numpy.linalg [eigh eigvals pinv lstsq det]])
(import [itertools [combinations]])

(import [.hyautocorrmtx [Rx autocorrelate]])



(defn LS-ESPRIT [Rx p]
    "Estimate signal frequencies using LS-ESPRIT algorithm
Rx: autocorrelation matrix of signal;
p:   number of complex sinusoids;
return value: normalized frequencies."
    (setv [S END ALL] [slice None (slice None)]) 
    (setv [p N] [(int p) (first Rx.shape)] ) 
    (setv [N-p N-1] [(- N p) (dec N)])
    (setv [D U] (eigh Rx) ) 
    (comment "Obtain signal subspace from U
Unlike numpy.linalg.svd, 
the eigenvalue and the corresponding eigenvectors 
calculated by eigh are in ascending order. ")
    (setv Uₛ (getcols U (S N-p END)))
    (setv U₀ (getrows Uₛ (S 0 N-1) ) )
    (setv U₁ (getrows Uₛ (S 1 END) ) )
    (setv U₁\U₀ (first (lstsq U₁ U₀ :rcond None) ) )
    (- 
        (/ 
            (∠ (eigvals U₁\U₀) ) 
            2 π) ) )



(defn root-MUSIC [Rx p]
    "Estimate signal frequencies using root-MUSIC algorithm
Rx: auto-correlation matrix of signal;
p:  number of complex sinusoids;
return value: normalized frequencies."
    (setv [S END ALL] [slice None (slice None)]) 
    (setv [p N] [(int p) (first Rx.shape)]) 
    (setv [D U] (eigh Rx)) (comment "Eigenvalue in ascending order.")
    (setv N-p (- N p) ) (comment "The dimension of the noise subspace.")
    (comment "An orth base of the noise subspace.")
    (setv Uₙₒᵢₛₑ (getcols U (S 0 N-p) ) ) 
    (setv P (
        ∑ #_< u ∈ Uₙₒᵢₛₑ.T #_> (autocorrelate u) ) ) 
    (setv roots-P (roots P))
    (setv |roots-P| (abs roots-P))
    (comment "Remove all the roots outside the unit circle.")
    (setv roots-P (get roots-P (.nonzero (<= |roots-P| 1) ) ) )
    (setv |roots-P| (abs roots-P))
    (comment "Sort the roots with respect to its distance to the unit circle.")
    (setv roots-P (get roots-P (.argsort |roots-P|)))
    (setv -p-1 (- 0 p 1) )
    (/ 
        (∠ (get roots-P (S -1 -p-1 -1))) 
        2 π) )



(defn MLE [Rx p &optional [freq-samps (arange 0 1 0.01)]]
    (setv [S END ALL] [slice None (slice None)]) 
    (setv [p N Nf] [(int p) (first Rx.shape) (len freq-samps)])
    (setv I (eye N))
    (defn Es [freqs]
        "Create a steering matrix."
        (call= freqs atleast-1d) 
        (setv n (npget r_ "c" (S 0 N)))
        (setv ω (* 2 π freqs))
        (exp (* 1j n ω)) ) 
    (setv F (full (* [Nf] p) ∞))
    (for [idx (combinations (range Nf) p)]
        (setv A (->> idx (array) (get freq-samps) (Es) ) )
        (setv A† (pinv A))
        (setv Pᴀ (@ A A†))
        (setv Pɴ (- (eye (first Pᴀ.shape)) Pᴀ))
        (setv N-p (- N p))
        (setv σ² 
            (. (/ 
                    (einsum "ij,ji->" Pɴ Rx) ; tr(PN@Rx)
                    N-p)
            real) )
        (setv σ²I (* σ² I))
        (setv Rs (@ A† (- Rx σ²I) A†.H))
        (assoc F idx
            (. (det (+ (@ A Rs A.H) σ²I) ) real)) )
    (setv sub (-> (.argmin F) 
        (unravel-index F.shape) 
        (array)))
    (get freq-samps sub) )
