
(require [wavesynlib.languagecenter.hy.numpydef [npget]])

(import [numpy [correlate r_]])


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
        (npget r_ "c" (S 0 m))
        (npget r_ "r" (S 0 m)) ) ) 
    (setv ̂a (autocorrelate x) ) 
    (comment "# using autocorrelation samples and indices matrix to create Rx
Rx =
  r[ 0] r[-1] r[-2] r[-3] ...
  r[ 1] r[ 0] r[-1] r[-2] ...
  r[ 2] r[ 1] r[ 0] r[-1] ...
  r[ 3] r[ 2] r[ 1] r[ 0] ...
  ...") 
    (/ 
        (get ̂a (+ indices N -1)) 
        N) )