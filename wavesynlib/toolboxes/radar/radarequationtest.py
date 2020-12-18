import numpy as np

import quantities as pq
from rangeequation.formulae import L_α



print(L_α(np.inf, 1*pq.deg, 10*pq.m, 0*pq.m, 3*pq.GHz))
