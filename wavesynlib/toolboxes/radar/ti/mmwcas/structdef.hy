(require [wavesynlib.languagecenter.hy.cdef [*]])
(init-cdef)


(struct [pack 1] Info [
    c_uint32 tag
    c_uint32 version
    c_uint32 flags
    c_uint32 numIdx
    c_uint64 dataFileSize ])
