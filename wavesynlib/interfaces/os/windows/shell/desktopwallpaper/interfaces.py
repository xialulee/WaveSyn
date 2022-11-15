from comtypes import GUID, IUnknown, COMMETHOD, HRESULT, c_voidp
from ctypes import POINTER
from ctypes.wintypes import UINT, BOOL, LPCWSTR, LPWSTR, RECT, COLORREF

COLORREF_PTR = POINTER(COLORREF)
LPWSTR_PTR = POINTER(LPWSTR)
UINT_PTR = POINTER(UINT)
RECT_PTR = POINTER(RECT)

CLSID_DesktopWallpaper = GUID("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}")


class IDesktopWallpaper(IUnknown):
    _iid_ = GUID("{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}")
    _methods_ = [
        COMMETHOD([], HRESULT, "SetWallpaper", 
            (["in"], LPCWSTR, "monitorID"), 
            (["in"], LPCWSTR, "wallpaper")
        ), 
        COMMETHOD([], HRESULT, "GetWallpaper", 
            (["in"], LPCWSTR, "monitorID"), 
            (["out"], LPWSTR_PTR, "wallpaper")
        ),
        COMMETHOD([], HRESULT, "GetMonitorDevicePathAt", 
            (["in"], UINT, "monitorIndex"), 
            (["out"], LPWSTR_PTR, "monitorID")
        ), 
        COMMETHOD([], HRESULT, "GetMonitorDevicePathCount", 
            (["out"], UINT_PTR, "count")
        ), 
        COMMETHOD([], HRESULT, "GetMonitorRECT", 
            (["in"], LPCWSTR, "monitorID"), 
            (["out"], RECT_PTR, "displayRect")
        ), 
        COMMETHOD([], HRESULT, "SetBackgroundColor", 
            (["in"], COLORREF, "color")), 
        COMMETHOD([], HRESULT, "GetBackgroundColor", 
            (["out"], COLORREF_PTR, "color")
        ),
        COMMETHOD([], HRESULT, "SetPosition", 
            (["in"], UINT, "position")
        ), 
        COMMETHOD([], HRESULT, "GetPosition", 
            (["out"], UINT_PTR, "position")
        ), 
        COMMETHOD([], HRESULT, "SetSlideshow", 
            (["in"], c_voidp, "items")
        ), 
        COMMETHOD([], HRESULT, "GetSlideshow", 
            (["out"], c_voidp, "items")
        ), 
        COMMETHOD([], HRESULT, "SetSlideshowOptions", 
            (["in"], UINT, "options"), 
            (["in"], UINT, "slideshowTick")
        ), 
        COMMETHOD([], HRESULT, "GetSlideshowOptions", 
            (["out"], UINT_PTR, "options"), 
            (["out"], UINT_PTR, "slideshowTick")
        ), 
        COMMETHOD([], HRESULT, "AdvanceSlideshow", 
            (["in"], LPCWSTR, "monitorID"), 
            (["in"], UINT, "direction")
        ), 
        COMMETHOD([], HRESULT, "GetStatus", 
            (["out"], UINT_PTR, "state")
        ), 
        COMMETHOD([], HRESULT, "Enable", 
            (["in"], BOOL, "enable")
        )
    ]