(import [comtypes [STDMETHOD COMMETHOD]])



(defn handle-stdmethod-args [sexpr]
    [(first sexpr) ; Return Type
     (-> sexpr (second) (str) (mangle))  ; Method Name
     (keyword "argtypes") ; Keyword assignment
     (. sexpr [2])])



(defn handle-commethod-args [sexpr]
    (setv desc
        [(first sexpr);  idflag
         (second sexpr); Return Type
         (-> (. sexpr [2]) (str) (mangle)) ; Method Name
    ])
    (setv arg-list [])
    (for [[prop type- name] (-> sexpr (get 3) (partition 3))]
        (arg-list.append `(, [~(str prop)] ~type- ~(-> name (str) (mangle)))))
    (desc.extend arg-list)
    desc)



(defmacro interface [interfacesym bases guid methods]
    `(do
        (import wavesynlib.languagecenter.hy.comobjects)
        (defclass ~interfacesym ~bases [
            -iid- ~guid
            -methods- ~(lfor methinfo methods (do
                (setv methtype (first methinfo)
                      methdesc (-> methinfo (rest) (list)))
                (cond 
                [(= methtype 'STDMETHOD)
                    `(wavesynlib.languagecenter.hy.comobjects.STDMETHOD 
                        ~@(handle-stdmethod-args methdesc))]
                [(= methtype 'COMMETHOD)
                    `(wavesynlib.languagecenter.hy.comobjects.COMMETHOD
                        ~@(handle-commethod-args methdesc))])))])))

; Example:
;(require comdef)
;(import [comtypes [*]])
;(import [ctypes.wintypes [*]])
;
;(setv ULONGLONG c_ulonglong)
;
;
;(setv CLSID-ProgressDialog (GUID "{F8383852-FCD3-11d1-A6B9-006097DF5BD4}"))
;
;(comdef.interface IProgressDialog [IUnknown] 
;    (GUID "{EBBC7C04-315E-11d2-B62F-006097DF5BD4}") [
;    [STDMETHOD HRESULT StartProgressDialog [HWND LPVOID DWORD LPCVOID]]
;    [STDMETHOD HRESULT StopProgressDialog []]
;    [STDMETHOD HRESULT SetTitle [LPCWSTR]]
;    [STDMETHOD HRESULT SetAnimation [HINSTANCE UINT]]
;    [STDMETHOD BOOL HasUserCancelled []]
;    [STDMETHOD HRESULT SetProgress [DWORD DWORD]]
;    [STDMETHOD HRESULT SetProgress64 [ULONGLONG ULONGLONG]]
;    [STDMETHOD HRESULT SetLine [DWORD LPCWSTR BOOL LPCVOID]]
;    [STDMETHOD HRESULT SetCancelMsg [LPCWSTR LPCVOID]]])

