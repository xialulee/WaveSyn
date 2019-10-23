(require [wavesynlib.languagecenter.hy.cdef [make-ptr-type]])
(require [wavesynlib.languagecenter.hy.comdef [interface]])

(import [comtypes [c_uint64 GUID IUnknown HRESULT c_uint c_voidp c_uint32]])
(import [ctypes [POINTER c_ulonglong]])
(import [ctypes.wintypes [HWND HICON DWORD UINT BOOL LPCWSTR RECT]])

(setv ULONGLONG c_ulonglong)
(make-ptr-type RECT)



(interface ITaskbarList [IUnknown]
    (GUID "{56FDF342-FD6D-11D0-958A-006097C9A090}") [
    (COMMETHOD [] HRESULT HrInit [])
    (COMMETHOD [] HRESULT AddTab [in HWND hwnd])
    (COMMETHOD [] HRESULT DeleteTab [in HWND hwnd])
    (COMMETHOD [] HRESULT ActivateTab [in HWND hwnd])
    (COMMETHOD [] HRESULT SetActiveAlt [in HWND hwnd])])



(interface ITaskbarList2 [ITaskbarList]
    (GUID "{602D4995-B13A-429B-A66E-1935E44F4317}") [
    (COMMETHOD [] HRESULT MarkFullscreenWindow [
        in HWND hwnd
        in BOOL fFullscreen])])



(interface ITaskbarList3 [ITaskbarList2]
    (GUID "{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}") [
    
    (COMMETHOD [] HRESULT SetProgressValue [
        in HWND hwnd
        in ULONGLONG ullCompleted
        in ULONGLONG ullTotal])

    (COMMETHOD [] HRESULT SetProgressState [
        in HWND hwnd
        in c_uint tbpFlags])

    (COMMETHOD [] HRESULT RegisterTab [
        in HWND hwndTab
        in HWND hwndMDI])

    (COMMETHOD [] HRESULT UnregisterTab [in  HWND  hwndTab]) 

    (COMMETHOD [] HRESULT SetTabOrder [
        in HWND  hwndTab 
        in HWND  hwndInsertBefore]) 

    (COMMETHOD [] HRESULT SetTabActive [
        in HWND  hwndTab 
        in HWND  hwndInsertBefore
        in DWORD  dwReserved]) 

    (COMMETHOD [] HRESULT ThumbBarAddButtons [
        in HWND  hwnd
        in UINT  cButtons 
        in c_voidp  pButtons]) 

    (COMMETHOD [] HRESULT ThumbBarUpdateButtons [
        in HWND hwnd
        in UINT cButtons
        in c_voidp pButtons]) 

    (COMMETHOD [] HRESULT ThumbBarSetImageList [
        in HWND hwnd 
        in c_voidp himl]) 

    (COMMETHOD [] HRESULT SetOverlayIcon [ 
        in HWND hwnd
        in HICON hIcon
        in LPCWSTR pszDescription]) 

    (COMMETHOD [] HRESULT SetThumbnailTooltip [
        in HWND hwnd
        in LPCWSTR pszTip]) 

    (COMMETHOD [] HRESULT SetThumbnailClip [
        in HWND hwnd
        in RECT* prcClip]) ])



(interface ITaskbarList4 [ITaskbarList3]
    (GUID "{C43DC798-95D1-4BEA-9030-BB99E2983A1A}") [
    (COMMETHOD [] HRESULT SetTabProperties [
        in HWND hwndTab
        in c_uint32 stpFlags]) ])
					        
						   
