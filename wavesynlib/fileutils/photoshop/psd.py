import struct

import numpy as np
from PIL import Image
import time

from .packbits import packbits


_head_def = ">4cH6cHIIHH"



def get_image_matrix(psd_file):
    psd_file.seek(0)
    head = psd_file.read(struct.calcsize(_head_def))
    head = struct.unpack(_head_def, head)

    n_ch = head[11]
    height = head[12]
    width = head[13]
    pixel_num = width * height
    color_mode_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(color_mode_len, 1)
    image_res_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(image_res_len, 1)
    layer_info_len = struct.unpack(">I", psd_file.read(4))[0]

    psd_file.seek(layer_info_len, 1)
    compress_type = struct.unpack(">H", psd_file.read(2))[0]

    if compress_type == 0: # RAW
        buf_size = height*width*3 # 3 channels, RGB
        buf = psd_file.read(buf_size)
        pixels = np.frombuffer(buf, dtype="uint8")
    elif compress_type == 1: # RLE
        scan_line_counts = struct.unpack(">"+"H"*height*n_ch, psd_file.read(2*height*n_ch))
        buf_size = sum(scan_line_counts[:(height*3)]) # 3 channels, RGB
        buf = psd_file.read(buf_size)
        pixels = packbits(buf, pixel_num*3)
    else:
        raise NotImplementedError("Not implemented compression type.")
    imgmtx = pixels.reshape(3, height, width).transpose([1, 2, 0])
    return imgmtx



def get_pil_image(psd_file):
    return Image.fromarray(get_image_matrix(psd_file))


