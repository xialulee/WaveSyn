(require [wavesynlib.languagecenter.hy.cdef [compound]])
(import [ctypes [Structure Union]])
(import [ctypes.wintypes [WORD DWORD LONG WPARAM]])
(setv ULONG_PTR WPARAM)



(compound Structure MOUSEINPUT [
    LONG dx
    LONG dy
    DWORD mouseData
    DWORD dwFlags
    DWORD time
    ULONG_PTR dwExtraInfo])



(compound Structure KEYBDINPUT [
    WORD wVk
    WORD wScan
    DWORD dwFlags
    DWORD time
    ULONG_PTR dwExtraInfo])



(compound Structure HARDWAREINPUT [
    DWORD uMsg
    WORD wParamL
    WORD wParamH])



(compound Union -DUMMYUNIONNAME[
    MOUSEINPUT mi
    KEYBDINPUT ki
    HARDWAREINPUT hi])
