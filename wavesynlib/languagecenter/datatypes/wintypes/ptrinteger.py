import ctypes as ct
from ctypes.wintypes import WPARAM

# See https://docs.microsoft.com/en-us/windows/win32/winprog/windows-data-types#long_ptr
# and https://docs.microsoft.com/en-us/cpp/cpp/data-type-ranges?view=vs-2019


PTR_SIZE = ct.sizeof(ct.POINTER(ct.c_int))
PTR_BITS = PTR_SIZE * 8

UINT_PTR = WPARAM

if ct.sizeof(ct.c_long) < PTR_SIZE:
    ULONG_PTR = getattr(ct, f"c_uint{PTR_BITS}")
    LONG_PTR = getattr(ct, f"c_int{PTR_BITS}")
else:
    ULONG_PTR = ct.c_ulong
    LONG_PTR = ct.c_long

LRESULT = LONG_PTR