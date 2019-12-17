# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 16:11:07 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division

from six.moves.tkinter import Frame, IntVar, StringVar
from six.moves.tkinter_ttk import Combobox, Checkbutton, Button, Entry
from six import iterkeys

import ctypes as ct
from ctypes import byref
from ctypes import wintypes

from collections import OrderedDict, namedtuple

import threading
# import time
import inspect
from os.path import abspath, dirname, join

from wavesynlib.languagecenter.designpatterns import Observable, SimpleObserver
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.devcomm.oneasyb.spi import USBSPIConverter
from wavesynlib.widgets.tk import Group
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow


#def get_my_dir():
#    return abspath(dirname(inspect.getfile(inspect.currentframe())))
#    
#uis = ct.cdll.LoadLibrary(join(get_my_dir(), 'usb2uis.dll'))
#
## Considering that all the functions in the DLL is CFUNCTYPE, I do not known why they chose WINFUNCTYPE for callbacks.
#USBCallback = ct.WINFUNCTYPE(None, wintypes.BYTE, wintypes.DWORD)
#
#uis.USBIO_SetUSBNotify.argtypes = (ct.c_bool, USBCallback) # restype: void
#
#uis.USBIO_GetMaxNumofDev.restype = ct.wintypes.BYTE # argtypes: void
#
#uis.USBIO_GetSerialNo.argtypes = (wintypes.BYTE, ct.c_char_p)
#uis.USBIO_GetSerialNo.restype = wintypes.BYTE
#
#uis.USBIO_OpenDeviceByNumber.argtypes = (ct.c_char_p,)
#uis.USBIO_OpenDeviceByNumber.restype = wintypes.BYTE
#
#uis.USBIO_GetWorkMode.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE)) # restype: void
#
#uis.USBIO_CloseDevice.argtypes = (wintypes.BYTE,)
#uis.USBIO_CloseDevice.restype = ct.c_bool
#
#uis.USBIO_SPIGetConfig.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE), ct.POINTER(wintypes.DWORD))
#uis.USBIO_SPIGetConfig.restype = ct.c_bool
#
#uis.USBIO_SPISetConfig.argtypes = (wintypes.BYTE, wintypes.BYTE, wintypes.DWORD)
#uis.USBIO_SPISetConfig.restype = ct.c_bool
#
#uis.USBIO_SPIWrite.argtypes = (wintypes.BYTE, ct.POINTER(wintypes.BYTE), wintypes.BYTE, ct.POINTER(wintypes.BYTE), wintypes.WORD)
#uis.USBIO_SPIWrite.restype = ct.c_bool
#
#SERIALNO_LEN = 10 # The length of the converter's serial number
#
#
#_usb_change_event = threading.Event()
#
#@USBCallback
#def _usb_event_callback(x, y):
#    '''The callback function of USB_SetUSBNotify.
#I guess the DLL will create a new thread and call this callback in that thread.
#Consequently, we cannot do anything to vital resources of Python here.'''
#    _usb_change_event.set()
#    
#    
#class DeviceInfo(object):
#    __slots__ = ['handle', 'is_opened', 'is_master', 'CPOL', 'CPHA', 
#                 'baudrate', 'baudrate_range', 'read_timeout', 'write_timeout']
#    
#    def __init__(self, handle=None, is_opened=None, is_master=None, 
#                 CPOL=0, CPHA=0, baudrate=0, baudrate_range=None,
#                 read_timeout=0, write_timeout=0):
#        self.handle = handle
#        self.is_opened = is_opened
#        self.is_master = is_master
#        self.CPOL = CPOL
#        self.CPHA = CPHA
#        self.baudrate = baudrate
#        self.baudrate_range = baudrate_range
#        self.read_timeout = read_timeout
#        self.write_timeout = write_timeout
#
#
#class USBSPIConverter(Observable):    
#    def __init__(self, usb_monitor_timer=None):
#        '''A class abstracts the USB to SPI/I2C/UART board which made by an company named OnEasyB.
#The usb_monitor_timer monitors the USB change event.
#For Tk applications, it can be simply set to None.
#For applications use other GUI frameworks such as Qt/Wx, the corresponding timer should be created and passed to __init__.'''
#        super(USBSPIConverter, self).__init__()
#        self.__dev_serialmap = self._get_dev_serialmap()
#        uis.USBIO_SetUSBNotify(False, _usb_event_callback)
#        
#        if usb_monitor_timer is None:
#            usb_monitor_timer = TkTimer(interval=100)
#        
#        @SimpleObserver 
#        def on_usb_change(*args, **kwargs):
#            '''This observer will be called periodically.
#It will check the Event object set by _usb_event_callback.
#We can do anything here because it is called in the main thread without
#thread safety issues.'''
#            if _usb_change_event.is_set():
#                self.__dev_serialmap = self._get_dev_serialmap()
#                self.notify_observers(self.__dev_serialmap)
#                _usb_change_event.clear()
#                
#        usb_monitor_timer.add_observer(on_usb_change)
#        self.__usb_monitor_timer = usb_monitor_timer
#        usb_monitor_timer.active = True
#        
#    def add_observer(self, observer):
#        '''Unlike add_observer of its base class, this class's add_observer will call the observer's update method.'''
#        super(USBSPIConverter, self).add_observer(observer)
#        observer.update(self.__dev_serialmap)
#        
#    def update(self, command_slot):
#        serialmap = self.__dev_serialmap
#        # print (command_slot)
#        if command_slot.command == 'open':
#            serialno = command_slot.args[0]
#            open_ = command_slot.args[1]
#            if open_:
#                ret = uis.USBIO_OpenDeviceByNumber(serialno)
#                # print(ret)
#                if ret == 0xff:
#                    print('Open Error')
#                baudrate, CPHA, CPOL, read_timeout, write_timeout = self._get_config(serialno)
#                dev_info = serialmap[serialno]
#                dev_info.baudrate = baudrate
#                dev_info.CPHA = CPHA
#                dev_info.CPOL = CPOL
#                dev_info.read_timeout = read_timeout
#                dev_info.write_timeout = write_timeout
#                self.notify_observers(serialmap)
#            else:
#                # I don't know that why there isn't a USBIO_CloseDeviceByNumber
#                uis.USBIO_CloseDevice(serialmap[serialno].handle)
#        elif command_slot.command == 'config':
#            args = command_slot.args
#            self._set_config(*args)
#        elif command_slot.command == 'write':
#            serialno, data = command_slot.args[:2]
#            index = self.__dev_serialmap[serialno].handle
#            ret = uis.USBIO_SPIWrite(index, None, 0, ct.cast(data, ct.POINTER(ct.c_byte)), len(data))
#            print(ret)
#
#        
#    def is_opened(self, serialno):
#        return self.__dev_serialmap[serialno].is_opened
#    
#    def _get_config(self, serialno):
#        index = self.__dev_serialmap[serialno].handle
#        p1, p2 = wintypes.BYTE(), wintypes.DWORD()
#        uis.USBIO_SPIGetConfig(index, byref(p1), byref(p2))
#        p1, p2 = p1.value, p2.value
#        baudrate_range = [200, 400, 600, 800, 
#                          1000, 2000, 4000, 6000, 12000]
#        baudrate = baudrate_range[p1 & 0xf]
#        CPHA = p1 & 0x10 >> 4
#        CPOL = p1 & 0x20 >> 5
#        read_timeout = p2 & 0xffff
#        write_timeout = p2 & 0xffff0000 >> 16
#        return baudrate, CPHA, CPOL, read_timeout, write_timeout
#        
#    def _set_config(self, serialno, is_master, baudrate, CPHA, CPOL, read_timeout, write_timeout):
#        index = self.__dev_serialmap[serialno].handle
#        baudrate_range = [200, 400, 600, 800, 
#                          1000, 2000, 4000, 6000, 12000]
#        baudrate_code = baudrate_range.index(baudrate)
#        timeout_code = (write_timeout<<16) + read_timeout
#        ret = uis.USBIO_SPISetConfig(index, (is_master<<7) + baudrate_code + (CPHA<<4) + (CPOL<<5), timeout_code)
#        # print(ret)
#        
#        
#    @staticmethod
#    def _get_dev_serialmap():
#        buf = (ct.c_char * SERIALNO_LEN)()
#        max_dev_num = uis.USBIO_GetMaxNumofDev()
#        dev_serialmap = OrderedDict()
#        for index in range(max_dev_num):
#            stat = uis.USBIO_GetSerialNo(index, buf)
#            # print('stat=', stat)
#            if stat != 0:
#                is_opened = True if stat==2 else False
#                dev_serialmap[buf.value] = DeviceInfo(
#                    handle=index, 
#                    is_opened=is_opened, 
#                    is_master=None,
#                    CPOL=None, 
#                    CPHA=None, 
#                    baudrate=0,
#                    baudrate_range=[200, 400, 600, 800, 
#                                    1000, 2000, 4000, 6000, 12000])
#        return dev_serialmap


CommandSlot = namedtuple('GUICommandSlot', ['command', 'args'])



# Temporarily used for a interference cancellation circuit
class InstFields(ct.BigEndianStructure):
    _fields_ = [('i_dac', ct.c_uint, 10),
                ('q_dac', ct.c_uint, 10),
                ('freq_range', ct.c_uint, 2),
                ('gain', ct.c_uint, 1),
                ('spare', ct.c_uint, 1)
                ]
                
class Inst(ct.Union):
    _anonymous_ = ('inst_fields', )
    _fields_ = [('inst_bytes', ct.c_ubyte*3),
                ('inst_fields', InstFields)]
# End     



# To Do: on_close: close device automatically.
class USBSPIWindow(TkToolWindow, Observable):
    '''A control panel for USB to SPI converter.'''
        
    def __init__(self, *args, **kwargs):
        TkToolWindow.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        
        self.__serialmap = None
        
        # Temporarily
        self.inst = Inst()
        # End Temporarily
        
        #window = self.tk_object
        tooltab = Frame(self._tool_tabs)
        self._tool_tabs.add(tooltab, text='SPI')
        #tooltab.pack(expand='yes', fill='x')        
        
    # Group OPEN 
        open_group = Group(tooltab)
        open_group.name = 'Open Device'
        open_group.pack(side='left', fill='y', expand='yes')
        
        self.__dev_combo = dev_combo = Combobox(open_group, value=[], takefocus=1, stat='readonly', width=12)
        dev_combo.bind('<<ComboboxSelected>>', self._on_dev_change)
        self.__current_serialno = None
        dev_combo.pack(side='top')
        
        self.__is_opened = IntVar(0)
        self.__open_check = open_check = Checkbutton(open_group, text='Open', 
            variable=self.__is_opened,
            command=self._on_open_click)
        open_check.pack(expand='yes', fill='y', side='top')
    # End Group Open
        
    # Group Parameters
        param_group = Group(tooltab)
        param_group.name = 'Parameters'
        param_group.pack(side='left')
        Button(param_group, text='Configure', command=self._on_param_change).pack(side='bottom')        
        
        param_frame = Frame(param_group)
        param_frame.pack()
        
        self.__CPOL = CPOL = IntVar(0)
        self.__CPHA = CPHA = IntVar(0)
        Checkbutton(param_frame, text='CPOL', variable=CPOL).grid(row=0, column=0)
        Checkbutton(param_frame, text='CPHA', variable=CPHA).grid(row=1, column=0)
        
        self.__baud_combo = baud_combo = Combobox(param_frame, value=[], takefocus=1, stat='readonly', width=8)
        baud_combo.grid(row=0, column=1, columnspan=2)
        
        self.__read_timeout_str = r_timeout = StringVar()
        self.__write_timeout_str = w_timeout = StringVar()
        Entry(param_frame, textvariable=r_timeout, width=5).grid(row=1, column=1)
        Entry(param_frame, textvariable=w_timeout, width=5).grid(row=1, column=2)
    # End Group Parameters
        
    # Write Group
        write_group = Group(tooltab)
        write_group.name = 'Write'
        write_group.pack(side='left', fill='y', expand='yes')
        
        self.__writebuf = writebuf = StringVar()
        Entry(write_group, textvariable=writebuf).pack()
        Button(write_group, text='Write', command=self._on_write_click).pack()
    # End Write Group
        
        self._make_window_manager_tab()
        
        # To Do: a driver group for loading specified spi bus driver
        converter = USBSPIConverter()
        converter.add_observer(self)
        self.add_observer(converter)
                
    def _on_dev_change(self, event): # User selects another device via dev_combo.
        '''Called when user selects another device via dev_combo.'''
        dev_combo = self.__dev_combo
        self.__current_serialno = serialno = dev_combo.get()
        print(serialno)
        self.__is_opened.set(self.__serialmap[serialno].is_opened)
        print(self.__serialmap[serialno].is_opened)
        self.__baud_combo['values'] = self.__serialmap[serialno].baudrate_range
        
    def _on_open_click(self):
        open_or_close = self.__is_opened.get()
        serialno = self.__dev_combo.get()

        with code_printer():
            if open_or_close:
                self.open_device(serialno)
            else:
                self.close_device(serialno)

    @WaveSynScriptAPI        
    def open_device(self, serial_number):
        self.notify_observers(CommandSlot(command='open', 
                                          args=(serial_number, True))) 

    @WaveSynScriptAPI                                          
    def close_device(self, serial_number):
        self.notify_observers(CommandSlot(command='open', 
                                          args=(serial_number, False)))
        
    def _on_param_change(self):
        serialno = self.__dev_combo.get()
        baudrate = int(self.__baud_combo.get())
        CPOL = self.__CPOL.get()
        CPHA = self.__CPHA.get()
        read_timeout = int(self.__read_timeout_str.get())
        write_timeout = int(self.__write_timeout_str.get())
                  
        kwargs = {}
        kwargs['serial_number'] = serialno
        kwargs['is_master'] = True
        kwargs['baudrate'] = baudrate
        kwargs['CPHA'] = CPHA
        kwargs['CPOL'] = CPOL
        kwargs['read_timeout'] = read_timeout
        kwargs['write_timeout'] = write_timeout
        
        with code_printer():
            self.configure_device(**kwargs)
    
    @WaveSynScriptAPI
    def configure_device(self, serial_number, is_master, baudrate, CPHA, CPOL, 
                         read_timeout, write_timeout):
        self.notify_observers(CommandSlot(command='config', 
                                          args=(serial_number, is_master, 
                                                baudrate, CPHA, CPOL, 
                                                read_timeout, write_timeout)))
        
    def _on_write_click(self):
        serialno = self.__dev_combo.get()
        data = self.__writebuf.get()
        if len(data) % 2 != 0:
            data += '0'

        data_list = [int(data[(k*2):(k*2+2)], base=16) for k in range(len(data)//2)]
        with code_printer():
            self.write_bytes(serial_number=serialno, data=data_list)
        
    @WaveSynScriptAPI
    def write_bytes(self, serial_number, data):
        length = len(data)
        buf = (wintypes.BYTE * length)()
        for index, d in enumerate(data):
            if d > 255:
                raise ValueError('Value of bytes should less than 256.')
            buf[index] = d
        self.notify_observers(CommandSlot(command='write', 
                              args=(serial_number, buf)))
            
    def update(self, serialmap): # Notice: tk_object also has a method named "update".
        '''Called when the underlying USBSPI class catches an USB change event.'''
        # print(serialmap)
        dev_combo = self.__dev_combo
        current_text = dev_combo.get()
        try:
            current_dev = serialmap[current_text]
            current_index = current_dev.handle
        except KeyError:
            current_index = -1
        dev_combo['values'] = list(iterkeys(serialmap))
        
        if current_index == -1: # which means the current selected device has been plugged out. 
            dev_combo.set('')
        else:
            dev_combo.current(current_index)
            dev_info = serialmap[current_text]
            self.__CPOL.set(dev_info.CPOL)
            self.__CPHA.set(dev_info.CPHA)
            self.__baud_combo.current(current_dev.baudrate_range.index(dev_info.baudrate))
            self.__read_timeout_str.set(str(dev_info.read_timeout))
            self.__write_timeout_str.set(str(dev_info.write_timeout))
            
        self.__serialmap = serialmap
        
    @staticmethod
    def to_bytes(integer):
        if integer < 0:
            raise ValueError('Integer should be non-negative.')
        byte_list = []
        while True:
            byte = integer & 0xFF            
            byte_list.insert(0, byte)
            integer >>= 8
            if integer == 0:
                break
        return byte_list
                                                            
