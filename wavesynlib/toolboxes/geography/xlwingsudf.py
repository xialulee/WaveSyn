import numpy as np
import xlwings as xw

from . import proj


@xw.func
@xw.arg("lla", np.array, ndim=2)
def lla_to_wgs84(lla):
    wgs84 = proj.lla_to_wgs84(*(col for col in lla.T))
    return np.array(wgs84)


@xw.func
@xw.arg("wgs84", np.array, ndim=2)
def wgs84_to_lla(wgs84):
    lla = proj.wgs84_to_lla(*(col for col in wgs84.T))
    return np.array(lla)


@xw.func
@xw.arg("xyz1", np.array, ndim=2)
@xw.arg("xyz2", np.array, ndim=2)
def dist_wgs84(xyz1, xyz2):
    dist = proj.calc_euclidean_distance(
        # coord 1
        x1=xyz1[:, 0],
        y1=xyz1[:, 1],
        z1=xyz1[:, 2],
        # coord 2
        x2=xyz2[:, 0], 
        y2=xyz2[:, 1],
        z2=xyz2[:, 2])
    return dist.magnitude.reshape((dist.size, 1))


@xw.func
@xw.arg("lla1", np.array, ndim=2)
@xw.arg("lla2", np.array, ndim=2)
def dist_lla(lla1, lla2):
    dist = proj.calc_euclidean_distance(
        # coord 1
        lat1=lla1[:, 0],
        lon1=lla1[:, 1],
        alt1=lla1[:, 2],
        # coord 2
        lat2=lla2[:, 0], 
        lon2=lla2[:, 1],
        alt2=lla2[:, 2])
    return dist.magnitude.reshape((dist.size, 1))
