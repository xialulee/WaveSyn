import hy
import struct
from ctypes import sizeof

import numpy as np
from PIL import Image
import time

from .packbits import packbits
from .structdef import Head



COLORMODE = {
    0: "Bitmap",
    1: "Grayscale",
    2: "Indexed",
    3: "RGB",
    4: "CMYK",
    7: "Multichannel",
    8: "Duotone",
    9: "Lab"}



def get_image_matrix(psd_file, read_channels=-1):
    """\
Get the numpy array of the image in the given psd_file.

psd_file:      a stream object of the psd file.
read_channels: 
    'min': read channels based on colormode (without any alpha channel);
    -1: read all channels;
    a positive integer: read specified number of channels."""
    psd_file.seek(0)
    head = Head()
    head.bytes[:] = psd_file.read(sizeof(Head))

    if head.signature != b"8BPS":
        raise TypeError("Given file is not PSD.")

    n_ch = head.channels

    if read_channels == "min":
        read_channels = {
            0: 1,
            1: 1,
            2: 1,
            3: 3,
            4: 4,
            7: -1,
            8: -1, # Not sure
            9: 3
        }[head.colormode]

    if read_channels > n_ch:
        raise ValueError("Too many channels to read.")
    elif read_channels <= 0:
        read_channels = n_ch

    height = head.height
    width  = head.width
    pixel_num = width * height
    color_mode_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(color_mode_len, 1)
    image_res_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(image_res_len, 1)
    layer_info_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(layer_info_len, 1)
    compress_type = struct.unpack(">H", psd_file.read(2))[0]

    read_ch = read_channels

    if compress_type == 0: # RAW
        buf_size = height*width*read_ch # 3 channels, RGB
        buf = psd_file.read(buf_size)
        pixels = np.frombuffer(buf, dtype="uint8")
    elif compress_type == 1: # RLE
        scan_line_counts = struct.unpack(">"+"H"*height*n_ch, psd_file.read(2*height*n_ch))
        buf_size = sum(scan_line_counts[:(height*read_ch)]) 
        buf = psd_file.read(buf_size)
        pixels = packbits(buf, pixel_num*read_ch)
    else:
        raise NotImplementedError("Not implemented compression type.")
    imgmtx = pixels.reshape(read_ch, height, width).transpose([1, 2, 0])
    return imgmtx, COLORMODE[head.colormode]



def get_pil_image(psd_file, read_channels=-1):
    matrix, colormode = get_image_matrix(psd_file, read_channels)
    return Image.fromarray(matrix), colormode


