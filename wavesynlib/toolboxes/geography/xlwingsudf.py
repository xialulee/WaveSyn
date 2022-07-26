from pathlib import Path
import numpy as np

import xlwings as xw
import quantities as pq

from ..basetoolboxnode import BaseXLWingsUDFNode
from . import proj
from . import bingmaps


class XLWingsUDFNode(BaseXLWingsUDFNode):
    def get_module_path(self) -> str:
        return f"{self.parent_node.toolbox_package_path}.{Path(__file__).stem}"


@xw.func
@xw.arg("lla", np.array, ndim=2)
def lla_to_wgs84(lla):
    wgs84 = proj.lla_to_wgs84(
        lat = lla[:, 0],
        lon = lla[:, 1],
        alt = lla[:, 2])
    return np.array(wgs84)


@xw.func
@xw.arg("wgs84", np.array, ndim=2)
def wgs84_to_lla(wgs84):
    lla = proj.wgs84_to_lla(
        x = wgs84[:, 0],
        y = wgs84[:, 1],
        z = wgs84[:, 2])
    return np.array(lla)


@xw.func
@xw.arg("lla", np.array, ndim=2)
@xw.arg("lla0", np.array, ndim=1)
def lla_to_enu(lla, lla0):
    enu = proj.lla_to_enu(
        lat = lla[:, 0],
        lon = lla[:, 1],
        alt = lla[:, 2],
        lat0 = lla0[0], 
        lon0 = lla0[1],
        alt0 = lla0[2])
    return np.array(enu)


@xw.func
@xw.arg("xyz1", np.array, ndim=2)
@xw.arg("xyz2", np.array, ndim=2)
def dist_wgs84(xyz1, xyz2):
    dist = proj.calc_euclid_dist(
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
def dist_lla(
    lla1, 
    lla2, 
    alt1_unit="m", 
    alt2_unit="m", 
    dist_unit="m"):
    """\
Calculate the distance between lla1 and lla2.
lla1:      the first LLA coordinate;
lla2:      the second LLA coordinate;
alt1_unit: the unit of lla1's altitude (m by default);
alt2_unit: the unit of lla2's altitude (m by default);
dist_unit: the unit of the distance (m by default).

The range of lla1 and lla2 should comprises three columns (lat, lon and alt). 
Either lla1 and lla2 have the same shape, or one of them only has one LLA coordinate.
"""
    dist = proj.calc_euclid_dist(
        # coord 1
        lat1=lla1[:, 0],
        lon1=lla1[:, 1],
        alt1=lla1[:, 2] * pq.CompoundUnit(alt1_unit),
        # coord 2
        lat2=lla2[:, 0], 
        lon2=lla2[:, 1],
        alt2=lla2[:, 2] * pq.CompoundUnit(alt2_unit))
    return dist.rescale(pq.CompoundUnit(dist_unit)).magnitude.reshape((dist.size, 1))


@xw.func
@xw.arg("lla", np.array, ndim=2)
def bingmaps_display_lla_points(names, lla):
    bingmaps.display_multiple_points(names, lla=lla)
    return "SUCCESS"
