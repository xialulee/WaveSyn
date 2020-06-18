(require [wavesynlib.languagecenter.hy.cdef [init-cdef struct funcptrtype]])
(init-cdef)

(import [ctypes [WINFUNCTYPE POINTER c_int]])
(import [ctypes.wintypes [WPARAM DWORD]])
(import [.ptrinteger [ULONG_PTR LRESULT]])


(struct KBDLLHOOKSTRUCT [
    DWORD     vkCode
    DWORD     scanCode
    DWORD     flags
    DWORD     time
    ULONG_PTR dwExtraInfo])


(setv KBDLLHOOKSTRUCT* (POINTER KBDLLHOOKSTRUCT))

(funcptrtype WINFUNCTYPE
    LRESULT KHOOKPROC [c_int WPARAM KBDLLHOOKSTRUCT*])
