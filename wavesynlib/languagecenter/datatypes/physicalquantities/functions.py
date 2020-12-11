import numpy as np
from numpy import pi as π
import quantities as pq



def expj(x):
    if isinstance(x, pq.Quantity):
        x = x.rescale(pq.rad).magnitude
    return np.exp(1j*x)



def expj2π(x):
    if isinstance(x, pq.Quantity):
        raise ValueError('Parameter "x" should be a normalized value rather than a quantity.')
    return np.exp(1j*2*π*x)
