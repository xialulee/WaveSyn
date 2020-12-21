(import pathlib)

(import [numpy :as np])
(import [numpy [sqrt :as √]])
(import [scipy.integrate [quad :as ∫ₐᵇ]])
(import [quantities :as pq])
(import [pandas :as pd])

(import [wavesynlib.languagecenter.datatypes.physicalquantities.containers [QuantityFrame]])
(import [wavesynlib.languagecenter.datatypes.physicalquantities.conversions [to_K]])

(import [.constants [A_e k_e T_0]])



(defn -to-unit [x unit]
    (if (instance? pq.Quantity x)
        (. (.rescale x unit) magnitude)
    #_else
        x))


(defn -to-km [x]
    (-to-unit x pq.km))


(defn -to-rad [x]
    (-to-unit x pq.rad))


(defn -to-GHz [x]
    (-to-unit x pq.GHz) )



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
"Calculate the atmospheric attenuation.

R:   range (in km or an instance of Quantity)
θ:   Rx beam axis elevation (in deg or an instance of Quantity)
h_r: antenna height above surface (in km or an instance of Quantity)
h_s: surface height above sea level (in km or an instance of Quantity)
f:   carrier frequency (in GHz or an instance of Quantity)" 
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



(defn T_a [R θ h_r h_s f k_g G_s L_a]
"Calculate the antenna temperature in kelvins. 

R:   range (in km or an instance of Quantity)
θ:   Rx beam axis elevation (in deg or an instance of Quantity)
h_r: antenna height above surface (in km or an instance of Quantity)
h_s: surface height above sea level (in km or an instance of Quantity)
f:   carrier frequency (in GHz or an instance of Quantity)
k_g: galactic constant: 1.6=quiet, 10=average, 60=high
G_s: sidelobe fraction of integrated antenna pattern
L_a: antenna loss as ratio." 
    (setv f²·⁵ (** (-to-GHz f) 2.5))
    (setv T₀ (. (to_K T_0) magnitude) )
    (setv L_αt (L_α R θ h_r h_s f) ) 
    (setv Tₐ₁ (->> L_αt
        (√) (/ 1) (- 1) (* 0.75 T₀) ) )
    (setv T_g 
        (if (< θ 0) 
            290
        #_else
            (+ (/ k_g f²·⁵) 5) ) ) 
    (setv T_a_ (+ Tₐ₁ T_g)) 
    (+ T₀ (/ 
        (* (- 1 G_s) (- T_a_ T₀) ) 
        L_a)) )
