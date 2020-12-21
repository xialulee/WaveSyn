(import pathlib)

(import [numpy :as np])
(import [scipy.integrate [quad :as ∫ₐᵇ]])
(import [quantities :as pq])
(import [pandas :as pd])

(import [wavesynlib.languagecenter.datatypes.physicalquantities.containers [QuantityFrame]])

(import [.constants [A_e k_e]])



(defn -to-unit [x unit]
    (if (instance? pq.Quantity x)
        (. (.rescale x unit) magnitude)
    #_else
        x))


(defn -to-km [x]
    (-to-unit x pq.km))


(defn -to-rad [x]
    (-to-unit x pq.rad))



(setv 
    -kalpha 
    (-> --file-- 
        (pathlib.Path) 
        (. parent) 
        (/ "kalpha.csv") 
        (pd.read-csv) 
        (QuantityFrame)))



(defn k_α [f]
    (setv 
        freq-array (.qcol -kalpha "freq")
        att-array  (.qcol -kalpha "attenuation")) 
    (setv f (-to-unit f freq-array.units)) 
    (* (np.interp f freq-array.magnitude att-array.magnitude) att-array.units) )



(defn L_α [R θ h_r h_s f]
    (setv 
        R     (-to-km R)
        θ     (-to-rad θ)
        sinθ  (np.sin θ)
        hᵣ    (-to-km h_r)
        hₛ     (-to-km h_s)
        hᵣ+hₛ  (+ hᵣ hₛ)
        Aₑ    A_e.magnitude
        kₑ    k_e
        2kₑAₑ (* 2 kₑ Aₑ)
        -⅕    (/ -1 5))
        
    (setv result
        (∫ₐᵇ (fn [r] 
            (setv 
                r²    (** r 2)
                rsinθ (* r sinθ) )
            (np.exp (* -⅕ (+ hᵣ+hₛ (/ r² 2kₑAₑ) rsinθ) )) )
        :a 0 :b R #_dr))
        
    (as-> 
        (first result) it
        (* (. (k_α f) magnitude) it) 
        (/ it 10)
        (** 10 it) ) )
