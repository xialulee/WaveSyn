import numpy as np
cimport numpy as np
cimport cython

from libc.stdint cimport uint8_t



@cython.wraparound(False)
def packbits(const uint8_t [::1] buf, int image_size):
    cdef int buf_size
    cdef int row_idx
    cdef int size_pos
    cdef int size
    cdef int col
    cdef int len_data
    cdef int cnt
    cdef uint8_t value 
    cdef np.ndarray[np.uint8_t, ndim=1] pixels 
    
    pixels = np.zeros([image_size], dtype=np.uint8)
    buf_size = len(buf)
    col = 0
    size_pos = 0
    
    while size_pos < buf_size:
        size = buf[size_pos]
        if size >= 128:
            size = 257 - size
            value = buf[size_pos+1]
            for cnt in range(size):
                pixels[col+cnt] = value
            size_pos += 2
        else:
            size += 1
            for cnt in range(size):
                pixels[col+cnt] = buf[size_pos+1+cnt]
            size_pos += size + 1

        col += size
            
    return pixels    

