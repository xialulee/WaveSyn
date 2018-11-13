(require comdef)
(import [comtypes [*]])
(import [ctypes.wintypes [*]])

(setv ULONGLONG c_ulonglong)


(setv CLSID-ProgressDialog (GUID "{F8383852-FCD3-11d1-A6B9-006097DF5BD4}"))

(comdef.interface IProgressDialog [IUnknown] 
    (GUID "{EBBC7C04-315E-11d2-B62F-006097DF5BD4}") [
    [STDMETHOD HRESULT StartProgressDialog [HWND LPVOID DWORD LPCVOID]]
    [STDMETHOD HRESULT StopProgressDialog []]
    [STDMETHOD HRESULT SetTitle [LPCWSTR]]
    [STDMETHOD HRESULT SetAnimation [HINSTANCE UINT]]
    [STDMETHOD BOOL HasUserCancelled []]
    [STDMETHOD HRESULT SetProgress [DWORD DWORD]]
    [STDMETHOD HRESULT SetProgress64 [ULONGLONG ULONGLONG]]
    [STDMETHOD HRESULT SetLine [DWORD LPCWSTR BOOL LPCVOID]]
    [STDMETHOD HRESULT SetCancelMsg [LPCWSTR LPCVOID]]])

