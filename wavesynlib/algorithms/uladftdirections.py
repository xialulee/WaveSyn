from math import ceil
from numpy import abs, arcsin, r_, rad2deg
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
