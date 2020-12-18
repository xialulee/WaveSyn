import pathlib
from typing import Union

import numpy as np
from scipy.integrate import quad
import pandas as pd
import quantities as pq
from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame

from .constants import A_e, k_e



# Troposphere attenuation table
_kalpha = QuantityFrame(pd.read_csv(pathlib.Path(__file__).parent/"kalpha.csv"))



def k_α(f:Union[float, pq.Quantity, np.ndarray]) -> pq.Quantity:
    """Calculating attenuation coefficients for the troposphere.
k: frequency, in GHz or Quantity instance with any frequency unit.
return (Quantity instance): unit length (defined by its unit) attenuation coefficient."""
    freq_array = _kalpha.qcol("freq")
    att_array  = _kalpha.qcol("attenuation")
    if isinstance(f, pq.Quantity):
        f = f.rescale(freq_array.units)
    return np.interp(f, freq_array.magnitude, att_array.magnitude) * att_array.units




def L_α(
    R: Union[float, pq.Quantity],
    θ: Union[float, pq.Quantity],
    h_r: Union[float, pq.Quantity],
    h_s: Union[float, pq.Quantity],
    f: Union[float, pq.Quantity]
) -> float:
    if isinstance(R, pq.Quantity): 
        R = R.rescale(pq.meter)
    if isinstance(θ, pq.Quantity):
        θ = θ.rescale(pq.rad)
    if isinstance(h_r, pq.Quantity):
        h_r = h_r.rescale(pq.meter)
    if isinstance(h_s, pq.Quantity):
        h_s = h_s.rescale(pq.meter)

    A_e = A_e.rescale(pq.meter)
    k_e = k_e.rescale(pq.meter)
    
    def func(r):
        np.exp(-1/5*(
            h_r + h_s + 
            r**2/2/k_e/A_e +
            r*np.sin(θ) ) )

    return quad(func, 0, R)