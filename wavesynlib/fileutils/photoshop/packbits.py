import numpy as np
from numba import njit

@njit
def packbits(buf: bytes, image_size: int):
    buf_size = len(buf)
    col = 0
    size_pos = 0
    error_flag = 0

    pixels = np.empty(image_size, dtype=np.uint8)

    while size_pos < buf_size - 1:
        # size_pos cannot be the last byte of buf.
        size = buf[size_pos]
        if size >= 128:
            size = 257 - size
            value = buf[size_pos + 1]
            # bounds check for pixel_view
            if col + size > image_size:
                error_flag = 1
                break
            for cnt in range(size):
                pixels[col + cnt] = value
            size_pos += 2
        else:
            size += 1
            if col + size > image_size:
                error_flag = 1
                break
            if size_pos + 1 + size > buf_size:
                error_flag = 2
                break
            for cnt in range(size):
                pixels[col + cnt] = buf[size_pos + 1 + cnt]
            size_pos += size + 1
        col += size

    if error_flag == 1:
        raise IndexError("Pixel array index out of range.")
    elif error_flag == 2:
        raise IndexError("RLE data buf index out of range.")

    return pixels
