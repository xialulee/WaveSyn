# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 15:40:21 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division

from os.path import abspath, dirname, join
import inspect

import ctypes as ct
from ctypes import wintypes

from collections import OrderedDict, namedtuple

import threading

from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.interfaces.timer.tk import TkTimer


def get_my_dir():
    return abspath(dirname(inspect.getfile(inspect.currentframe())))

uis = ct.cdll.LoadLibrary(join(get_my_dir(), 'usb2uis.dll'))

# Considering that all the functions in the DLL is CFUNCTYPE, I do not known why they chose WINFUNCTYPE for callbacks.
USBCallback = ct.WINFUNCTYPE(None, wintypes.BYTE, wintypes.DWORD)

uis.USBIO_SetUSBNotify.argtypes = (ct.c_bool, USBCallback) # restype: void

uis.USBIO_GetMaxNumofDev.restype = ct.wintypes.BYTE # argtypes: void

uis.USBIO_GetSerialNo.argtypes = (wintypes.BYTE, ct.c_char_p)
uis.USBIO_GetSerialNo.restypes = wintypes.BYTE

uis.USBIO_OpenDeviceByNumber.argtypes = (ct.c_char_p,)
uis.USBIO_OpenDeviceByNumber.restype = wintypes.BYTE

uis.USBIO_GetWorkMode.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE)) # restype: void

uis.USBIO_CloseDevice.argtypes = (wintypes.BYTE,)
uis.USBIO_CloseDevice.restype = ct.c_bool

uis.USBIO_SPIGetConfig.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE), ct.POINTER(wintypes.DWORD))
uis.USBIO_SPIGetConfig.restype = ct.c_bool

uis.USBIO_SPISetConfig.argtypes = (wintypes.BYTE, wintypes.BYTE, wintypes.DWORD)
uis.USBIO_SPISetConfig.restype = ct.c_bool

uis.USBIO_SPIWrite.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE), wintypes.BYTE, ct.POINTER(wintypes.BYTE), wintypes.WORD)
uis.USBIO_SPIWrite.restype = ct.c_bool

SERIALNO_LEN = 10 # The length of the converter's serial number


_usb_change_event = threading.Event()

@USBCallback
def _usb_event_callback(x, y):
    '''The callback function of USB_SetUSBNotify.
I guess the DLL will create a new thread and call this callback in that thread.
Consequently, we cannot do anything to vital resources of Python here.'''
    _usb_change_event.set()


class USBSPIConverter(Observable):
    DeviceInfo = namedtuple('DeviceInfo', ['handle', 'is_opened'])
    
    def __init__(self, usb_monitor_timer=None):
        '''A class abstracts the USB to SPI/I2C/UART board which made by an company named OnEasyB.
The usb_monitor_timer monitors the USB change event.
For Tk applications, it can be simply set to None.
For applications use other GUI frameworks such as Qt/Wx, the corresponding timer should be created and passed to __init__.'''
        super(USBSPIConverter, self).__init__()
        self.__dev_serialmap = self._get_dev_serialmap()
        uis.USBIO_SetUSBNotify(True, _usb_event_callback)
        
        if usb_monitor_timer is None:
            usb_monitor_timer = TkTimer(interval=100)
        
        @SimpleObserver 
        def on_usb_change(*args, **kwargs):
            '''This observer will be called periodically.
It will check the Event object set by _usb_event_callback.
We can do anything here because it is called in the main thread without
thread safety issues.'''
            if _usb_change_event.is_set():
                self.notify_observers(self._get_dev_serialmap())
                _usb_change_event.clear()
                
        usb_monitor_timer.add_observer(on_usb_change)
        self.__usb_monitor_timer = usb_monitor_timer
        usb_monitor_timer.active = True
        
    def add_observer(self, observer):
        '''Unlike add_observer of its base class, this class's add_observer will call the observer's update method.'''
        super(USBSPIConverter, self).add_observer(observer)
        observer.update(self.__dev_serialmap)
            
    @classmethod
    def _get_dev_serialmap(cls):
        buf = (ct.c_char * SERIALNO_LEN)()
        max_dev_num = uis.USBIO_GetMaxNumofDev()
        print (max_dev_num)
        dev_serialmap = OrderedDict()
        for index in range(max_dev_num):
            print(index)
            if uis.USBIO_GetSerialNo(index, buf):
                dev_serialmap[buf.value] = cls.DeviceInfo(handle=index, is_opened=False)
        return dev_serialmap