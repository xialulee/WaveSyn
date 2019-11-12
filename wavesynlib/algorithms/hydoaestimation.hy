(import [numpy [correlate r_ 
    angle :as ∠ 
    pi    :as π]])
(import [numpy.linalg [eigh eigvals pinv lstsq]])


(defn autocorrelate [x] (correlate x x :mode "full") )


(defn Rx [x &optional m]
    "Estimate autocorrelation matrix of vector x.
x: signal vector;
m: size of Rx
return value: estimated autocorrelation matrix."
    (setv S slice)
    (setv N (len x) ) 
    (if (is m None) 
        (setv m N) 
    #_else
        (raise (ValueError "The number of rows/columns of R should less than or equal to vector lenght N.") ) ) 
    (comment "generate a indices matrix, as
generate a indices matrix, as
0 -1 -2 -3 ...
1  0 -1 -2 ...
2  1  0 -1 ...
3  2  1  0 ...
...") 
    (setv indices (- 
        (get r_ (, "c" (S 0 m))) 
        (get r_ (, "r" (S 0 m))) ) ) 
    (setv ̂a (autocorrelate x) ) 
    (comment "# using autocorrelation samples and indices matrix to create Rx
Rx =
  r[ 0] r[-1] r[-2] r[-3] ...
  r[ 1] r[ 0] r[-1] r[-2] ...
  r[ 2] r[ 1] r[ 0] r[-1] ...
  r[ 3] r[ 2] r[ 1] r[ 0] ...
  ...") 
    (/ (get ̂a (+ indices N -1)) N) )


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
    (setv Usig (get U (, 
        ALL 
        (S N-p END) ) ) ) 
    (setv U₀ (get Usig (, 
        (S 0 N-1) 
        ALL ) ) ) 
    (setv U₁ (get Usig (, 
        (S 1 END) 
        ALL) ) ) 
    (- 
        (/ 
            (∠ (eigvals 
                (first (lstsq U₁ U₀ :rcond None) ) ) ) 
            2 π) ) )
