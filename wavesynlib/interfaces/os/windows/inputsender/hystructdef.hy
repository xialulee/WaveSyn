(require [wavesynlib.languagecenter.hy.cdef [struct union]])
(import [ctypes.wintypes [WORD DWORD LONG WPARAM]])

; See https://stackoverflow.com/a/13615802.
(setv ULONG_PTR WPARAM)



(struct MOUSEINPUT [
    LONG dx
    LONG dy
    DWORD mouseData
    DWORD dwFlags
    DWORD time
    ULONG_PTR dwExtraInfo])



(struct KEYBDINPUT [
    WORD wVk
    WORD wScan
    DWORD dwFlags
    DWORD time
    ULONG_PTR dwExtraInfo])



(struct HARDWAREINPUT [
    DWORD uMsg
    WORD wParamL
    WORD wParamH])



(union -DUMMYUNIONNAME [
    MOUSEINPUT mi
    KEYBDINPUT ki
    HARDWAREINPUT hi])



;According to Microsoft, INPUT is used by SendInput to store information for 
;synthesizing input events such as keystrokes, mouse movement, and mouse clicks.
;
;Fields:
;    type: DWORD. The type of the input event.
;        0: (INPUT_MOUSE) The event is a mouse event. Corresponding to the mi 
;            field.
;        1: (INPUT_KEYBOARD) The event is a keyboard event. Corresponding to the
;            ki field.
;        2: (INPUT_HARDWARE) The event is a hardware event. Corresponding to the 
;            hi field.
;    mi: MOUSEINPUT. The information about a simulated mouse event.
;    ki: KEYBDINPUT. The information about a simulated keyboard event.
;    hi: HARDWAREINPUT. The information about a simulated hardware event. 
(struct INPUT [
    DWORD type
    [anonymous -DUMMYUNIONNAME] dummy])
