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



def _get_carrier_wavelength(carrier_frequency=None, carrier_wavelength=None):
    carrier_wavelength = _to_meter_if_quantity(carrier_wavelength)
    if carrier_wavelength is not None:
        # Should not use *= here.
        carrier_wavelength = carrier_wavelength * pq.meter

    carrier_frequency = _to_hz_if_quantity(carrier_frequency)
    if carrier_frequency is not None:
        # Should not use *= here.
        carrier_frequency = carrier_frequency * pq.Hz

    carrier_info = frequency_wavelength_period(
        f=carrier_frequency, 
        lambda_=carrier_wavelength)

    return carrier_info["λ"]



def _dist_to_phase_compensation(dist, wavelength):
    """For a given point, calculate the phase compensation of each element from the distances between the point and the elements.
dist:      float array, the distances between a given point and the elements;
wavelenth: Quantity, the wavelength of the carrier;
return:    Quantity, the compensation phase in rad."""
    delta_dist = ((dist-dist[0])/wavelength).rescale(pq.dimensionless).magnitude
    delta_dist = np.modf(delta_dist)[0]
    return delta_dist * 2 * np.pi * pq.rad



def xyz_to_phase_compensation(
    point_x, point_y, point_z, 
    element_x, element_y, element_z,
    carrier_frequency=None,
    carrier_wavelength=None):
    """Calculate phase compensation of each element of an array for a given point (In cartesian system).

point_x: Quantity/scalar, x-coord of the given point;
point_y: Quantity/scalar, y-coord of the given point;
point_z: Quantity/scalar, z-coord of the given point;
element_x: Quantity/array, x-coord of the array elements;
element_y: Quantity/array, y-coord of the array elements;
element_z: Quantity/array, z-coord of the array elements;
carrier_frequency: Quantity/scalar, optional, the carrier frequency;
carrier_wavelength: Quantity/scalar, optional, the carrier wavelength.

return: Quantity/array: the compensation phase in rad.

Note that one and only one of (carrier_frequency, carrier_wavelength) should be given."""
    wavelength = _get_carrier_wavelength(
        carrier_frequency=carrier_frequency,
        carrier_wavelength=carrier_wavelength)

    dist = calc_euclidean_distance(
        x1=point_x, 
        y1=point_y, 
        z1=point_z,
        x2=element_x,
        y2=element_y,
        z2=element_z)

    return _dist_to_phase_compensation(
        dist=dist, 
        wavelength=wavelength)



def enu_to_phase_compensation(
    point_e, point_n, point_u,
    element_e, element_n, element_u,
    origin_x=None, origin_y=None, origin_z=None,
    origin_lat=None, origin_lon=None, origin_alt=None,
    carrier_frequency=None,
    carrier_wavelength=None):
    """Calculate phase compensation of each element for a given point (In ENU system).
    
point_e: Quantity/scalar, E-coord of the given point;
point_n: Quantity/scalar, N-coord of the given point;
point_u: Quantity/scalar, U-coord of the given point;
element_e: Quantity/array, E-coord of the array elements;
element_n: Quantity/array, N-coord of the array elements;
element_u: Quantity/array, U-coord of the array elements;
origin_x: Quantity/scalar, optional, x-coord (WGS84) of the ENU origin;
origin_y: Quantity/scalar, optional, y-coord (WGS84) of the ENU origin;
origin_z: Quantity/scalar, optional, z-coord (WGS84) of the ENU origin;
origin_lat: Quantity/scalar, optional, LAT-coord (LLA) of the ENU origin;
origin_lon: Quantity/scalar, optional, LON-coord (LLA) of the ENU origin;
origin_alt: Quantity/scalar, optional, ALT-coord (LLA) of the ENU origin;
carrier_frequency: Quantity/scalar, optional, the carrier frequency;
carrier_wavelength: Quantity/scalar, optional, the carrier wavelength.

return: Quantity/array: the compensation phase in rad.

Note that: 
one and only one of (carrier_frequency, carrier_wavelength) should be given.
one and only one of the origin coord should be given (WGS84 or LLA).
"""
    wavelength = _get_carrier_wavelength(
        carrier_frequency=carrier_frequency,
        carrier_wavelength=carrier_wavelength)

    dist = calc_euclidean_distance(
        # Point ENU each of which is a scalar.
        e1=point_e,
        n1=point_n,
        u1=point_u,
        # Element ENU each of which is an array.
        e2=element_e,
        n2=element_n,
        u2=element_u,
        # WGS84 coord of origin if given.
        x0=origin_x,
        y0=origin_y,
        z0=origin_z,
        # LLA coord of origin if given.
        lat0=origin_lat,
        lon0=origin_lon,
        alt0=origin_alt)

    return _dist_to_phase_compensation(
        dist=dist,
        wavelength=wavelength)



if __name__ == "__main__":
    result = beam_width_equation(lambda_=0.2*pq.meter, d=0.1*pq.meter, theta=0, thetaB=1*pq.degree)
    print(result)
