from __future__ import annotations

from ctypes.wintypes import WORD, DWORD

from wavesynlib.languagecenter.cpp.typeutils import ctype_build



@ctype_build("struct", pack=1)
class BITMAPFILEHEADER:
    bfType:      WORD
    bfSize:      DWORD
    bfReserved1: WORD
    bfReserved2: WORD
    bfOffBits:   DWORD
