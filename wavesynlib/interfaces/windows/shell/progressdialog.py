# -*- coding: utf-8 -*-
"""
Created on Wed Nov 04 18:50:46 2015

@author: Feng-cong Li
"""
from comtypes import *
from ctypes.wintypes import *

# ULONGLONG is not defined in ctypes.wintypes
ULONGLONG = c_ulonglong

PROGDLG_NORMAL          = 0
PROGDLG_MODAL           = 1
PROGDLG_AUTOTIME        = 2
PROGDLG_NOTIME          = 4
PROGDLG_NOMINIMIZE      = 8
PROGDLG_NOPROGRESSBAR   = 0x10
PROGDLG_MARQUEEPROGRESS = 0x20
PROGDLG_NOCANCEL        = 0x40

PDTIMER_RESET           = 1
PDTIMER_PAUSE           = 2
PDTIMER_RESUME          = 3


CLSID_ProgressDialog = GUID('{F8383852-FCD3-11d1-A6B9-006097DF5BD4}')

class IProgressDialog(IUnknown):
    _iid_   = GUID('{EBBC7C04-315E-11d2-B62F-006097DF5BD4}')
    _methods_   = [
        STDMETHOD(HRESULT, 'StartProgressDialog', argtypes=(HWND, LPVOID, DWORD, LPCVOID)),
        STDMETHOD(HRESULT, 'StopProgressDialog', argtypes=()),
        STDMETHOD(HRESULT, 'SetTitle', argtypes=(LPCWSTR,)),
        STDMETHOD(HRESULT, 'SetAnimation', argtypes=(HINSTANCE, UINT)),
        STDMETHOD(BOOL, 'HasUserCancelled', argtypes=()),
        STDMETHOD(HRESULT, 'SetProgress', argtypes=(DWORD, DWORD)),
        STDMETHOD(HRESULT, 'SetProgress64', argtypes=(ULONGLONG, ULONGLONG)),
        STDMETHOD(HRESULT, 'SetLine', argtypes=(DWORD, LPCWSTR, BOOL, LPCVOID)),
        STDMETHOD(HRESULT, 'SetCancelMsg', argtypes=(LPCWSTR, LPCVOID))
    ]
    
    
if __name__ == '__main__':
    from time import sleep
    pd = CoCreateInstance(CLSID_ProgressDialog, interface=IProgressDialog)
    pd.SetTitle('Test Progress Dialog')
    pd.SetLine(1, 'This is a python description of IProgressDialog.', False, None)
    pd.SetLine(2, 'Use SetLine here.', False, None)
    pd.SetCancelMsg('Cancelled', None)
    pd.StartProgressDialog(None, None, PROGDLG_NORMAL | PROGDLG_AUTOTIME, None)
    
    total = 100
    for i in range(total+1):
        pd.SetProgress(i, total)
        sleep(0.25)
        if pd.HasUserCancelled():
            break
    pd.StopProgressDialog()