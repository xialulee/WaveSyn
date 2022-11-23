from __future__ import annotations

from typing import Tuple, List

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



def calc_fit_rect(
        screen_size:  Tuple[int, int], 
        image_size:   Tuple[int, int], 
        return_float: bool = False
    ) -> List[int] | List[float]:
    sw, sh = screen_size
    iw, ih = image_size
    sratio = sw / sh
    iratio = iw / ih
    cx = sw / 2
    cy = sh / 2
    if iratio > sratio:
        scale = sw / iw
        nh = ih * scale
        x = 0
        y = cy - nh / 2
        w = sw
        h = nh
    else:
        scale = sh / ih
        nw = iw * scale
        x = cx - nw / 2
        y = 0
        w = nw
        h = sh
    result = [x, y, w, h]
    if not return_float:
        result = [int(i) for i in result]
    return result
