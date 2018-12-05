# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 17:16:04 2018

@author: Feng-cong Li
"""
from wavesynlib.interfaces.os.windows.xinput.utils import *
from wavesynlib.interfaces.os.windows.xinput.constants import *
from wavesynlib.interfaces.os.windows.inputsender.utils import send_key_input



button_consts = {
    'XINPUT_GAMEPAD_DPAD_UP':	    XINPUT_GAMEPAD_DPAD_UP,
    'XINPUT_GAMEPAD_DPAD_DOWN':	    XINPUT_GAMEPAD_DPAD_DOWN,
    'XINPUT_GAMEPAD_DPAD_LEFT':	    XINPUT_GAMEPAD_DPAD_LEFT,
    'XINPUT_GAMEPAD_DPAD_RIGHT':	XINPUT_GAMEPAD_DPAD_RIGHT,
    'XINPUT_GAMEPAD_START':	        XINPUT_GAMEPAD_START,
    'XINPUT_GAMEPAD_BACK':	        XINPUT_GAMEPAD_BACK,
    'XINPUT_GAMEPAD_LEFT_THUMB':	XINPUT_GAMEPAD_LEFT_THUMB,
    'XINPUT_GAMEPAD_RIGHT_THUMB':	XINPUT_GAMEPAD_RIGHT_THUMB,
    'XINPUT_GAMEPAD_LEFT_SHOULDER':	XINPUT_GAMEPAD_LEFT_SHOULDER,
    'XINPUT_GAMEPAD_RIGHT_SHOULDER':XINPUT_GAMEPAD_RIGHT_SHOULDER,
    'XINPUT_GAMEPAD_A':	            XINPUT_GAMEPAD_A,
    'XINPUT_GAMEPAD_B':	            XINPUT_GAMEPAD_B,
    'XINPUT_GAMEPAD_X':	            XINPUT_GAMEPAD_X,
    'XINPUT_GAMEPAD_Y':	            XINPUT_GAMEPAD_Y
}



def do(keymap):
    current = set()
    packet_number = -1
    while True:
        state = get_state(0)
        if packet_number == state.dwPacketNumber:
            continue
        else:
            packet_number = state.dwPacketNumber
        buttons = state.Gamepad.wButtons
        for name in button_consts:
            if button_consts[name].value & buttons:
                if name not in current:
                    current.add(name)
                    if name in keymap:
                        send_key_input(keymap[name], press=True)
            else:
                if name in current:
                    current.remove(name)
                    if name in keymap:
                        send_key_input(keymap[name], release=True)
                    
                    
                    
if __name__ == '__main__':
    keymap = {
        'XINPUT_GAMEPAD_DPAD_UP': 0x57, #w
        'XINPUT_GAMEPAD_DPAD_DOWN': 0x53, #s
        'XINPUT_GAMEPAD_DPAD_LEFT': 0x41, #a
        'XINPUT_GAMEPAD_DPAD_RIGHT': 0x44, #d
        'XINPUT_GAMEPAD_A': 0x48, #h
        'XINPUT_GAMEPAD_B': 0x4c, #l
        'XINPUT_GAMEPAD_X': 0x4a, #j
        'XINPUT_GAMEPAD_Y': 0x4b #k
    }
    
    do(keymap)
    