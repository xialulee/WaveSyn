(require [wavesynlib.languagecenter.hy.numpydef [npget]])


(import [numpy [correlate r_ roots
    angle :as ∠ 
    pi    :as π]])
(import [numpy.linalg [eigh eigvals pinv lstsq]])


(import [.hyautocorrmtx [Rx autocorrelate]])

(setv ∑ sum)



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
    (setv Usig 
        (npget U 
            ALL 
            (S N-p END) ) ) 
    (setv U₀ 
        (npget Usig 
            (S 0 N-1) 
            ALL) ) 
    (setv U₁ 
        (npget Usig  
            (S 1 END) 
            ALL) ) 
    (- 
        (/ 
            (∠ (eigvals 
                (first (lstsq U₁ U₀ :rcond None) ) ) ) 
            2 π) ) )



(defn root-MUSIC [Rx p]
    "Estimate signal frequencies using root-MUSIC algorithm
Rx: auto-correlation matrix of signal;
p:  number of complex sinusoids;
return value: normalized frequencies."
    (setv [S END ALL] [slice None (slice None)]) 
    (setv [p N] [(int p) (first Rx.shape)]) 
    (setv [D U] (eigh Rx)) (comment "Eigenvalue in ascending order.")
    (setv M (- N p) ) (comment "The dimension of the noise subspace.")
    (setv Un (npget U 
        ALL
        (S 0 M) ) ) (comment "An orth base of the noise subspace.")
    (setv P 
        (∑ (gfor k (range M) 
            (autocorrelate (npget Un ALL k) ) ) ) )
    (setv roots-P (roots P))
    (setv |roots-P| (abs roots-P))
    (comment "Remove all the roots outside the unit circle.")
    (setv roots-P (get roots-P (.nonzero (<= |roots-P| 1) ) ) )
    (setv |roots-P| (abs roots-P))
    (comment "Sort the roots with respect to its distance to the unit circle.")
    (setv roots-P (get roots-P (.argsort |roots-P|)))
    (setv -p-1 (dec (- p)))
    (/ 
        (∠ (get roots-P (S -1 -p-1 -1))) 
        2 π) )