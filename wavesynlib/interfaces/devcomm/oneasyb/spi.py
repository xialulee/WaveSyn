# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 15:40:21 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division

from os.path import abspath, dirname, join
import inspect

import ctypes as ct
from ctypes import wintypes, byref

from collections import OrderedDict

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
uis.USBIO_GetSerialNo.restype = wintypes.BYTE

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
    
    
class DeviceInfo(object):
    __slots__ = ['handle', 'is_opened', 'is_master', 'CPOL', 'CPHA', 
                 'baudrate', 'baudrate_range', 'read_timeout', 'write_timeout']
    
    def __init__(self, handle=None, is_opened=None, is_master=None, 
                 CPOL=0, CPHA=0, baudrate=0, baudrate_range=None,
                 read_timeout=0, write_timeout=0):
        self.handle = handle
        self.is_opened = is_opened
        self.is_master = is_master
        self.CPOL = CPOL
        self.CPHA = CPHA
        self.baudrate = baudrate
        self.baudrate_range = baudrate_range
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout


class USBSPIConverter(Observable):    
    def __init__(self, usb_monitor_timer=None):
        '''A class abstracts the USB to SPI/I2C/UART board which made by an company named OnEasyB.
The usb_monitor_timer monitors the USB change event.
For Tk applications, it can be simply set to None.
For applications use other GUI frameworks such as Qt/Wx, the corresponding timer should be created and passed to __init__.'''
        super(USBSPIConverter, self).__init__()
        self.__dev_serialmap = self._get_dev_serialmap()
        uis.USBIO_SetUSBNotify(False, _usb_event_callback)
        
        if usb_monitor_timer is None:
            usb_monitor_timer = TkTimer(interval=100)
        
        @SimpleObserver 
        def on_usb_change(*args, **kwargs):
            '''This observer will be called periodically.
It will check the Event object set by _usb_event_callback.
We can do anything here because it is called in the main thread without
thread safety issues.'''
            if _usb_change_event.is_set():
                self.__dev_serialmap = self._get_dev_serialmap()
                self.notify_observers(self.__dev_serialmap)
                _usb_change_event.clear()
                
        usb_monitor_timer.add_observer(on_usb_change)
        self.__usb_monitor_timer = usb_monitor_timer
        usb_monitor_timer.active = True
        
    def add_observer(self, observer):
        '''Unlike add_observer of its base class, this class's add_observer will call the observer's update method.'''
        super(USBSPIConverter, self).add_observer(observer)
        observer.update(self.__dev_serialmap)
        
    def update(self, command_slot):
        serialmap = self.__dev_serialmap
        # print (command_slot)
        if command_slot.command == 'open':
            serialno = command_slot.args[0]
            open_ = command_slot.args[1]
            if open_:
                ret = uis.USBIO_OpenDeviceByNumber(serialno)
                # print(ret)
                if ret == 0xff:
                    raise IOError('Cannot open SPI device {}'.format(serialno))
                baudrate, CPHA, CPOL, read_timeout, write_timeout = self._get_config(serialno)
                dev_info = serialmap[serialno]
                dev_info.is_opened = True
                dev_info.baudrate = baudrate
                dev_info.CPHA = CPHA
                dev_info.CPOL = CPOL
                dev_info.read_timeout = read_timeout
                dev_info.write_timeout = write_timeout
            else:
                # I don't know that why there isn't a USBIO_CloseDeviceByNumber
                uis.USBIO_CloseDevice(serialmap[serialno].handle)
                dev_info = serialmap[serialno].is_opened = False
            self.notify_observers(serialmap)                
        elif command_slot.command == 'config':
            args = command_slot.args
            self._set_config(*args)
        elif command_slot.command == 'write':
            serialno, data = command_slot.args[:2]
            index = self.__dev_serialmap[serialno].handle
            ret = uis.USBIO_SPIWrite(index, None, 0, ct.cast(data, ct.POINTER(ct.c_byte)), len(data))
            print(ret)

        
    def is_opened(self, serialno):
        return self.__dev_serialmap[serialno].is_opened
    
    def _get_config(self, serialno):
        index = self.__dev_serialmap[serialno].handle
        p1, p2 = wintypes.BYTE(), wintypes.DWORD()
        uis.USBIO_SPIGetConfig(index, byref(p1), byref(p2))
        p1, p2 = p1.value, p2.value
        baudrate_range = [200, 400, 600, 800, 
                          1000, 2000, 4000, 6000, 12000]
        baudrate = baudrate_range[p1 & 0xf]
        CPHA = p1 & 0x10 >> 4
        CPOL = p1 & 0x20 >> 5
        read_timeout = p2 & 0xffff
        write_timeout = p2 & 0xffff0000 >> 16
        return baudrate, CPHA, CPOL, read_timeout, write_timeout
        
    def _set_config(self, serialno, is_master, baudrate, CPHA, CPOL, read_timeout, write_timeout):
        index = self.__dev_serialmap[serialno].handle
        baudrate_range = [200, 400, 600, 800, 
                          1000, 2000, 4000, 6000, 12000]
        baudrate_code = baudrate_range.index(baudrate)
        timeout_code = (write_timeout<<16) + read_timeout
        ret = uis.USBIO_SPISetConfig(index, (is_master<<7) + baudrate_code + (CPHA<<4) + (CPOL<<5), timeout_code)
        # print(ret)
        
        
    @staticmethod
    def _get_dev_serialmap():
        buf = (ct.c_char * SERIALNO_LEN)()
        max_dev_num = uis.USBIO_GetMaxNumofDev()
        dev_serialmap = OrderedDict()
        for index in range(max_dev_num):
            stat = uis.USBIO_GetSerialNo(index, buf)
            # print('stat=', stat)
            if stat != 0:
                is_opened = True if stat==2 else False
                dev_serialmap[buf.value] = DeviceInfo(
                    handle=index, 
                    is_opened=is_opened, 
                    is_master=None,
                    CPOL=None, 
                    CPHA=None, 
                    baudrate=0,
                    baudrate_range=[200, 400, 600, 800, 
                                    1000, 2000, 4000, 6000, 12000])
        return dev_serialmap