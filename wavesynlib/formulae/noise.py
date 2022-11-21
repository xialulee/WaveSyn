from numpy import atleast_1d, sqrt 
from numpy.random import randn


def complex_gaussian(size, variance=1):
    size = atleast_1d(size)
    return sqrt(variance/2) * \
        (randn(*size) + 1j*randn(*size))