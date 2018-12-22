(require [wavesynlib.languagecenter.hy.cdef [struct]])
(import [ctypes.wintypes [DWORD]])
(import [ctypes [c_size_t :as size_t]])



(struct MEMORYSTATUS [
    DWORD  dwLength
    DWORD  dwMemoryLoad
    size_t dwTotalPhys
    size_t dwAvailPhys
    size_t dwTotalPageFile
    size_t dwAvailPageFile
    size_t dwTotalVirtual
    size_t dwAvailVirtual])

