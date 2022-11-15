from ctypes import Structure
from ctypes import c_uint32, c_uint64


class Info(Structure):
    _pack_ = 1
    _fields_ = [
        ('tag', c_uint32), 
        ('version', c_uint32), 
        ('flags', c_uint32), 
        ('numIdx', c_uint32), 
        ('dataFileSize', c_uint64)
    ]
