# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 23:26:46 2017

@author: Feng-cong Li
"""
import ctypes
from ctypes import byref
from ctypes.wintypes import BOOL, DWORD, BYTE

# The following code generates the bytecode file of the 
# structdef.hy which is written in Hy.
# If we import a module written in hy directly in wavesyn,
# it will fail, and I cannot figure out why. 
import os
from pathlib import Path
structdef_path = Path(__file__).parent / 'structdef.hy'
os.system(f'hy {structdef_path}')
# After the bytecode file generated, we can import the module written by hy.
from wavesynlib.interfaces.os.windows.xinput.structdef import (
    XINPUT_STATE, XINPUT_VIBRATION, XINPUT_BATTERY_INFORMATION)

from wavesynlib.interfaces.os.windows.xinput.constants import BATTERY_DEVTYPE_GAMEPAD



xinput = ctypes.windll.xinput1_4



def enable(en):
    en = BOOL(en)
    xinput.XInputEnable(en)



def get_state(user_index):
    user_index = DWORD(user_index)
    state = XINPUT_STATE()
    ret = xinput.XInputGetState(user_index, byref(state))
    if ret:
        raise ValueError('Cannot get device state.')
    return state



def vibrate(user_index, left_motor_speed, right_motor_speed):
    user_index = DWORD(user_index)
    vibration = XINPUT_VIBRATION()
    vibration.wLeftMotorSpeed = left_motor_speed
    vibration.wRightMotorSpeed = right_motor_speed
    xinput.XInputSetState(user_index, byref(vibration))
    
    
    
def get_battery_info(user_index, dev_type=BATTERY_DEVTYPE_GAMEPAD):
    info = XINPUT_BATTERY_INFORMATION()
    user_index = DWORD(user_index)
    if not isinstance(dev_type, BYTE):
        dev_type = BYTE(dev_type)
    xinput.XInputGetBatteryInformation(user_index, dev_type, byref(info))
    return info
    
    
