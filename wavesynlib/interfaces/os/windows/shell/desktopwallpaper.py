# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 14:34:51 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from comtypes import *
from ctypes import POINTER
from ctypes.wintypes import UINT, BOOL, LPCWSTR, LPWSTR, RECT, COLORREF


CLSID_DesktopWallpaper = GUID("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}")


# comtypes doc:
# Since the COM internal reference count is handled automatically by comtypes, 
# there is no need to call the first two methods (AddRef, Release).

class IDesktopWallpaper(IUnknown):
    _iid_ = GUID("{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}")
    _methods_ = [
        COMMETHOD([], HRESULT, 'SetWallpaper', 
            (['in'], LPCWSTR, 'monitorID'), 
            (['in'], LPCWSTR, 'wallpaper')
        ),
        
        COMMETHOD([], HRESULT, 'GetWallpaper',
            (['in'], LPCWSTR, 'monitorID'),
            (['out'], POINTER(LPWSTR), 'wallpaper')
        ),
        
        COMMETHOD([], HRESULT, 'GetMonitorDevicePathAt',
            (['in'], UINT, 'monitorIndex'),
            (['out'], POINTER(LPWSTR), 'monitorID')
        ),
        
        COMMETHOD([], HRESULT, 'GetMonitorDevicePathCount',
            (['out'], POINTER(UINT), 'count')
        ),
        
        COMMETHOD([], HRESULT, 'GetMonitorRECT',
            (['in'], LPCWSTR, 'monitorID'),
            (['out'], POINTER(RECT), 'displayRect')
        ),
        
        COMMETHOD([], HRESULT, 'SetBackgroundColor',
            (['in'], COLORREF, 'color')
        ),
        
        COMMETHOD([], HRESULT, 'GetBackgroundColor',
            (['out'], POINTER(COLORREF), 'color')
        ), 
        
        COMMETHOD([], HRESULT, 'SetPosition',
            (['in'], UINT, 'position')
        ),
        
        COMMETHOD([], HRESULT, 'GetPosition',
            (['out'], POINTER(UINT), 'position')
        ),
        
        COMMETHOD([], HRESULT, 'SetSlideshow',
            (['in'], c_voidp, 'items')
        ),
        
        COMMETHOD([], HRESULT, 'GetSlideshow',
            (['out'], c_voidp, 'items')
        ),
        
        COMMETHOD([], HRESULT, 'SetSlideshowOptions',
            (['in'], UINT, 'options'),
            (['in'], UINT, 'slideshowTick')
        ),
        
        COMMETHOD([], HRESULT, 'GetSlideshowOptions',
            (['out'], POINTER(UINT), 'options'),
            (['out'], POINTER(UINT), 'slideshowTick')
        ),
        
        COMMETHOD([], HRESULT, 'AdvanceSlideshow',
            (['in'], LPCWSTR, 'monitorID'),
            (['in'], UINT, 'direction')
        ), 
        
        COMMETHOD([], HRESULT, 'GetStatus',
            (['out'], POINTER(UINT), 'state')
        ), 
        
        COMMETHOD([], HRESULT, 'Enable',
            (['in'], BOOL, 'enable')
        )
    ]