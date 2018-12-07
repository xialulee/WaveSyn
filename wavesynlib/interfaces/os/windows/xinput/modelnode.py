# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 20:12:50 2018

@author: Feng-cong Li
"""
import _thread as thread

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.xinput import utils, constants



class Gamepads(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__op_map = [{}, {}, {}, {}]
        self.__button_names = tuple(
            name[len('XINPUT_GAMEPAD_'):].lower() \
                for name in dir(constants) \
                if name.startswith('XINPUT_GAMEPAD_') )
        self.__stop_flag = [True]
        self.__lock = thread.allocate_lock()
        self.__button_state = [[], [], [], []]
        
        
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
        
        
    def get_availability(self):
        return [self.is_available(uid) for uid in range(4)]
    
    
    def get_button_names(self):
        return self.__button_names
    
    
    def button_to_key(self, user_index, button_name, key_name, modifiers=None):
        action = {'type':'key', 'name':key_name, 'modifiers':modifiers}
        for type_ in ('press', 'release'):
            self.set_button_map(user_index, button_name, type_, action)
    
    
    def set_button_map(self, user_index, button, type_, action):
        '''\
Map the specified button to an action.

user_index: the ID of the gamepad;
button: the name of the button (call get_button_names to get available names);
type_: "press" or "release", indicating the action trigger by button press or
    button release;
action: the action trigger by the gamepad button, action can be a string
    indicating a name of the keyboard, a list indicating a chain events or
    a callable object.
'''
        if not callable(action):
            if isinstance(action, dict):
                if action['type'].lower() == 'key':
                    key_name = action['name']
                    if 'modifiers' in action:
                        mods = action['modifiers']
                    else:
                        mods = None
                    kwargs = {'modifiers':mods}
                    if type_ == 'press':
                        kwargs['press'] = True
                    elif type_ == 'release':
                        kwargs['release'] = True
                    def action():
                        self.root_node.interfaces.os.windows.\
                        input_senders.key_sender.send(key_name, **kwargs)

        with self.__lock:
            if button in self.__op_map[user_index]:
                self.__op_map[user_index][button][type_] = action
            else:
                self.__op_map[user_index][button] = {type_:action}
            
            
    def get_button_map(self):
        return self.__op_map
        
        
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
    
    
    def start_listening(self):
        if not self.__stop_flag[0]:
            return
        self.__stop_flag[0] = False
        
        lock = self.__lock
        
        @self.root_node.thread_manager.new_thread_do
        def listen():
            packet_number = -1
            current = [set(), set(), set(), set()]
            
            while True:
                with lock:
                    if self.__stop_flag[0]:
                        break
                    
                availability = self.get_availability()
                for uid in range(4):
                    if not availability[uid]:
                        continue
                    
                    state = utils.get_state(uid)
                    if packet_number == state.dwPacketNumber:
                        continue
                    else:
                        packet_number = state.dwPacketNumber
                        
                    buttons = state.Gamepad.wButtons
                    
                    with lock:     
                        names = self.__op_map[uid]                               
                        for name in names:
                            act_info = names[name]
                            constant = getattr(
                                constants,
                                f'XINPUT_GAMEPAD_{name.upper()}').value
                            if constant & buttons:
                                if name not in current[uid]: # Pressed
                                    current[uid].add(name)
                                    if 'press' in act_info:
                                        action = act_info['press']
                                        self.root_node.\
                                        thread_manager.\
                                        main_thread_do(block=False)(action)
                            else:
                                if name in current[uid]: # Released
                                    current[uid].remove(name)
                                    if 'release' in act_info:
                                        action = act_info['release']
                                        self.root_node.\
                                        thread_manager.\
                                        main_thread_do(block=False)(action)
    
    
    def stop_listening(self):
        with self.__lock:
            self.__stop_flag[0] = True
    


class XInput(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gamepads = Gamepads()        
