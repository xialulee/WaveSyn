from typing import Union

import numpy as np
from pandas import DataFrame

import pyproj
import pymap3d

import quantities as pq
from quantities.quantity import Quantity

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame


_ecef_wgs84 = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
_lla      = pyproj.Proj(proj="longlat", ellps="WGS84", datum="WGS84")
_wgs84_to_lla_transformer = pyproj.Transformer.from_proj(
    proj_from=_ecef_wgs84,
    proj_to=_lla)
_lla_to_wgs84_transformer = pyproj.Transformer.from_proj(
    proj_from=_lla,
    proj_to=_ecef_wgs84)

_flatten_if_array = lambda value: value.flatten() if isinstance(value, np.ndarray) else value

_to_meter_if_quantity  = lambda value: value.rescale(pq.meter).magnitude if isinstance(value, pq.Quantity) else value
_to_degree_if_quantity = lambda value: value.rescale(pq.degree).magnitude if isinstance(value, pq.Quantity) else value

_any_not_None = lambda *t: any(i is not None for i in t)
_all_not_None = lambda *t: all(i is not None for i in t)

_split_qframe_xyz = lambda q: (q.qcol("x"), q.qcol("y"), q.qcol("z"))
_split_qframe_lla = lambda q: (q.qcol("latitude"), q.qcol("longitude"), q.qcol("altitude"))
_split_qframe_enu = lambda q: (q.qcol("east"), q.qcol("north"), q.qcol("up"))




def wgs84_to_lla(*,
    x: Union[float, np.ndarray, pq.Quantity]=None, 
    y: Union[float, np.ndarray, pq.Quantity]=None, 
    z: Union[float, np.ndarray, pq.Quantity]=None,
    xyz: QuantityFrame=None):

    df_index = None

    if _all_not_None(x, y, z):
        x, y, z = (
            _to_meter_if_quantity(_flatten_if_array(v)) 
                for v in (x, y, z))
    elif _any_not_None(x, y, z):
        raise ValueError("WGS84 x/y/z incomplete.")
    elif xyz is not None:
        x, y, z = (
            xyz.qcol(s).rescale(pq.meter).magnitude
                for s in ("x", "y", "z"))
        df_index = xyz.index
    else:
        raise ValueError("WGS84 coordinates x/y/z not given.")

    lon, lat, alt = _wgs84_to_lla_transformer.transform(x, y, z)
    data = np.vstack((lat, lon, alt)).transpose()
    head = ["latitude/deg", "longitude/deg", "altitude/m"]
    kwargs = {"data":data, "columns":head}
    if df_index is not None:
        kwargs["index"] = df_index
    return QuantityFrame(**kwargs)



def lla_to_wgs84(lat, lon, alt):
    lat = _to_degree_if_quantity(_flatten_if_array(lat))
    lon = _to_degree_if_quantity(_flatten_if_array(lon))
    alt = _to_meter_if_quantity(_flatten_if_array(alt))
    x, y, z = _lla_to_wgs84_transformer.transform(lon, lat, alt)
    data = np.vstack((x, y, z)).transpose()
    head = ("x/m", "y/m", "z/m")
    return QuantityFrame(columns=head, data=data)



def wgs84_to_enu(*,
    x:    Union[float, np.ndarray, pq.Quantity]=None, 
    y:    Union[float, np.ndarray, pq.Quantity]=None, 
    z:    Union[float, np.ndarray, pq.Quantity]=None, 
    xyz:  QuantityFrame=None,
    x0:   Union[float, pq.Quantity]=None,
    y0:   Union[float, pq.Quantity]=None,
    z0:   Union[float, pq.Quantity]=None,
    xyz0: QuantityFrame=None
) -> QuantityFrame:

    df_index = None

    if _all_not_None(x0, y0, z0):
        lla0 = wgs84_to_lla(x=x0, y=y0, z=z0)
    elif _any_not_None(x0, y0, z0):
        raise ValueError("WGS84 x0/y0/z0 incomplete.")
    elif xyz0 is not None:
        if xyz0.shape[0] > 1:
            raise ValueError("Multiple origin given.")
        lla0 = wgs84_to_lla(xyz=xyz0)
    else:
        raise ValueError("The origin of ENU is not given.")
    lon0 = lla0.iloc[0]['longitude/deg']
    lat0 = lla0.iloc[0]['latitude/deg']
    alt0 = lla0.iloc[0]['altitude/m']

    if _all_not_None(x, y, z):
        lla = wgs84_to_lla(x=x, y=y, z=z)
    elif _any_not_None(x, y, z):
        raise ValueError("WGS84 x/y/z incomplete.")
    elif xyz is not None:
        lla = wgs84_to_lla(xyz=xyz)
        df_index = xyz.index
    else:
        raise ValueError("No WGS84 coordinates given.")

    lon = lla['longitude/deg'].to_numpy()
    lat = lla['latitude/deg'].to_numpy()
    alt = lla['altitude/m'].to_numpy()

    east, north, up = pymap3d.enu.geodetic2enu(lat=lat, lon=lon, h=alt, lat0=lat0, lon0=lon0, h0=alt0)
    data = np.vstack((east, north, up))
    data = data.transpose()
    head = ("east/m", "north/m", "up/m")
    kwargs = {"data":data, "columns":head}
    if df_index is not None:
        kwargs["index"] = df_index
    return QuantityFrame(**kwargs)



def lla_to_enu(*,
    lat:  Union[float, np.ndarray, pq.Quantity]=None, 
    lon:  Union[float, np.ndarray, pq.Quantity]=None, 
    alt:  Union[float, np.ndarray, pq.Quantity]=None, 
    lla:  QuantityFrame=None,
    lat0: Union[float, pq.Quantity]=None,
    lon0: Union[float, pq.Quantity]=None,
    alt0: Union[float, pq.Quantity]=None,
    lla0: QuantityFrame=None
) -> QuantityFrame:

    df_index = None

    if _all_not_None(lat0, lon0, alt0):
        pass
    elif _any_not_None(lat0, lon0, alt0):
        raise ValueError("LLA lat0/lon0/alt0 incomplete.")
    elif lla0 is not None:
        if lla0.shape[0] > 1:
            raise ValueError("Multiple origin given.")
        lon0 = lla0.iloc[0]['longitude/deg']
        lat0 = lla0.iloc[0]['latitude/deg']
        alt0 = lla0.iloc[0]['altitude/m']
    else:
        raise ValueError("The origin of ENU is not given.")

    if _all_not_None(lat, lon, alt):
        #lla = wgs84_to_lla(x=x, y=y, z=z)
        pass
    elif _any_not_None(lat, lon, alt):
        raise ValueError("LLA lat/lon/alt incomplete.")
    elif lla is not None:
        df_index = lla.index
        lon = lla['longitude/deg'].to_numpy()
        lat = lla['latitude/deg'].to_numpy()
        alt = lla['altitude/m'].to_numpy()
    else:
        raise ValueError("No LLA coordinates given.")

    east, north, up = pymap3d.enu.geodetic2enu(lat=lat, lon=lon, h=alt, lat0=lat0, lon0=lon0, h0=alt0)
    data = np.vstack((east, north, up))
    data = data.transpose()
    head = ("east/m", "north/m", "up/m")
    kwargs = {"data":data, "columns":head}
    if df_index is not None:
        kwargs["index"] = df_index
    return QuantityFrame(**kwargs)


def enu_to_wgs84(
    e: Union[float, np.ndarray, Quantity], 
    n: Union[float, np.ndarray, Quantity], 
    u: Union[float, np.ndarray, Quantity],
    # Observer coord.
    # In WGS84: 
    x0: Union[float, Quantity]=None, 
    y0: Union[float, Quantity]=None, 
    z0: Union[float, Quantity]=None,
    # In LLA:
    lat0: Union[float, Quantity]=None, 
    lon0: Union[float, Quantity]=None, 
    alt0: Union[float, Quantity]=None
) -> QuantityFrame:

    e, n, u = (_to_meter_if_quantity(v) for v in (e, n, u))

    if _all_not_None(x0, y0, z0):
        lla_0 = wgs84_to_lla(x=x0, y=y0, z=z0)
        lat0 = lla_0["latitude/deg"][0]
        lon0 = lla_0["longitude/deg"][0]
        alt0 = lla_0["altitude/m"][0]
    elif _any_not_None(x0, y0, z0):
        raise ValueError("WGS84 x0/y0/z0 incomplete.")
    elif _all_not_None(lat0, lon0, alt0):
        lat0, lon0 = (_to_degree_if_quantity(v) for v in (lat0, lon0))
        alt0 = _to_meter_if_quantity(alt0)
    elif _any_not_None(lat0, lon0, alt0):
        raise ValueError("LLA lat0/lon0/alt0 incomplete.")
    else:
        raise NotImplementedError("The type of given observer coord is not implemented.")

    lat, lon, alt = pymap3d.enu.enu2geodetic(e, n, u, lat0=lat0, lon0=lon0, h0=alt0)
    return lla_to_wgs84(lat=lat, lon=lon, alt=alt)



def enu_to_lla(*args, **kwargs):
    xyz = enu_to_wgs84(*args, **kwargs)
    return wgs84_to_lla(xyz=xyz)



def calc_euclid_dist(*,
    x1:   Union[np.ndarray, Quantity]=None, 
    y1:   Union[np.ndarray, Quantity]=None, 
    z1:   Union[np.ndarray, Quantity]=None, 
    x2:   Union[np.ndarray, Quantity]=None, 
    y2:   Union[np.ndarray, Quantity]=None, 
    z2:   Union[np.ndarray, Quantity]=None,
    xyz1: QuantityFrame=None,
    xyz2: QuantityFrame=None,
    lat1: Union[np.ndarray, Quantity]=None, 
    lon1: Union[np.ndarray, Quantity]=None, 
    alt1: Union[np.ndarray, Quantity]=None, 
    lla1: QuantityFrame=None,
    lat2: Union[np.ndarray, Quantity]=None, 
    lon2: Union[np.ndarray, Quantity]=None, 
    alt2: Union[np.ndarray, Quantity]=None,
    lla2: QuantityFrame=None,
    e1:   Union[np.ndarray, Quantity]=None, 
    n1:   Union[np.ndarray, Quantity]=None, 
    u1:   Union[np.ndarray, Quantity]=None, 
    enu1: QuantityFrame=None,
    e2:   Union[np.ndarray, Quantity]=None, 
    n2:   Union[np.ndarray, Quantity]=None, 
    u2:   Union[np.ndarray, Quantity]=None, 
    enu2: QuantityFrame=None,
    # Coord of observer in ENU system:
    lat0: Union[float, Quantity]=None, 
    lon0: Union[float, Quantity]=None, 
    alt0: Union[float, Quantity]=None, 
    lla0: QuantityFrame=None,
    x0:   Union[float, Quantity]=None, 
    y0:   Union[float, Quantity]=None, 
    z0:   Union[float, Quantity]=None,
    xyz0: QuantityFrame=None
) -> Quantity:
    """Calc Eulidean distance of points."""
    field_names = ("x/m", "y/m", "z/m")
    get_fields = lambda df: (df[name].to_numpy() for name in field_names)
    if (_all_not_None(x1, y1, z1) or xyz1 is not None) and (_all_not_None(x2, y2, z2) or xyz2 is not None):
        # Already WGS84. No need coord conversion. 
        if x1 is None:
            x1, y1, z1 = _split_qframe_xyz(xyz1)
        if x2 is None:
            x2, y2, z2 = _split_qframe_xyz(xyz2)
        # Unit conversion:
        x1, y1, z1, x2, y2, z2 = (
            _to_meter_if_quantity(_flatten_if_array(v)) for v in (x1, y1, z1, x2, y2, z2) )
    elif (_all_not_None(lat1, lon1, alt1) or lla1 is not None) and (_all_not_None(lat2, lon2, alt2) or lla2 is not None):
        # LLA coords. Convert to WGS84:
        if lat1 is None:
            lat1, lon1, alt1 = _split_qframe_lla(lla1)
        if lat2 is None:
            lat2, lon2, alt2 = _split_qframe_lla(lla2)
        wgs84_1 = lla_to_wgs84(lat=lat1, lon=lon1, alt=alt1)
        wgs84_2 = lla_to_wgs84(lat=lat2, lon=lon2, alt=alt2)
        x1, y1, z1 = get_fields(wgs84_1)
        x2, y2, z2 = get_fields(wgs84_2)
    elif (_all_not_None(e1, n1, u1) or enu1 is not None) and (_all_not_None(e2, n2, u2) or enu2 is not None):
        if _all_not_None(lat0, lon0, alt0) or lla0 is not None:
            if lat0 is None:
                lat0 = lla0.qcol("latitude")[0]
                lon0 = lla0.qcol("longitude")[0]
                alt0 = lla0.qcol("altitude")[0]
            kwargs = dict(lat0=lat0, lon0=lon0, alt0=alt0)
        elif _all_not_None(x0, y0, z0) or xyz0 is not None:
            if x0 is None:
                x0 = xyz0.qcol("x")[0]
                y0 = xyz0.qcol("y")[0]
                z0 = xyz0.qcol("z")[0]
            kwargs = dict(x0=x0, y0=y0, z0=z0)
        else:
            raise NotImplementedError("The type of given observer coord is not implemented.")
        if e1 is None:
            e1, n1, u1 = _split_qframe_enu(enu1)
        if e2 is None:
            e2, n2, u2 = _split_qframe_enu(enu2)
        wgs84_1 = enu_to_wgs84(e=e1, n=n1, u=u1, **kwargs)
        wgs84_2 = enu_to_wgs84(e=e2, n=n2, u=u2, **kwargs)
        x1, y1, z1 = get_fields(wgs84_1)
        x2, y2, z2 = get_fields(wgs84_2)
    else:
        raise NotImplementedError("The type of given coord is not implemented.")

    return np.sqrt( (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2 ) * pq.meter



if __name__ == "__main__":
    pass








