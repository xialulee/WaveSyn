(require [hy.contrib.loop [loop]])

(import hashlib)



(defn calc-hash [fileobj algorithm]
    (setv algo (getattr hashlib (.lower algorithm) ) ) 
    (loop [[m (algo)] [f fileobj]]
        (setv data (.read fileobj 1048576) ) 
        (if-not data
            (.hexdigest m) 
        #_else (do
            (.update m data) 
            (recur m f) ) ) ) )
