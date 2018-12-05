# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 20:12:50 2018

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.xinput import utils



class Gamepad(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def enable(self, en):
        utils.enable(en)        
        
        
    def viberate(self, user_index, left_motor_percent, right_motor_percent):
        if not (0<=left_motor_percent<=100 and 0<=right_motor_percent<=100):
            raise ValueError('''\
Valid motor usage percent should be in [0, 100].''')
        # percent to speed
        p2s = lambda percent: int(percent/100*0xffff)
        utils.vibrate(
            user_index, 
            p2s(left_motor_percent), 
            p2s(right_motor_percent))
        
        
    def is_available(self, user_index):
        try:
            utils.get_state(user_index)
            return True
        except ValueError:
            return False
        
        
    def get_state(self, user_index):
        return utils.get_state(user_index)
        
        
    def get_battery_info(self, user_index):
        return utils.get_battery_info(user_index)



class XInput(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gamepad = Gamepad()        