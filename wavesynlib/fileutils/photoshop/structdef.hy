(require [wavesynlib.languagecenter.hy.cdef [*]])
(init-cdef)
(import [ctypes [c_uint8 c_uint16 c_uint32 c_char]])


(setv HEADLEN 26)
(setv HEADBYTES (* c_uint8 HEADLEN))
(setv UB6 (* c_uint8 6))
(setv SIGNATURE (* c_char 4))

(struct [pack 1 endian big] HeadStruct [
    SIGNATURE signature
    c_uint16  version
    UB6       reserved
    c_uint16  channels
    c_uint32  height
    c_uint32  width
    c_uint16  depth
    c_uint16  colormode])


(union Head [
    [anonymous HeadStruct] hs
    HEADBYTES              bytes 
])
