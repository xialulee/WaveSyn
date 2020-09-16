from math import asin, ceil, pi
from numpy import r_, hstack, deg2rad, rad2deg, dot, exp, sin
from pandas import DataFrame



def calc_directions(num_elem, dist_elem):
    #k_range = r_[:num_elem] - num_elem//2
    k_range = r_[:num_elem]
    neg_index = (num_elem - 1) // 2
    k_range[-neg_index:] -= num_elem
    cd2 = ceil(dist_elem*2)
    steps = hstack([0, r_[(1-cd2):0], r_[1:cd2]]) * num_elem
    result = []
    for k in k_range:
        ratio_coll = (k+steps)/dist_elem/num_elem
        ratio_coll = [ratio for ratio in ratio_coll if -1<=ratio<=1]
        result.append(dict(
            dft_index=k,
            angle_coll=[asin(ratio) for ratio in ratio_coll]))
    return DataFrame(result)



def angles_to_dft_indices(num_elem, dist_elem, angles_deg=None, angles_rad=None):
    result = []
    if angles_deg and angles_rad:
        raise ValueError("Only one of theta_deg and theta_rad should be specified.")
    if angles_deg:
        angles_rad = deg2rad(angles_deg)
    elif angles_rad:
        angles_deg = rad2deg(angles_rad)
    theta_k = sin(angles_rad) * dist_elem * num_elem % num_elem
    for index, k in enumerate(theta_k):
        s1 = exp(1j*2*pi*k*r_[:num_elem]/num_elem)
        s2 = exp(1j*2*pi*round(k)*r_[:num_elem]/num_elem)
        loss = 1 - abs(sum(s1*s2.conj())) / num_elem
        result.append({
            "angles_deg": angles_deg[index],
            "angles_rad": angles_rad[index],
            "freq": k/num_elem,
            "dft_index": round(k),
            "loss": loss })
    return DataFrame(result)




#######################################################################
#from math import ceil, pi
#from numpy import abs, arcsin, deg2rad, dot, exp, inner, r_, rad2deg, sin, sum
#from pandas import DataFrame



#def ula_dft_directions(M, d):
    #"""\
#Calculation the directions of an ULA corresponding to
#each DFT vectors.

#M: the number of the elements.
#d: the space between elements with respect to wavelength."""
    #result = []
    #K = r_[:M]
    #M_2 = M//2
    #cd2 = ceil(d*2)
    #steps = r_[(1-cd2):cd2] * M
    #for k in K:
        #j = ((k if k<=M_2 else k-M)+steps)/d/M
        #j = j[abs(j)<=1]
        #for i in j:
            #theta = arcsin(i)
            #result.append({
                #"k":k, 
                #"θ (°)":rad2deg(theta),
                #"θ (rad)":theta})
    #return DataFrame(result)



#def calc_dft_indices(M, d, theta_deg=None, theta_rad=None):
    #result = []
    #if theta_deg is not None:
        #theta_rad = deg2rad(theta_deg)
    #else:
        #theta_deg = rad2deg(theta_rad)
    #theta_k = sin(theta_rad) * d * M % M
    #for index, k in enumerate(theta_k):
        #s1 = exp(1j*2*pi*k*r_[:M]/M)
        #s2 = exp(1j*2*pi*round(k)*r_[:M]/M)
        #loss = 1 - abs(sum(s1*s2.conj()))/M
        #result.append({
            #"θ(°)": theta_deg[index],
            #"θ(rad)": theta_rad[index],
            #"freq": k/M,
            #"k": round(k),
            #"loss": loss })
    #return DataFrame(result)

