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
def lla_to_wgs84(lla, alt_unit="m", xyz_unit="m"):
    """\
Convert LLA coordinates to WGS84 coordinates.
lla:       LLA coordinates of the given points;
alt_unit:  the altitude unit of the LLA coordinates;
xyz_unit:  the unit of the WGS84 coordinates;
"""
    xyz = proj.lla_to_wgs84(
        lat = lla[:, 0],
        lon = lla[:, 1],
        alt = lla[:, 2] * pq.CompoundUnit(alt_unit))
    return xyz.qmatrix.rescale(xyz_unit).magnitude


@xw.func
@xw.arg("xyz", np.array, ndim=2)
def wgs84_to_lla(xyz, xyz_unit="m", alt_unit="m"):
    """\
Convert WGS84 coordinates to LLA coordinates.
xyz:       WGS84 coordinates of the given points;
xyz_unit:  the unit of the WGS84 coordinates;
alt_unit:  the altitude unit of LLA coordinates;
"""
    xyz = xyz * pq.CompoundUnit(xyz_unit)
    lla = proj.wgs84_to_lla(
        x = xyz[:, 0],
        y = xyz[:, 1],
        z = xyz[:, 2])
    return np.vstack((
        lla.qcol("latitude").magnitude,
        lla.qcol("longitude").magnitude,
        lla.qcol("altitude").rescale(pq.CompoundUnit(alt_unit)).magnitude)).T


@xw.func
@xw.arg("lla", np.array, ndim=2)
@xw.arg("lla0", np.array, ndim=1)
def lla_to_enu(lla, lla0, alt_unit="m", alt0_unit="m", enu_unit="m"):
    """\
Convert LLA coordinates to ENU coordinates.
lla:       LLA coordinates of the given points;
lla0:      LLA coordinate of the origin;
alt_unit:  the altitude unit of lla;
alt0_unit: the altitude unit of the origin;
enu_unit:  the unit of enu.
"""
    enu = proj.lla_to_enu(
        lat = lla[:, 0],
        lon = lla[:, 1],
        alt = lla[:, 2] * pq.CompoundUnit(alt_unit),
        lat0 = lla0[0], 
        lon0 = lla0[1],
        alt0 = lla0[2] * pq.CompoundUnit(alt0_unit))
    enu_unit = pq.CompoundUnit(enu_unit)
    return enu.qmatrix.rescale(enu_unit).magnitude


@xw.func
@xw.arg("aer", np.array, ndim=2)
def aer_to_enu(aer, az_unit="deg", el_unit="deg", sr_unit="m", enu_unit="m"):
    """\
Convert AER coordinates to ENU coordinates.
aer:     AER coordinates of the given points;
az_unit: the azimuth unit of aer;
el_unit: the elevation unit of aer;
sr_unit: the slant range unit of aer.
"""
    enu = proj.aer_to_enu(
        a = aer[:, 0] * pq.CompoundUnit(az_unit),
        e = aer[:, 1] * pq.CompoundUnit(el_unit),
        r = aer[:, 2] * pq.CompoundUnit(sr_unit))
    enu_unit = pq.CompoundUnit(enu_unit)
    return enu.qmatrix.rescale(enu_unit).magnitude


@xw.func
@xw.arg("xyz1", np.array, ndim=2)
@xw.arg("xyz2", np.array, ndim=2)
def dist_wgs84(xyz1, xyz2, xyz1_unit="m", xyz2_unit="m", dist_unit="m"):
    """\
Calculate the distance between xyz1 and xyz2.
xyz1:      the first WGS84 coordinates;
xyz2:      the second WGS84 coordinates;
xyz1_unit: the unit of xyz1 (m by default);
xyz2_unit: the unit of xyz2 (m by default);
dist_unit: the unit of the distance (m by default).

The range of xyz1 and xyz2 should comprises three columns (x, y and z). 
Either xyz1 and xyz2 have the same shape, or one of them only has one WGS84 coordinate.
"""
    xyz1_unit = pq.CompoundUnit(xyz1_unit)
    xyz2_unit = pq.CompoundUnit(xyz2_unit)
    xyz1 = xyz1 * xyz1_unit
    xyz2 = xyz2 * xyz2_unit
    dist = proj.calc_euclid_dist(
        # coord 1
        x1=xyz1[:, 0],
        y1=xyz1[:, 1],
        z1=xyz1[:, 2],
        # coord 2
        x2=xyz2[:, 0], 
        y2=xyz2[:, 1],
        z2=xyz2[:, 2])
    return dist.rescale(pq.CompoundUnit(dist_unit)).magnitude.reshape((dist.size, 1))


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
lla1:      the first LLA coordinates;
lla2:      the second LLA coordinates;
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
@xw.arg("latlon", np.array, ndim=2)
def bingmaps_display_latlong_points(names, latlon):
    """\
Display multiple points on Windows Maps App. 
names:  the names of the points to display;
latlon: the latitude and longitude of the points to display.
"""
    bingmaps.display_multiple_points(names, latlon=latlon)
    return "SUCCESS"
