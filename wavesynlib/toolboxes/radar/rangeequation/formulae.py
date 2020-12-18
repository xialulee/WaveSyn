import hy

from math import log10
import pathlib
from typing import Union

import numpy as np
from scipy.integrate import quad
import pandas as pd
import quantities as pq
from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame

from .constants import A_e, k_e

from .hyformulae import L_α



# Troposphere attenuation table
#_kalpha = QuantityFrame(pd.read_csv(pathlib.Path(__file__).parent/"kalpha.csv"))



#def k_α(f:Union[float, pq.Quantity, np.ndarray]) -> pq.Quantity:
    #"""Calculating attenuation coefficients for the troposphere.
#k: frequency, in GHz or Quantity instance with any frequency unit.
#return (Quantity instance): unit length (defined by its unit) attenuation coefficient."""
    #freq_array = _kalpha.qcol("freq")
    #att_array  = _kalpha.qcol("attenuation")
    #if isinstance(f, pq.Quantity):
        #f = f.rescale(freq_array.units)
    #return np.interp(f, freq_array.magnitude, att_array.magnitude) * att_array.units




#def L_α(
    #R: Union[float, pq.Quantity],
    #θ: Union[float, pq.Quantity],
    #h_r: Union[float, pq.Quantity],
    #h_s: Union[float, pq.Quantity],
    #f: Union[float, pq.Quantity]
#) -> float:

    #if isinstance(R, pq.Quantity): 
        #R = R.rescale(pq.km).magnitude
    #if isinstance(θ, pq.Quantity):
        #θ = θ.rescale(pq.rad).magnitude
    #if isinstance(h_r, pq.Quantity):
        #h_r = h_r.rescale(pq.km).magnitude
    #if isinstance(h_s, pq.Quantity):
        #h_s = h_s.rescale(pq.km).magnitude

    #A_e_ = A_e.magnitude

    #def func(r):
        #return np.exp(-1/5*(
            #h_r + h_s + 
            #r**2/2/k_e/A_e_ +
            #r*np.sin(θ) ) )
    #return 10 ** (k_α(f).magnitude*quad(func, 0, R)[0] / 10)
