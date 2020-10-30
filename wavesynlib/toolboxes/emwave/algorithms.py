from . import constants



def frequency_wavelength_period(f=None, lambda_=None, T=None):
    c = constants.c
    if lambda_ is not None and lambda_>0:
        T = lambda_ / c
        f = 1 / T
    elif T is not None and T>0:
        lambda_ = c * T
        f = 1 / T
    elif f is not None and f>0:
        T = 1 / f
        lambda_ = c * T
    else:
        raise ValueError("Given parameters are not valid.")
    return {"f":f, "λ": lambda_, "T":T}
