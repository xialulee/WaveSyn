from math import ceil, pi
from numpy import abs, arcsin, deg2rad, dot, exp, inner, r_, rad2deg, sin, sum
from pandas import DataFrame



def ula_dft_directions(M, d):
    """\
Calculation the directions of an ULA corresponding to
each DFT vectors.

M: the number of the elements.
d: the space between elements with respect to wavelength."""
    result = []
    K = r_[:M]
    M_2 = M//2
    cd2 = ceil(d*2)
    steps = r_[(1-cd2):cd2] * M
    for k in K:
        j = ((k if k<=M_2 else k-M)+steps)/d/M
        j = j[abs(j)<=1]
        for i in j:
            theta = arcsin(i)
            result.append({
                "k":k, 
                "θ (°)":rad2deg(theta),
                "θ (rad)":theta})
    return DataFrame(result)



def calc_dft_indices(M, d, theta_deg=None, theta_rad=None):
    result = []
    if theta_deg is not None:
        theta_rad = deg2rad(theta_deg)
    else:
        theta_deg = rad2deg(theta_rad)
    theta_k = sin(theta_rad) * d * M % M
    for index, k in enumerate(theta_k):
        s1 = exp(1j*2*pi*k*r_[:M]/M)
        s2 = exp(1j*2*pi*round(k)*r_[:M]/M)
        loss = 1 - abs(sum(s1*s2.conj()))/M
        result.append({
            "θ(°)": theta_deg[index],
            "θ(rad)": theta_rad[index],
            "freq": k/M,
            "k": round(k),
            "loss": loss })
    return DataFrame(result)
