import webbrowser
from urllib.parse import quote

import numpy as np

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame



def display_multiple_points(names, latlon=None, ecef=None):
    if latlon is not None:
        if isinstance(latlon, (list, tuple)):
            latlon = np.array(latlon)

        if isinstance(latlon, QuantityFrame):
            pass
        elif isinstance(latlon, np.ndarray):
            latlon = QuantityFrame({
                "latitude/deg":  latlon[:, 0],
                "longitude/deg": latlon[:, 1]})
        else:
            raise NotImplementedError()
    elif ecef is not None:
        raise NotImplementedError()
    else:
        raise ValueError("No coordinate given.")

    uri = []

    for idx, coord in enumerate(latlon.iloc):
        lat = coord.qelem("latitude").magnitude
        lon = coord.qelem("longitude").magnitude
        name = quote(str(names[idx]), safe="")
        uri.append(f"point.{str(lat)}_{str(lon)}_{name}")

    uri = "~".join(uri)
    uri = f"bingmaps:?collection={uri}"
    webbrowser.open(uri)
