(require [hy.contrib.loop [loop]])

(import [quantities :as pq])



(defn to-unit-ifq [x unit &optional mag]
    (if (instance? pq.Quantity x) (do
        (setv x (.rescale x unit))
        (if mag (setv x x.magnitude)))
    #_else
        #_pass)
    x)



(setv -module-namespace (locals))

(loop [[-unit-name-iter (iter (,
        "mm" "cm" "dm" "m" "km"
        "Hz" "kHz" "MHz" "GHz"))]]
    (setv -unit-name (first -unit-name-iter))
    (when -unit-name
        (assoc -module-namespace f"to_{-unit-name}_ifq"
            (fn [x &optional mag]
                (to-unit-ifq x (getattr pq -unit-name) :mag mag)))
        (recur -unit-name-iter)))
