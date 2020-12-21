import numpy as np

import quantities as pq
import quantities as pq
from rangeequation.formulae import *




L_r = 10**0.1

print(L_α(np.inf, 1*pq.deg, 10*pq.m, 0*pq.m, 3*pq.GHz))

T_a = antenna_temp(np.inf, 1*pq.deg, 10*pq.m, 0*pq.m, 3*pq.GHz, 10, 0.12, 10**0.02)
print(f"T_a = {T_a}")

T_r = rxline_temp(10**0.1, 290*pq.K)
print(f"T_r = {T_r}")

T_e = receiver_temp(10**0.5)
print(f"T_e = {T_e}")

T_s = sysnoise_temp(T_a, T_r, T_e, L_r)
print(f"T_s = {T_s}")


