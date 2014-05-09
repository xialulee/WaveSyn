# 2013.09.20 PM 02:00
# taskbarmanager.py
# python 2.7
# xialulee

from comtypes import *

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
            (['in'], c_voidp, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'DeleteTab',
            (['in'], c_voidp, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'ActivateTab',
            (['in'], c_voidp, 'hwnd')
        ),

        COMMETHOD([], HRESULT, 'SetActiveAlt',
            (['in'], c_voidp, 'hwnd')
        ),

        # ITaskbarList2
        COMMETHOD([], HRESULT, 'MarkFullscreenWindow',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_bool, 'fFullscreen')
        ),

        # ITaskbarList3
        COMMETHOD([], HRESULT, 'SetProgressValue',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_uint64, 'ullCompleted'),
            (['in'], c_uint64, 'ullTotal')
        ),

        COMMETHOD([], HRESULT, 'SetProgressState',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_uint, 'tbpFlags')
        ),

        COMMETHOD([], HRESULT, 'RegisterTab',
            (['in'], c_voidp, 'hwndTab'),
            (['in'], c_voidp, 'hwndMDI')
        ),

        COMMETHOD([], HRESULT, 'UnregisterTab',
            (['in'], c_voidp, 'hwndTab')
        ),

        COMMETHOD([], HRESULT, 'SetTabOrder',
            (['in'], c_voidp, 'hwndTab'),
            (['in'], c_voidp, 'hwndInsertBefore')
        ),

        COMMETHOD([], HRESULT, 'SetTabActive',
            (['in'], c_voidp, 'hwndTab'),
            (['in'], c_voidp, 'hwndInsertBefore'),
            (['in'], c_uint32, 'dwReserved')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarAddButtons',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_uint32, 'cButtons'),
            (['in'], c_voidp, 'pButtons')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarUpdateButtons',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_uint32, 'cButtons'),
            (['in'], c_voidp, 'pButtons')
        ),

        COMMETHOD([], HRESULT, 'ThumbBarSetImageList',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_voidp, 'himl')
        ),

        COMMETHOD([], HRESULT, 'SetOverlayIcon',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_voidp, 'hIcon')
        ),

        COMMETHOD([], HRESULT, 'SetThumbnailTooltip',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_voidp, 'pszTip')
        ),

        COMMETHOD([], HRESULT, 'SetThumbnailClip',
            (['in'], c_voidp, 'hwnd'),
            (['in'], c_voidp, 'prcClip')
        ),

        # ITaskbarList4
        COMMETHOD([], HRESULT, 'SetTabProperties',
            (['in'], c_voidp, 'hwndTab'),
            (['in'], c_uint32, 'stpFlags')
        )
    ]