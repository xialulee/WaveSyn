(require [wavesynlib.languagecenter.hy.cdef [init-cdef struct →]])
(init-cdef)
(require [wavesynlib.languagecenter.hy.win32def [import-func]])

(import [ctypes.wintypes [DWORD]])
(import [ctypes [c_size_t :as size_t]])
(import [ctypes [sizeof byref]])

(import-func kernel32 GlobalMemoryStatus)



(struct MEMORYSTATUS [
    DWORD  dwLength
    DWORD  dwMemoryLoad
    size_t dwTotalPhys
    size_t dwAvailPhys
    size_t dwTotalPageFile
    size_t dwAvailPageFile
    size_t dwTotalVirtual
    size_t dwAvailVirtual])



(defn get-memory-usage []
    (setv memstat (MEMORYSTATUS)) 
    (setv memstat.dwLength (sizeof MEMORYSTATUS) ) 
    (GlobalMemoryStatus #→[memstat]) 
    memstat.dwMemoryLoad)