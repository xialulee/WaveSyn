# -*- coding: utf-8 -*-
"""
Created on Thur Feb 25 2016

@author: Feng-cong Li
"""
from ctypes.wintypes import DWORD
from ctypes import c_size_t as size_t
from ctypes import sizeof, byref
from ctypes import windll

from wavesynlib.languagecenter.cpp.typeutils import ctype_build

GlobalMemoryStatus = windll.kernel32.GlobalMemoryStatus


@ctype_build("struct")
class MEMORYSTATUS:
    dwLength:        DWORD 
    dwMemoryLoad:    DWORD 
    dwTotalPhys:     size_t 
    dwAvailPhys:     size_t 
    dwTotalPageFile: size_t 
    dwAvailPageFile: size_t 
    dwTotalVirtual:  size_t 
    dwAvailVirtual:  size_t


def get_memory_usage():
    memstat = MEMORYSTATUS()
    memstat.dwLength = sizeof(MEMORYSTATUS)
    GlobalMemoryStatus(byref(memstat))
    return memstat.dwMemoryLoad

