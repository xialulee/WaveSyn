# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 23:26:46 2017

@author: Feng-cong Li
"""
import ctypes
from ctypes import byref
from ctypes.wintypes import BOOL, WORD, DWORD, BYTE, SHORT
from wavesynlib.languagecenter.utils import ctype_build



BATTERY_DEVTYPE_GAMEPAD = BYTE(0)
BATTERY_DEVTYPE_HEADSET = BYTE(1)

BATTERY_LEVEL_EMPTY = BYTE(0)
BATTERY_LEVEL_FULL = BYTE(3)
BATTERY_LEVEL_LOW = BYTE(1)
BATTERY_LEVEL_MEDIUM = BYTE(2)

BATTERY_TYPE_ALKALINE = BYTE(2)
BATTERY_TYPE_DISCONNECTED = BYTE(0)
BATTERY_TYPE_NIMH = BYTE(3)
BATTERY_TYPE_UNKNOWN = BYTE(0XFF)
BATTERY_TYPE_WIRED = BYTE(1)

XINPUT_GAMEPAD_DPAD_UP = WORD(0x0001)
XINPUT_GAMEPAD_DPAD_DOWN = WORD(0x0002)
XINPUT_GAMEPAD_DPAD_LEFT = WORD(0x0004)
XINPUT_GAMEPAD_DPAD_RIGHT = WORD(0x0008)
XINPUT_GAMEPAD_START = WORD(0x0010)
XINPUT_GAMEPAD_BACK = WORD(0x0020)
XINPUT_GAMEPAD_LEFT_THUMB = WORD(0x0040)
XINPUT_GAMEPAD_RIGHT_THUMB = WORD(0x0080)
XINPUT_GAMEPAD_LEFT_SHOULDER = WORD(0x0100)
XINPUT_GAMEPAD_RIGHT_SHOULDER = WORD(0x0200)
XINPUT_GAMEPAD_A = WORD(0x1000)
XINPUT_GAMEPAD_B = WORD(0x2000)
XINPUT_GAMEPAD_X = WORD(0x4000)
XINPUT_GAMEPAD_Y = WORD(0x8000)



@ctype_build('struct')
def XINPUT_GAMEPAD(
    wButtons: WORD,
    bLeftTrigger: BYTE,
    bRightTrigger: BYTE,
    sThumbLX: SHORT,
    sThumbLY: SHORT,
    sThumbRX: SHORT,
    sThumbRY: SHORT
):pass
        
        

@ctype_build('struct')
def XINPUT_STATE(
    dwPacketNumber: DWORD,
    Gamepad: XINPUT_GAMEPAD
):pass
        
        
        
@ctype_build('struct')
def XINPUT_VIBRATION(
    wLeftMotorSpeed: WORD,
    wRightMotorSpeed: WORD
):pass
        
        
        
@ctype_build('struct')
def XINPUT_BATTERY_INFORMATION(
    BatteryType: BYTE,
    BatteryLevel: BYTE
):pass
        
        
        
xinput = ctypes.windll.xinput1_4



def enable(en):
    en = BOOL(en)
    xinput.XInputEnable(en)



def get_state(user_index):
    user_index = DWORD(user_index)
    state = XINPUT_STATE()
    ret = xinput.XInputGetState(user_index, byref(state))
    if ret:
        raise RuntimeError('Cannot get device state.')
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
    
    