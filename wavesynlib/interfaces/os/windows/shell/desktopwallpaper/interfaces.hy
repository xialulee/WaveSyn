(require [wavesynlib.languagecenter.hy.cdef [init-cdef make-ptr-type]])
(init-cdef)
(require [wavesynlib.languagecenter.hy.comdef [interface]])

(import [comtypes [GUID IUnknown COMMETHOD HRESULT c_voidp]])
(import [ctypes [POINTER]])
(import [ctypes.wintypes [UINT BOOL LPCWSTR LPWSTR RECT COLORREF]])

(make-ptr-type
    COLORREF
    LPWSTR
    UINT
    RECT)

(setv CLSID-DesktopWallpaper (GUID "{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}") )



(interface IDesktopWallpaper [IUnknown]
    (GUID "{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}") [

    (COMMETHOD [] HRESULT SetWallpaper [
        in LPCWSTR monitorID
        in LPCWSTR wallpaper]) 

    (COMMETHOD [] HRESULT GetWallpaper [
        in LPCWSTR monitorID
        out LPWSTR* wallpaper])
        
    (COMMETHOD [] HRESULT GetMonitorDevicePathAt [
        in UINT monitorIndex
        out LPWSTR* monitorID])
        
    (COMMETHOD [] HRESULT GetMonitorDevicePathCount [
        out UINT* count]) 
        
    (COMMETHOD [] HRESULT GetMonitorRECT [
        in LPCWSTR monitorID
        out RECT* displayRect]) 
        
    (COMMETHOD [] HRESULT SetBackgroundColor [
        in COLORREF color] )
        
    (COMMETHOD [] HRESULT GetBackgroundColor [
        out COLORREF* color]) 
        
    (COMMETHOD [] HRESULT SetPosition [
        in UINT position]) 
        
    (COMMETHOD [] HRESULT GetPosition [
        out UINT* position])
        
    (COMMETHOD [] HRESULT SetSlideshow [
        in c_voidp items])
        
    (COMMETHOD [] HRESULT GetSlideshow [
        out c_voidp items])
        
    (COMMETHOD [] HRESULT SetSlideshowOptions [
        in UINT options
        in UINT slideshowTick])
        
    (COMMETHOD [] HRESULT GetSlideshowOptions [
        out UINT* options
        out UINT* slideshowTick])
        
    (COMMETHOD [] HRESULT AdvanceSlideshow [
        in LPCWSTR monitorID
        in UINT direction])
        
    (COMMETHOD [] HRESULT GetStatus [
        out UINT* state])
        
    (COMMETHOD [] HRESULT Enable [
        in BOOL enable]) ])
