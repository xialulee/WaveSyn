from math import asin, ceil, pi
from numpy import r_, hstack
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
