(import sys)


(defn hyeval [^str expr &optional frame]
    (unless frame
        (setv frame (. (sys.-getframe 1) f-locals)))  
    (-> expr (read-str) (eval :locals frame)))


(defn efhyeval [environment value &optional attribute] 
    (hyeval value :frame (. (sys.-getframe 1) f-locals)))