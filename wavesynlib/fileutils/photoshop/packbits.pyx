import numpy as np
cimport numpy as np
cimport cython

from libc.stdint cimport uint8_t



@cython.boundscheck(False)
@cython.wraparound(False)
def packbits(const uint8_t [::1] buf, int image_size):
    cdef: 
        int buf_size
        int row_idx
        int size_pos
        int size
        int col
        int len_data
        int cnt
        uint8_t value 
        int error_flag
        np.ndarray[np.uint8_t, ndim=1] pixels 
        uint8_t [::1] pixel_view

    
    pixels = np.empty([image_size], dtype=np.uint8)
    # The continuous of pixels is guaranteed.
    # Use the continous view to avoid unnecessary multiplication 
    # to stride of indexing. 
    pixel_view = pixels

    buf_size = len(buf)
    col = 0
    size_pos = 0
    error_flag = 0
    
    with cython.nogil:
        while size_pos < buf_size-1: 
            # size_pos cannot be the last byte of buf.
            # hence size_pos < buf_size MINUS ONE.
            size = buf[size_pos]
            if size >= 128:
                size = 257 - size
                value = buf[size_pos+1]
                # bounds check for pixel_view
                if col+size > image_size:
                    error_flag = 1
                    break
                for cnt in range(size):
                    pixel_view[col+cnt] = value
                size_pos += 2
            else:
                size += 1
                if col+size > image_size:
                    error_flag = 1
                    break
                if size_pos+1+size > buf_size:
                    error_flag = 2
                    break
                for cnt in range(size):
                    pixel_view[col+cnt] = buf[size_pos+1+cnt]
                size_pos += size + 1
            col += size
            
    if error_flag == 1:
        raise IndexError("Pixel array index out of range.")
    elif error_flag == 2:
        raise IndexError("RLE data buf index out of range.")
            
    return pixels  