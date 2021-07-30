import numpy as np
import quantities as pq

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame

from . import constants



def _to_meter(x):
    if isinstance(x, pq.Quantity):
        return x.rescale(pq.meter).magnitude
    else:
        return x



def λfT_eq(λ=None, f=None, T=None):
    def regularize(arg, unit):
        if not isinstance(arg, pq.Quantity):
            result = arg * unit
        else:
            result = arg.rescale(unit)
        if (result<=0).any():
            raise ValueError("The given argument should be a positive real number.")
        return result

    def valid(v):
        if v is None:
            return False
        if isinstance(v, np.ndarray):
            return (v>0).all()
        else:
            return v>0

    c = constants.c
    if valid(λ):
        λ = regularize(λ, pq.meter)
        T = λ / c
        f = 1 / T
    elif valid(T):
        T = regularize(T, pq.second)
        λ = c * T
        f = 1 / T
    elif valid(f):
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



def dist_to_phase(dist, λ=None, f=None, T=None):
    λfT = λfT_eq(λ=λ, f=f, T=T)
    λ = λfT.qcol("λ").rescale(pq.meter).magnitude
    dist = _to_meter(dist)
    return -2 * np.pi * np.modf(dist/λ)[0] * pq.rad



if __name__ == "__main__":
    print(λfT_eq(λ=0.05))
    print(λfT_eq(f=60*pq.GHz))
    print(λfT_eq(T=1))
