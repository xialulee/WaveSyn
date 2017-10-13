# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 23:26:46 2017

@author: Feng-cong Li
"""
import ctypes
from ctypes import byref
from ctypes.wintypes import BOOL, WORD, DWORD, BYTE, SHORT
from wavesynlib.languagecenter.utils import build_struct



@build_struct
def XINPUT_GAMEPAD(
    wButtons: WORD,
    bLeftTrigger: BYTE,
    bRightTrigger: BYTE,
    sThumbLX: SHORT,
    sThumbLY: SHORT,
    sThumbRX: SHORT,
    sThumbRY: SHORT
):pass
        
        

@build_struct
def XINPUT_STATE(
    dwPacketNumber: DWORD,
    Gamepad: XINPUT_GAMEPAD
):pass
        
        
        
@build_struct
def XINPUT_VIBRATION(
    wLeftMotorSpeed: WORD,
    wRightMotorSpeed: WORD
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
    
