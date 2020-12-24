import numpy as np

import quantities as pq
import quantities as pq
from rangeequation.formulae import *

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import Decibel as dB




f   = 3*pq.GHz
h_r = 10*pq.meter
h_s = 0*pq.meter
θ_t = 1*pq.deg
k_g = 10
G_s = 0.12
L_a = dB(0.2)
L_r = 10**0.1

P_d = 0.9
P_fa = 1e-6
n=24
n_e = 1

print(L_α(np.inf, 1*pq.deg, h_r, h_s, f))

T_a = antenna_temp(np.inf, θ_t, 10*pq.m, 0*pq.m, 3*pq.GHz, k_g, G_s, L_a)
print(f"T_a = {T_a}")

T_r = rxline_temp(10**0.1, 290*pq.K)
print(f"T_r = {T_r}")

T_e = receiver_temp(10**0.5)
print(f"T_e = {T_e}")

T_s = sysnoise_temp(T_a, T_r, T_e, L_r)
print(f"T_s = {T_s}")

r_f = freespace_range(
    P   = 100*pq.kW, 
    t   = 1*pq.microsecond,
    G_t = dB(40),
    G_r = dB(40),
    σ   = 1*pq.m**2,
    f   = 3*pq.GHz,
    T_s = T_s,
    D   = dB(11),
    M   = dB(0.8),
    L_p = dB(1.3),
    L_x = dB(3),
    L_t = dB(1))

print(f"Freespace range: {r_f}")


δ = atmospheric_factor(r_f, θ_t, h_r, h_s, f)
print(f"Atmospheric factor: {δ}")


R_m = r_f * δ
print(f"Final result: {R_m}")

D_k = detectability_factor(P_d, P_fa, n, n_e)
print(f"Detectability_factor: {D_k}")

