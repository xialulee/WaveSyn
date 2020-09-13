import hy
from .hygeometry import *

from numpy.random import rand 
from numpy import abs, arctan2, hstack, rad2deg, sqrt, vstack
from pandas import DataFrame



def generate_2D_rand_points(
    num_points, 
    x_range, y_range, 
    dataframe=False, 
    range_=False, 
    deg=False, rad=False):

    pos = rand(num_points, 2) - 0.5
    x_range.sort()
    y_range.sort()
    x_len = x_range[1] - x_range[0]
    y_len = y_range[1] - y_range[0]
    x_center = x_range[0] + x_len/2
    y_center = y_range[0] + y_len/2
    pos[:, 0] *= x_len
    pos[:, 0] += x_center
    pos[:, 1] *= y_len
    pos[:, 1] += y_center
    result = pos

    if dataframe:
        head = ["x", "y"]
        columns = pos
        if range_:
            r = sqrt(pos[:, 0]**2 + pos[:, 1]**2)
            head.append("range")
            columns.append(r)
        if deg or rad:
            angle = arctan2(pos[:, 1], pos[:, 0])
            if deg:
                head.append("azimuth (deg)")
                columns.append(rad2deg(angle))
            if rad:
                head.append("azimuth (rad)")
                columns.append(angle)
        result = DataFrame(data=columns, columns=head)

    return result

