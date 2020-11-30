from math import cos
import sympy
import quantities as pq
import numpy as np

from wavesynlib.toolboxes.emwave.algorithms import frequency_wavelength_period
from wavesynlib.toolboxes.geography.proj import calc_euclidean_distance



_to_meter_if_quantity  = lambda value: value.rescale(pq.meter).magnitude if isinstance(value, pq.Quantity) else value
_to_hz_if_quantity     = lambda value: value.rescale(pq.Hz).magnitude if isinstance(value, pq.Quantity) else value



def beam_width(lambda_, N, d, theta=0, k=0.886):
    """
See https://www.analog.com/en/analog-dialogue/articles/phased-array-antenna-patterns-part1.html#
"""
    if isinstance(lambda_, pq.Quantity):
        lambda_ = lambda_.rescale(pq.meter).magnitude
    if isinstance(d, pq.Quantity):
        d = d.rescale(pq.meter).magnitude
    if isinstance(theta, pq.Quantity):
        theta = theta.rescale(pq.rad).magnitude
    return k*lambda_/(N*d*cos(theta))



def beam_width_equation(lambda_=None, N=None, d=None, theta=None, thetaB=None, k=0.886):
    """
See https://www.analog.com/en/analog-dialogue/articles/phased-array-antenna-patterns-part1.html#
"""
    if lambda_ is None:
        lambda_ = sympy.var("λ")
    elif isinstance(lambda_, pq.Quantity):
        lambda_ = lambda_.rescale(pq.meter).magnitude
    else:
        pass

    if N is None:
        N = sympy.var("N")

    if d is None:
        d = sympy.var("d")
    elif isinstance(d, pq.Quantity):
        d = d.rescale(pq.meter).magnitude

    if theta is None:
        theta = sympy.var("θ")
    elif isinstance(theta, pq.Quantity):
        theta = theta.rescale(pq.rad).magnitude

    if thetaB is None:
        thetaB = sympy.var("θ_B")
    elif isinstance(thetaB, pq.Quantity):
        thetaB = thetaB.rescale(pq.rad).magnitude

    eq = k*lambda_/(N*d*sympy.cos(theta)) - thetaB

    return sympy.solve(eq, set=True)



def xyz_to_phase_compensation(
    point_x, point_y, point_z, 
    element_x, element_y, element_z,
    carrier_frequency=None,
    carrier_wavelength=None):
    """Calculate phase compensation of each element for a given point."""
    carrier_wavelength = _to_meter_if_quantity(carrier_wavelength)
    if carrier_wavelength is not None: 
        # Should not use *= here.
        carrier_wavelength = carrier_wavelength * pq.meter

    carrier_frequency  = _to_hz_if_quantity(carrier_frequency)
    if carrier_frequency is not None: 
        # Should not use *= here.
        carrier_frequency = carrier_frequency * pq.Hz

    carrier_info = frequency_wavelength_period(f=carrier_frequency, lambda_=carrier_wavelength)
    wavelength = carrier_info["λ"]
    print(wavelength)

    dist = calc_euclidean_distance(
        x1=point_x, 
        y1=point_y, 
        z1=point_z,
        x2=element_x,
        y2=element_y,
        z2=element_z)
    delta_dist = ((dist-dist[0]) / wavelength).rescale(pq.dimensionless).magnitude
    delta_dist = np.modf(delta_dist)[0]
    return delta_dist * 2 * np.pi * pq.rad



if __name__ == "__main__":
    result = beam_width_equation(lambda_=0.2*pq.meter, d=0.1*pq.meter, theta=0, thetaB=1*pq.degree)
    print(result)
