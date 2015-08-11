# 2013.09.20 PM 02:00
# taskbarmanager.py
# python 2.7
# xialulee

from comtypes import *
from ctypes import POINTER
from ctypes.wintypes import HWND, HICON, DWORD, UINT, BOOL, LPCWSTR, RECT
ULONGLONG = c_uint64

GUID_CTaskbarList   = GUID('{56FDF344-FD6D-11d0-958A-006097C9A090}')

class TBPFLAG:
    __slots__   = ('TBPF_NOPROGRESS',
                   'TBPF_INDETERMINATE',
                   'TBPF_NORMAL',
                   'TBPF_ERROR',
                   'TBPF_PAUSED'
    )

    TBPF_NOPROGRESS     = 0
    TBPF_INDETERMINATE  = 1
    TBPF_NORMAL         = 2
    TBPF_ERROR          = 4
    TBPF_PAUSED         = 8

class ITaskbarList4(IUnknown):
    _iid_   = GUID('{c43dc798-95d1-4bea-9030-bb99e2983a1a}')
    _methods_   = [
        # ITaskbarList
        COMMETHOD([], HRESULT, 'HrInit'),

        COMMETHOD([], HRESULT, 'AddTab',
            (['in'], HWND, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'DeleteTab',
            (['in'], HWND, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'ActivateTab',
            (['in'], HWND, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'SetActiveAlt',
            (['in'], HWND, 'hwnd')
        ),

        # ITaskbarList2
        COMMETHOD([], HRESULT, 'MarkFullscreenWindow',
            (['in'], HWND, 'hwnd'),
            (['in'], BOOL, 'fFullscreen')
        ),

        # ITaskbarList3
        COMMETHOD([], HRESULT, 'SetProgressValue',
            (['in'], HWND, 'hwnd'),
            (['in'], ULONGLONG, 'ullCompleted'),
            (['in'], ULONGLONG, 'ullTotal')
        ),

        COMMETHOD([], HRESULT, 'SetProgressState',
            (['in'], HWND, 'hwnd'),
            (['in'], c_uint, 'tbpFlags')
        ),

        COMMETHOD([], HRESULT, 'RegisterTab',
            (['in'], HWND, 'hwndTab'),
            (['in'], HWND, 'hwndMDI')
        ),

        COMMETHOD([], HRESULT, 'UnregisterTab',
            (['in'], HWND, 'hwndTab')
        ),

        COMMETHOD([], HRESULT, 'SetTabOrder',
            (['in'], HWND, 'hwndTab'),
            (['in'], HWND, 'hwndInsertBefore')
        ),

        COMMETHOD([], HRESULT, 'SetTabActive',
            (['in'], HWND, 'hwndTab'),
            (['in'], HWND, 'hwndInsertBefore'),
            (['in'], DWORD, 'dwReserved')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarAddButtons',
            (['in'], HWND, 'hwnd'),
            (['in'], UINT, 'cButtons'),
            (['in'], c_voidp, 'pButtons')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarUpdateButtons',
            (['in'], HWND, 'hwnd'),
            (['in'], UINT, 'cButtons'),
            (['in'], c_voidp, 'pButtons')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarSetImageList',
            (['in'], HWND, 'hwnd'),
            (['in'], c_voidp, 'himl')
        ),

        COMMETHOD([], HRESULT, 'SetOverlayIcon',
            (['in'], HWND, 'hwnd'),
            (['in'], HICON, 'hIcon'),
            (['in'], LPCWSTR, 'pszDescription')
        ),

        COMMETHOD([], HRESULT, 'SetThumbnailTooltip',
            (['in'], HWND, 'hwnd'),
            (['in'], LPCWSTR, 'pszTip')
        ),

        COMMETHOD([], HRESULT, 'SetThumbnailClip',
            (['in'], HWND, 'hwnd'),
            (['in'], POINTER(RECT), 'prcClip')
        ),

        # ITaskbarList4
        COMMETHOD([], HRESULT, 'SetTabProperties',
            (['in'], HWND, 'hwndTab'),
            (['in'], c_uint32, 'stpFlags')
        )
    ]