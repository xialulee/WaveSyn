from comtypes import (
    c_uint64, GUID, HRESULT, c_uint, c_voidp, c_uint32,
    IUnknown, COMMETHOD)
from ctypes import POINTER, c_ulonglong
from ctypes.wintypes import HWND, HICON, DWORD, UINT, BOOL, LPCWSTR, RECT

ULONGLONG = c_ulonglong
RECT_PTR = POINTER(RECT)



class ITaskbarList(IUnknown):
    _iid_ = GUID("{56FDF342-FD6D-11D0-958A-006097C9A090}")
    _methods_ = [
        COMMETHOD([], HRESULT, "HrInit"), 
        COMMETHOD([], HRESULT, "AddTab", (["in"], HWND, "hwnd")),
        COMMETHOD([], HRESULT, "DeleteTab", (["in"], HWND, "hwnd")), 
        COMMETHOD([], HRESULT, "ActivateTab", (["in"], HWND, "hwnd")), 
        COMMETHOD([], HRESULT, "SetActiveAlt", (["in"], HWND, "hwnd"))
    ]



class ITaskbarList2(ITaskbarList):
    _iid_ = GUID("{602D4995-B13A-429B-A66E-1935E44F4317}")
    _methods_ = [
        COMMETHOD([], HRESULT, "MarkFullscreenWindow", 
            (["in"], HWND, "hwnd"), 
            (["in"], BOOL, "fFullscreen")
        )
    ]



class ITaskbarList3(ITaskbarList2):
    _iid_ = GUID("{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}")
    _methods_ = [
        COMMETHOD([], HRESULT, "SetProgressValue", 
            (["in"], HWND, "hwnd"), 
            (["in"], ULONGLONG, "ullCompleted"), 
            (["in"], ULONGLONG, "ullTotal")
        ),
        COMMETHOD([], HRESULT, "SetProgressState", 
            (["in"], HWND, "hwnd"), 
            (["in"], c_uint, "tbpFlags")
        ), 
        COMMETHOD([], HRESULT, "RegisterTab", 
            (["in"], HWND, "hwndTab"), 
            (["in"], HWND, "hwndMDI")
        ), 
        COMMETHOD([], HRESULT, "UnregisterTab", 
            (["in"], HWND, "hwndTab")
        ), 
        COMMETHOD([], HRESULT, "SetTabOrder", 
            (["in"], HWND, "hwndTab"), 
            (["in"], HWND, "hwndInsertBefore")
        ),
        COMMETHOD([], HRESULT, "SetTabActive", 
            (["in"], HWND, "hwndTab"), 
            (["in"], HWND, "hwndInsertBefore"), 
            (["in"], DWORD, "dwReserved")
        ), 
        COMMETHOD([], HRESULT, "ThumbBarAddButtons", 
            (["in"], HWND, "hwnd"), 
            (["in"], UINT, "cButtons"), 
            (["in"], c_voidp, "pButtons")
        ), 
        COMMETHOD([], HRESULT, "ThumbBarUpdateButtons", 
            (["in"], HWND, "hwnd"), 
            (["in"], UINT, "cButtons"), 
            (["in"], c_voidp, "pButtons")
        ), 
        COMMETHOD([], HRESULT, "ThumbBarSetImageList", 
            (["in"], HWND, "hwnd"), 
            (["in"], c_voidp, "himl")
        ), 
        COMMETHOD([], HRESULT, "SetOverlayIcon", 
            (["in"], HWND, "hwnd"), 
            (["in"], HICON, "hIcon"), 
            (["in"], LPCWSTR, "pszDescription")
        ), 
        COMMETHOD([], HRESULT, "SetThumbnailTooltip", 
            (["in"], HWND, "hwnd"), 
            (["in"], LPCWSTR, "pszTip")
        ), 
        COMMETHOD([], HRESULT, "SetThumbnailClip", 
            (["in"], HWND, "hwnd"), 
            (["in"], RECT_PTR, "prcClip")
        )
    ]



class ITaskbarList4(ITaskbarList3):
    _iid_ = GUID("{C43DC798-95D1-4BEA-9030-BB99E2983A1A}")
    _methods_ = [
        COMMETHOD([], HRESULT, "SetTabProperties", 
            (["in"], HWND, "hwndTab"), 
            (["in"], c_uint32, "stpFlags")
        )
    ]
