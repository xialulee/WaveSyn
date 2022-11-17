from wavesynlib.languagecenter.cpp.typeutils import ctype_build, field

from ctypes import (
    c_uint8 as UINT8, 
    c_uint16 as UINT16, 
    c_uint32 as UINT32,
    c_char as char,
    sizeof
)

UBYTE6 = UINT8 * 6
SIGNATURE = char * 4


@ctype_build("struct", pack=1, endian="big")
class HeadStruct:
    signature:  SIGNATURE
    version:    UINT16
    reserved:   UBYTE6
    channels:   UINT16
    height:     UINT32
    width:      UINT32
    depth:      UINT16
    colormode:  UINT16
    

HEADLEN = sizeof(HeadStruct)
HEADBYTES = UINT8 * HEADLEN

@ctype_build("union")
class Head:
    hs:    field(HeadStruct, anonymous=True)
    bytes: HEADBYTES
