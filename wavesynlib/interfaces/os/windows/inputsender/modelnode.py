# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 23:00:50 2018

@author: Feng-cong Li
"""
from time import sleep

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.inputsender import utils, constants



name_to_code = {}
for k in range(24):
    name_to_code[f'f{k+1}'] = getattr(constants, f'VK_F{k+1}')
for k in range(10):
    code = ord('0') + k
    name_to_code[chr(code)] = code
for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    code = ord(k)
    name_to_code[k] = code
    name_to_code[k.lower()] = code
for k in ('ctrl', 'control', 'alt', 'menu', 'shift'):
    name_to_code[k] = getattr(constants, f'VK_{k.upper()}')
for k in ('lctrl', 'lcontrol', 'left ctrl', 'left control'):
    name_to_code[k] = constants.VK_LCTRL
for k in ('rctrl', 'rcontrol', 'right ctrl', 'right control'):
    name_to_code[k] = constants.VK_RCTRL
for k in ('lalt', 'lmenu', 'left alt', 'left menu'):
    name_to_code[k] = constants.VK_LALT
for k in ('ralt', 'rmenu', 'right alt', 'right menu'):
    name_to_code[k] = constants.VK_RALT
    


class KeySender(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def send(self, key, modifiers=None, press=False, release=False, interval=0):
        if (not press) and (not release):
            self.send(key, modifiers, press=True)
            if interval > 0:
                sleep(interval)
            self.send(key, modifiers, release=True)
            return        
        
        key = key.lower()
        
        code = name_to_code[key]
            
        if modifiers:
            mod_codes = [name_to_code[m] for m in modifiers]
        else:
            mod_codes = []
            
        def keyact(): 
            utils.send_key_input(code, press=press, release=release)
        
        def modifier_act():
            for modifier in mod_codes:
                utils.send_key_input(modifier, press=press, release=release)
                
        if press:
            modifier_act()
            keyact()
        else:
            keyact()
            modifier_act()
        
        
        
class InputSenders(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_sender = KeySender()
