from __future__ import annotations

import pathlib
from typing import Final

import numpy as np
from numpy import sqrt
from scipy.integrate import quad
from scipy.stats import norm, chi2
import quantities as pq
import pandas as pd

from wavesynlib.toolboxes.emwave.algorithms import λfT_eq
from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame, Decibel
from wavesynlib.languagecenter.datatypes.physicalquantities.conversions import to_K
from .constants import A_e, k_e, T_0, K_r



def _to_unit(
        x: pq.Quantity | np.ndarray | float, 
        unit: pq.Quantity
    ) -> np.ndarray | float:
    return x.rescale(unit).magnitude if isinstance(x, pq.Quantity) else x


def _to_K(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return to_K(x).magnitude if isinstance(x, pq.Quantity) else x


def _to_W(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.W)


def _to_km(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.km)


def _to_square_meter(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.m**2)


def _to_rad(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.rad)


def _to_s(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.second)


def _to_GHz(x: pq.Quantity | np.ndarray | float) -> np.ndarray | float:
    return _to_unit(x, pq.GHz)


def _to_ratio(x: Decibel | float) -> float:
    return x.pow_ratio if isinstance(x, Decibel) else x


_kalpha: Final[QuantityFrame] = QuantityFrame(pd.read_csv(pathlib.Path(__file__).parent / 'kalpha.csv'))


def get_k_α_table() -> QuantityFrame:
    return _kalpha


def T_g(
        f: pq.Quantity | np.ndarray | float, 
        k_g: float
    ) -> float:
    """Galactic noise temperature in kelvin at specified frequency.
f:   the frequency, in GHz or a instance of Quantity;
k_g: galactic constant: 1.6=quiet, 10=average, 60=high"""
    f = _to_GHz(f)
    return 5 + k_g / f**2.5


def k_α(f: pq.Quantity | np.ndarray | float) -> pq.Quantity:
    freq_array = _kalpha.qcol('freq')
    att_array = _kalpha.qcol('attenuation')
    f = _to_unit(f, freq_array.units)
    return np.interp(
        f, 
        freq_array.magnitude, 
        att_array.magnitude
    ) * att_array.units


def L_α(
        R:   pq.Quantity | float, 
        θ:   pq.Quantity | float, 
        h_r: pq.Quantity | float, 
        h_s: pq.Quantity | float, 
        f:   pq.Quantity | float
    ):
    """Calculate the atmospheric attenuation.

R:   range (in km or an instance of Quantity)
θ:   Rx beam axis elevation (in deg or an instance of Quantity)
h_r: antenna height above surface (in km or an instance of Quantity)
h_s: surface height above sea level (in km or an instance of Quantity)
f:   carrier frequency (in GHz or an instance of Quantity)"""
    R = _to_km(R)
    θ = _to_rad(θ)
    sinθ = np.sin(θ)
    hᵣ = _to_km(h_r)
    hₛ = _to_km(h_s)
    hᵣ_plus_hₛ = hᵣ + hₛ
    Aₑ = A_e.rescale(pq.km).magnitude
    kₑ = k_e
    _2kₑAₑ = 2 * kₑ * Aₑ
    
    result = quad(
        lambda r: np.exp(-(hᵣ_plus_hₛ + r**2 / _2kₑAₑ + r*sinθ) / 5), 
        a=0, 
        b=R
    )
    
    return Decibel(k_α(f).magnitude * result[0]).pow_ratio


def antenna_temp(
        R:   pq.Quantity | float, 
        θ:   pq.Quantity | float, 
        h_r: pq.Quantity | float,  
        h_s: pq.Quantity | float,  
        f:   pq.Quantity | float, 
        k_g: float, 
        G_s: float, 
        L_a: float
    ) -> pq.Quantity:
    """Calculate the antenna temperature in kelvins.

R:   range (in km or an instance of Quantity)
θ:   Rx beam axis elevation (in deg or an instance of Quantity)
h_r: antenna height above surface (in km or an instance of Quantity)
h_s: surface height above sea level (in km or an instance of Quantity)
f:   carrier frequency (in GHz or an instance of Quantity)
k_g: galactic constant: 1.6=quiet, 10=average, 60=high
G_s: sidelobe fraction of integrated antenna pattern
L_a: antenna loss as ratio."""
    L_a = _to_ratio(L_a)
    T0 = to_K(T_0).magnitude
    L_αt = L_α(R, θ, h_r, h_s, f)
    T_a1 = 0.75 * T0 * (1 - 1 / sqrt(L_αt))
    T_g_ = 290 if θ < 0 else T_g(f, k_g)
    T_a_ = T_a1 + T_g_
    return (T0 + (1 - G_s) * (T_a_ - T0) / L_a) * pq.kelvin


def rxline_temp(
        L_r:  float, 
        T_tr: pq.Quantity | float
    ) -> pq.Quantity:
    """Calculate the receiving line temperature in kelvins.

L_r:  the receiving line loss as ratio
T_tr: the physical temperature of line in kelvins"""
    if isinstance(T_tr, pq.Quantity):
        T_tr = to_K(T_tr).magnitude
    return (L_r - 1) * T_tr * pq.kelvin


def receiver_temp(F_n: float) -> pq.Quantity:
    """Calculate the receiver temperature.

F_n: the reciever noise figure as ratio."""
    return T_0 * (F_n - 1)


def sysnoise_temp(
        T_a: pq.Quantity | float, 
        T_r: pq.Quantity | float, 
        T_e: pq.Quantity | float, 
        L_r: float
    ) -> pq.Quantity | float:
    """Calculate the system noise temperature.

T_a: the antenna temperature (in kelvin or an instance of Quantity)
T_r: the receiving line temperature (in kelvin or an instance of Quantity)
T_e: the receiver temperature (in kelvin or an instance of Quantity)
L_r: the receiving line loss as ratio"""
    return T_a + T_r + L_r * T_e


def D_c1(P_fa: float, P_d: float) -> float:
    """Detectability Factor: Steady target, single pulse, and coherent detection (known phase)."""
    return (norm.isf(P_fa) - norm.isf(P_d)) ** 2 / 2


def K(x: float, n: int) -> float:
    """Probability that the chi-square distribution with 2n degrees of freedom exceeds x"""
    return 1 - chi2.cdf(x, df=n * 2)


def K_1(p: float, n: int) -> float:
    """Inverse of Q(x,n): value of x that is exceeded with probability p"""
    return chi2.ppf(1 - p, 2 * n)


def detectability_factor(
        P_d:  float, 
        P_fa: float, 
        n:    int, 
        n_e:  float
    ) -> float:
    """Detectability factor for integration of n pulses with n_e independent signal samples"""
    return (K_1(P_fa, n) - K_1(P_d, n_e) - 2 * (n - n_e)) / (n / n_e * K_1(P_d, n_e))


def freespace_range(
        P:   pq.Quantity | float, 
        t:   pq.Quantity | float, 
        G_t: float, 
        G_r: float, 
        σ:   pq.Quantity | float,  
        f:   pq.Quantity | float,  
        T_s: pq.Quantity | float, 
        D:   float, 
        M:   float, 
        L_p: float, 
        L_x: float, 
        L_t: float
    ) -> pq.Quantity:
    """\
Calculate freespace range. 

P:    power
t:    pulse width or CPI
G_t:  transmit antenna power gain as ratio
G_r:  receive antenna power gain as ratio
σ:    target cross section in m²
f:    carrier frequency in GHz
T_s:  system temperature (can be calculated by sysnoise-temp)
D:    detectability factor as ratio
M:    matching factor as ratio
L_p:  beamshape loss as ratio
L_x:  signal processing loss as ratio
L_t:  transmit line loss as ratio 
"""
    P = _to_W(P)
    t = _to_s(t)
    G_t = _to_ratio(G_t)
    G_r = _to_ratio(G_r)
    σ = _to_square_meter(σ)
    T_s = _to_K(T_s)
    D = _to_ratio(D)
    M = _to_ratio(M)
    L_p = _to_ratio(L_p)
    L_x = _to_ratio(L_x)
    L_t = _to_ratio(L_t)

    λ = λfT_eq(f=f).qcol("λ")[0].rescale(pq.meter).magnitude
    X = (P * t * G_t * G_r * σ * λ**2 * K_r / 
        (T_s * D * M * L_p * L_x * L_t))
    return X ** 0.25 * pq.km


def atmospheric_factor(
        R:   pq.Quantity | float, 
        θ_t: pq.Quantity | float, 
        h_r: pq.Quantity | float, 
        h_s: pq.Quantity | float,  
        f:   pq.Quantity | float
    ):
    R = _to_km(R)
    L_α1 = L_α(R, θ_t, h_r, h_s, f)

    # Initial range reduction factor as ratio.
    δ_1 = (1 / L_α1) ** 0.25
    R_1 = R * δ_1
    L_α2 = L_α(R_1, θ_t, h_r, h_s, f)

    # Range increase factor as ratio.
    δ_2 = (L_α1 / L_α2) ** 0.25
    return δ_1 * δ_2
