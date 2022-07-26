import webbrowser
from urllib.parse import quote

import numpy as np

from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame



def display_multiple_points(names, lla=None, wgs84=None):
    if lla is not None:
        if isinstance(lla, (list, tuple)):
            lla = np.array(lla)

        if isinstance(lla, QuantityFrame):
            pass
        elif isinstance(lla, np.ndarray):
            lla = QuantityFrame({
                "latitude/deg":  lla[:, 0],
                "longitude/deg": lla[:, 1]})
        else:
            raise NotImplementedError()
    elif wgs84 is not None:
        raise NotImplementedError()
    else:
        raise ValueError("No coordinate given.")

    uri = []

    for idx, coord in enumerate(lla.iloc):
        lat = coord.qelem("latitude").magnitude
        lon = coord.qelem("longitude").magnitude
        name = quote(str(names[idx]), safe="")
        uri.append(f"point.{str(lat)}_{str(lon)}_{name}")

    uri = "~".join(uri)
    uri = f"bingmaps:?collection={uri}"
    webbrowser.open(uri)
