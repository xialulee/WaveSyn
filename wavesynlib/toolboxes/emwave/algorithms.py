import numpy as np
import quantities as pq

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame

from . import constants



def λfT_eq(λ=None, f=None, T=None):
    def regularize(arg, unit):
        if not isinstance(arg, pq.Quantity):
            result = arg * unit
        else:
            result = arg.rescale(unit)
        if (result<=0).any():
            raise ValueError("The given argument should be a positive real number.")
        return result

    c = constants.c
    if λ is not None:
        λ = regularize(λ, pq.meter)
        T = λ / c
        f = 1 / T
    elif T is not None and T>0:
        T = regularize(T, pq.second)
        λ = c * T
        f = 1 / T
    elif f is not None and f>0:
        f = regularize(f, pq.Hz)
        T = 1 / f
        λ = c * T
    else:
        raise ValueError("No valid arguments given.")

    λ = np.atleast_1d(λ.rescale(pq.meter))
    f = np.atleast_1d(f.rescale(pq.Hz))
    T = np.atleast_1d(T.rescale(pq.second))

    return QuantityFrame({
        "λ/m": λ,
        "f/Hz": f,
        "T/s": T})



if __name__ == "__main__":
    print(λfT_eq(λ=0.05))
    print(λfT_eq(f=60*pq.GHz))
    print(λfT_eq(T=1))
