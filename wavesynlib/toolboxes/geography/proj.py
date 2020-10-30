import numpy as np
from pandas import DataFrame

import pyproj
import pymap3d

import quantities as pq


_ecef_wgs84 = pyproj.Proj(proj="geocent", ellps="WGS84", datum="WGS84")
_lla      = pyproj.Proj(proj="longlat", ellps="WGS84", datum="WGS84")
_wgs84_to_lla_transformer = pyproj.Transformer.from_proj(
    proj_from=_ecef_wgs84,
    proj_to=_lla)
_lla_to_wgs84_transformer = pyproj.Transformer.from_proj(
    proj_from=_lla,
    proj_to=_ecef_wgs84)



def wgs84_to_lla(x, y, z):
    x, y, z = [arg.rescale(pq.meter) if isinstance(arg, pq.Quantity) else arg
                    for arg in (x, y, z)]
    lon, lat, alt = _wgs84_to_lla_transformer.transform(x, y, z)
    data = np.hstack((lon, lat, alt))
    data = data.reshape(-1, 3)
    head = ["longitude/deg", "latitude/deg", "altitude/m"]
    return DataFrame(data=data, columns=head)



def lla_to_wgs84(lon, lat, alt):
    lon = lon.rescale(pq.degree) if isinstance(lon, pq.Quantity) else lon
    lat = lat.rescale(pq.degree) if isinstance(lat, pq.Quantity) else lat
    alt = alt.rescale(pq.meter)  if isinstance(alt, pq.Quantity) else alt
    x, y, z = _lla_to_wgs84_transformer.transform(lon, lat, alt)
    data = np.hstack((x, y, z))
    data = data.reshape(-1, 3)
    head = ("x/m", "y/m", "z/m")
    return DataFrame(columns=head, data=data)
