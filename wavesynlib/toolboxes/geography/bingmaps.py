import webbrowser
from urllib.parse import quote
import numpy as np
from wavesynlib.languagecenter.datatypes.physicalquantities.containers import QuantityFrame

def display_multiple_points(names, latlon=None, ecef=None):
    """
    Open a web browser to display multiple geographical points on Bing Maps.

    This function supports displaying points using either Latitude/Longitude (latlon) or
    Earth-Centered Earth-Fixed (ECEF) coordinates, although ECEF is currently not implemented.

    Args:
        names (list): A list of names corresponding to each geographical point.
        latlon (list, tuple, np.ndarray, or QuantityFrame, optional): A collection of
                Latitude/Longitude pairs. Each pair should be in the form (latitude, longitude).
                This can be a list, tuple, numpy array, or QuantityFrame.
        ecef (NotImplemented): Future support for ECEF coordinates.

    Raises:
        NotImplementedError: If 'ecef' is provided or 'latlon' is an unsupported type.
        ValueError: If neither 'latlon' nor 'ecef' is provided.

    Returns:
        None
    """
    if latlon is not None:
        if isinstance(latlon, (list, tuple)):
            latlon = np.array(latlon)

        if isinstance(latlon, QuantityFrame):
            pass  # QuantityFrame is already in the desired format
        elif isinstance(latlon, np.ndarray):
            latlon = QuantityFrame({
                "latitude/deg":  latlon[:, 0],
                "longitude/deg": latlon[:, 1]})
        else:
            raise NotImplementedError("The provided 'latlon' type is not supported.")
    elif ecef is not None:
        raise NotImplementedError("ECEF coordinate handling is not yet implemented.")
    else:
        raise ValueError("No coordinate given.")

    uri_components = []

    for idx, coord in enumerate(latlon.iloc):
        lat = coord.qelem("latitude").magnitude
        lon = coord.qelem("longitude").magnitude
        name = quote(str(names[idx]), safe="")
        uri_components.append(f"point.{lat}_{lon}_{name}")

    uri = f"bingmaps:?collection={'~'.join(uri_components)}"
    webbrowser.open(uri)
