import quantities as pq



def to_unit_ifq(x, unit, mag=None):
    if isinstance(x, pq.Quantity):
        x = x.rescale(unit)
        if mag:
            x = x.magnitude
    return x


_module_namespace = locals()
for _unit_name in ('mm', 'cm', 'dm', 'm', 'km', 'Hz', 'kHz', 'MHz', 'GHz'):
    _module_namespace[f"to_{_unit_name}"] = lambda x, mag=None, __unit_name=_unit_name: \
        to_unit_ifq(x, getattr(pq, __unit_name), mag=mag)



def to_degF(t):
    if not isinstance(t, pq.Quantity):
        raise TypeError("t should be an instance of quantities.Quantity.")

    CtoF = lambda t: t.rescale(pq.degF) + 32*pq.degF
    KtoF = lambda t: (t - 273.15*pq.kelvin).rescale(pq.degF) + 32*pq.degF
    FtoF = lambda t: t

    dispatch = {"degC": CtoF, "K": KtoF, "degF": FtoF}

    return dispatch[t.dimensionality.string](t)



def to_degC(t):
    if not isinstance(t, pq.Quantity):
        raise TypeError("t should be an instance of quantities.Quantity.")

    FtoC = lambda t: (t - 32*pq.degF).rescale(pq.degC)
    KtoC = lambda t: (t - 273.15*pq.kelvin).rescale((pq.degC))
    CtoC = lambda t: t

    dispatch = {"degF": FtoC, "K": KtoC, "degC": CtoC}

    return dispatch[t.dimensionality.string](t)



def to_K(t):
    t = to_degC(t)
    return (t + 273.15*pq.degC).rescale(pq.Kelvin)



if __name__ == "__main__":
    print(to_degF(100*pq.degC))
    print(to_degF(373.15*pq.Kelvin))
    print(to_degC(212*pq.degF))
    print(to_degC(373.15*pq.Kelvin))
    print(to_K(100*pq.degC))
    print(to_K(212*pq.degF))
