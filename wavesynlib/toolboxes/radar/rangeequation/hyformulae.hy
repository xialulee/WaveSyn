(import pathlib)

(import [numpy :as np])
(import [numpy [sqrt :as √]])
(import [scipy.integrate [quad :as ∫ₐᵇ]])
(import [scipy.stats [norm chi2]])
(import [quantities :as pq])
(import [pandas :as pd])

(import [wavesynlib.toolboxes.emwave.algorithms [λfT-eq]])
(import [wavesynlib.languagecenter.datatypes.physicalquantities.containers [QuantityFrame Decibel]])
(import [wavesynlib.languagecenter.datatypes.physicalquantities.conversions [to-K]])

(import [.constants [A_e k_e T_0 K_r]])



(defn -to-unit [x unit]
    (if (instance? pq.Quantity x)
        (. (.rescale x unit) magnitude)
    #_else
        x))


(defn -to-K [x]
    (if (instance? pq.Quantity x)
        (-> x (to-K) (. magnitude)) 
    #_else  
        x) )


(defn -to-W [x]
    (-to-unit x pq.W))


(defn -to-km [x]
    (-to-unit x pq.km))


(defn -to-m² [x]
    (-to-unit x (** pq.m 2)))


(defn -to-rad [x]
    (-to-unit x pq.rad))


(defn -to-s [x]
    (-to-unit x pq.second))


(defn -to-GHz [x]
    (-to-unit x pq.GHz) )


(defn -to-ratio [x]
    (if (instance? Decibel x)
        (. x pow-ratio)
    #_else
        x))



(setv 
    -kalpha 
    (-> --file-- 
        (pathlib.Path) 
        (. parent) 
        (/ "kalpha.csv") 
        (pd.read-csv) 
        (QuantityFrame)))



(defn T_g [f k_g]
"Galactic noise temperature in kelvin at specified frequency.
f:   the frequency, in GHz or a instance of Quantity;
k_g: galactic constant: 1.6=quiet, 10=average, 60=high"
    (setv f (-to-GHz f))
    (+ 5 (/ k_g (** f 2.5))))



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



(defn antenna-temp [R θ h_r h_s f k_g G_s L_a]
"Calculate the antenna temperature in kelvins. 

R:   range (in km or an instance of Quantity)
θ:   Rx beam axis elevation (in deg or an instance of Quantity)
h_r: antenna height above surface (in km or an instance of Quantity)
h_s: surface height above sea level (in km or an instance of Quantity)
f:   carrier frequency (in GHz or an instance of Quantity)
k_g: galactic constant: 1.6=quiet, 10=average, 60=high
G_s: sidelobe fraction of integrated antenna pattern
L_a: antenna loss as ratio." 
    (setv
        L_a (-to-ratio L_a))
    (setv f²·⁵ (** (-to-GHz f) 2.5))
    (setv T₀ (. (to_K T_0) magnitude) )
    (setv L_αt (L_α R θ h_r h_s f) ) 
    (setv Tₐ₁ (->> L_αt
        (√) (/ 1) (- 1) (* 0.75 T₀) ) )
    (setv T_g_ 
        (if (< θ 0) 
            290
        #_else
            (T_g f k_g) ) ) 
    (setv T_a_ (+ Tₐ₁ T_g_)) 
    (* (+ T₀ (/ 
            (* (- 1 G_s) (- T_a_ T₀) ) 
            L_a)) 
        pq.kelvin) )



(defn rxline-temp [L_r T_tr]
"Calculate the receiving line temperature in kelvins.

L_r:  the receiving line loss as ratio
T_tr: the physical temperature of line in kelvins"
    (when (instance? pq.Quantity T_tr)
        (setv T_tr (-> T_tr (to_K) (. magnitude)) ) )
    (-> L_r 
        (- 1)
        (* T_tr)
        (* pq.kelvin)))



(defn receiver-temp [F_n]
"Calculate the receiver temperature.

F_n: the reciever noise figure as ratio."
    (* T_0 (- F_n 1)) )



(defn sysnoise-temp [T_a T_r T_e L_r]
"Calculate the system noise temperature.

T_a: the antenna temperature (in kelvin or an instance of Quantity)
T_r: the receiving line temperature (in kelvin or an instance of Quantity)
T_e: the receiver temperature (in kelvin or an instance of Quantity)
L_r: the receiving line loss as ratio"
    (+ T_a T_r (* L_r T_e)))




(defn D_c1 [P_fa P_d]
"Detectability Factor: Steady target, single pulse, and coherent detection (known phase)."
    (/ (** (- (norm.isf P_fa) (norm.isf P_d)) 2) 2) )



(defn K [x n]
"Probability that the chi-square distribution with 2n degrees of freedom exceeds x"
    (- 1 (.cdf chi2 x :df (* n 2))))



(defn K_1 [p n]
"Inverse of Q(x,n): value of x that is exceeded with probability p"
    (.ppf chi2 (- 1 p) (* 2 n)))



(defn detectability-factor [P_d P_fa n n_e]
"Detectability factor for integration of a pulses with n_e independent signal samples"
    (/ (- (K_1 P_fa n) (K_1 P_d n_e) (* 2 (- n n_e)))
        (* (/ n n_e) (K_1 P_d n_e))))




(defn freespace-range [
    P   ; power
    t   ; pulse width or CPI
    G_t ; transmit antenna power gain as ratio
    G_r ; receive antenna power gain as ratio
    σ   ; target cross section in m²
    f   ; carrier frequency in GHz
    T_s ; system temperature (can be calculated by sysnoise-temp)
    D   ; detectability factor as ratio
    M   ; matching factor as ratio
    L_p ; beamshape loss as ratio
    L_x ; signal processing loss as ratio
    L_t ; transmit line loss as ratio 
    ]
    (setv 
        P   (-to-W     P)
        t   (-to-s     t)
        G_t (-to-ratio G_t)
        G_r (-to-ratio G_r)
        σ   (-to-m²    σ)
        T_s (-to-K     T_s) 
        D   (-to-ratio D)
        M   (-to-ratio M)
        L_p (-to-ratio L_p)
        L_x (-to-ratio L_x)
        L_t (-to-ratio L_t))

    (setv 
        λ (as-> f it 
                (λfT-eq :f it) 
                (.qcol it "λ") 
                (first it)
                (.rescale it pq.meter)
                (. it magnitude)) 
        λ² (** λ 2))

    (setv X (/ (* P t G_t G_r σ λ² K_r) T_s D M L_p L_x L_t))
    (-> X 
        (** 0.25) 
        (* pq.km)))



(defn atmospheric-factor [
    R   ; range
    θ_t ; target elevation angle
    h_r
    h_s
    f]

    (setv R (-to-km R) )

    (setv L_α1 (L_α R θ_t h_r h_s f))
    
    (setv δ_1 (** (/ 1 L_α1) 0.25))
    (setv 
        R_1  (* R δ_1)
        L_α2 (L_α R_1 θ_t h_r h_s f))

    (setv δ_2 (** (/ L_α1 L_α2) 0.25))
    (* δ_1 δ_2))

