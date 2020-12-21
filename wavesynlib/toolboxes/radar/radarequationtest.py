import numpy as np

import quantities as pq
from rangeequation.formulae import L_α, T_a



print(L_α(np.inf, 1*pq.deg, 10*pq.m, 0*pq.m, 3*pq.GHz))

print(T_a(np.inf, 1*pq.deg, 10*pq.m, 0*pq.m, 3*pq.GHz, 10, 0.12, 10**0.02))
