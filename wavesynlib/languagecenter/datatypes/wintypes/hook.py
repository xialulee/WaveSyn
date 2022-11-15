from ctypes import Structure, WINFUNCTYPE, POINTER, c_int
from ctypes.wintypes import WPARAM, DWORD
from .ptrinteger import ULONG_PTR, LRESULT


class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('vkCode', DWORD), 
        ('scanCode', DWORD), 
        ('flags', DWORD), 
        ('time', DWORD), 
        ('dwExtraInfo', ULONG_PTR)
    ]


KHOOKPROC = WINFUNCTYPE(LRESULT, c_int, WPARAM, POINTER(KBDLLHOOKSTRUCT))
