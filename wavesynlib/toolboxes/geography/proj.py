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
    data = np.vstack((lon, lat, alt))
    data = data.transpose()
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



def wgs84_to_enu(x, y, z, x0, y0, z0, ell=None):
    lla0 = wgs84_to_lla(x0, y0, z0)
    lon0 = lla0.iloc[0]['longitude/deg']
    lat0 = lla0.iloc[0]['latitude/deg']
    alt0 = lla0.iloc[0]['altitude/m']

    lla = wgs84_to_lla(x, y, z)
    lon = lla['longitude/deg'].to_numpy()
    lat = lla['latitude/deg'].to_numpy()
    alt = lla['altitude/m'].to_numpy()

    east, north, up = pymap3d.enu.geodetic2enu(lat=lat, lon=lon, h=alt, lat0=lat0, lon0=lon0, h0=alt0)
    data = np.vstack((east, north, up))
    data = data.transpose()
    head = ("east/m", "north/m", "altitude/m")
    return DataFrame(data=data, columns=head)



if __name__ == "__main__":
    pass








