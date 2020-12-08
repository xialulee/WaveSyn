from typing import Union

import numpy as np
from pandas import DataFrame

import pyproj
import pymap3d

import quantities as pq
from quantities.quantity import Quantity

from wavesynlib.languagecenter.datatypes.quantitycontainers import QuantityFrame


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




def wgs84_to_lla(*,
    x: Union[float, np.ndarray, pq.Quantity]=None, 
    y: Union[float, np.ndarray, pq.Quantity]=None, 
    z: Union[float, np.ndarray, pq.Quantity]=None,
    xyz_frame: QuantityFrame=None):

    df_index = None

    if x is not None:
        x, y, z = (
            _to_meter_if_quantity(_flatten_if_array(v)) 
                for v in (x, y, z))
    elif xyz_frame is not None:
        x, y, z = (
            xyz_frame.qcol(s).rescale(pq.meter).magnitude
                for s in ("x", "y", "z"))
        df_index = xyz_frame.index
    else:
        raise ValueError("WGS84 coordinates not given.")

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
    return DataFrame(columns=head, data=data)



def wgs84_to_enu(*,
    x:          Union[float, np.ndarray, pq.Quantity]=None, 
    y:          Union[float, np.ndarray, pq.Quantity]=None, 
    z:          Union[float, np.ndarray, pq.Quantity]=None, 
    xyz_frame:  QuantityFrame=None,
    x0:         Union[float, pq.Quantity]=None,
    y0:         Union[float, pq.Quantity]=None,
    z0:         Union[float, pq.Quantity]=None,
    xyz0_frame: QuantityFrame=None
) -> QuantityFrame:

    df_index = None

    if x0 is not None:
        lla0 = wgs84_to_lla(x=x0, y=y0, z=z0)
    elif xyz0_frame is not None:
        if xyz0_frame.shape[0] > 1:
            raise ValueError("Multiple origin given.")
        lla0 = wgs84_to_lla(xyz_frame=xyz0_frame)
    else:
        raise ValueError("The origin of ENU is not given.")
    lon0 = lla0.iloc[0]['longitude/deg']
    lat0 = lla0.iloc[0]['latitude/deg']
    alt0 = lla0.iloc[0]['altitude/m']

    if x is not None:
        lla = wgs84_to_lla(x=x, y=y, z=z)
    elif xyz_frame is not None:
        lla = wgs84_to_lla(xyz_frame=xyz_frame)
        df_index = xyz_frame.index
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



def enu_to_wgs84(
    e, n, u,
    # Observer coord.
    # In WGS84: 
    x0=None, y0=None, z0=None,
    # In LLA:
    lat0=None, lon0=None, alt0=None):

    if x0 is not None:
        lla_0 = wgs84_to_lla(x=x0, y=y0, z=z0)
        lat0 = lla_0["latitude/deg"][0]
        lon0 = lla_0["longitude/deg"][0]
        alt0 = lla_0["altitude/m"][0]
    elif lat0 is not None:
        lat0, lon0 = (_to_degree_if_quantity(v) for v in (lat0, lon0))
        alt0 = _to_meter_if_quantity(alt0)
    else:
        raise NotImplementedError("The type of given observer coord is not implemented.")

    lat, lon, alt = pymap3d.enu.enu2geodetic(e, n, u, lat0=lat0, lon0=lon0, h0=alt0)
    return lla_to_wgs84(lat=lat, lon=lon, alt=alt)



def calc_euclidean_distance(
    x1=None, y1=None, z1=None, x2=None, y2=None, z2=None,
    lat1=None, lon1=None, alt1=None, lat2=None, lon2=None, alt2=None,
    e1=None, n1=None, u1=None, e2=None, n2=None, u2=None, 
    # Coord of observer in ENU system:
    lat0=None, lon0=None, alt0=None, 
    x0=None, y0=None, z0=None):
    """Calc Eulidean distance of points."""
    field_names = ("x/m", "y/m", "z/m")
    get_fields = lambda df: (df[name].to_numpy() for name in field_names)
    if x1 is not None:
        # Already WGS84. No need coord conversion. 
        # Unit conversion:
        x1, y1, z1, x2, y2, z2 = (
            _to_meter_if_quantity(_flatten_if_array(v)) for v in (x1, y1, z1, x2, y2, z2) )
    elif lat1 is not None:
        # LLA coords. Convert to WGS84:
        wgs84_1 = lla_to_wgs84(lat=lat1, lon=lon1, alt=alt1)
        wgs84_2 = lla_to_wgs84(lat=lat2, lon=lon2, alt=alt2)
        x1, y1, z1 = get_fields(wgs84_1)
        x2, y2, z2 = get_fields(wgs84_2)
    elif e1 is not None:
        if lat0 is not None:
            kwargs = dict(lat0=lat0, lon0=lon0, alt0=alt0)
        elif x0 is not None:
            kwargs = dict(x0=x0, y0=y0, z0=z0)
        else:
            raise NotImplementedError("The type of given observer coord is not implemented.")
        wgs84_1 = enu_to_wgs84(e=e1, n=n1, u=u1, **kwargs)
        wgs84_2 = enu_to_wgs84(e=e2, n=n2, u=u2, **kwargs)
        x1, y1, z1 = get_fields(wgs84_1)
        x2, y2, z2 = get_fields(wgs84_2)
    else:
        raise NotImplementedError("The type of given coord is not implemented.")

    return np.sqrt( (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2 ) * pq.meter



if __name__ == "__main__":
    pass








