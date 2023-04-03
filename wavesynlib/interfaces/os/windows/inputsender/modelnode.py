# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 23:00:50 2018

@author: Feng-cong Li
"""
from time import sleep

from wavesynlib.languagecenter.wavesynscript import ModelNode, WaveSynScriptAPI, Scripting, code_printer
from wavesynlib.interfaces.os.windows.inputsender import utils, constants

name_to_code = {}

for k in range(1, 25):
    name_to_code[f"f{k}"] = getattr(constants, f"VK_F{k}")

for k in range(10):
    code = ord("0") + k
    name_to_code[chr(code)] = code

for k in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    code = ord(k)
    name_to_code[k] = code
    name_to_code[k.lower()] = code

for k in ["ctrl", "control", "alt", "menu", "shift"]:
    name_to_code[k] = getattr(constants, f"VK_{k.upper()}")

for k in ["lctrl", "lcontrol", "left ctrl", "left control"]:
    name_to_code[k] = constants.VK_LCTRL

for k in ["rctrl", "rcontrol", "right ctrl", "right control"]:
    name_to_code[k] = constants.VK_RCTRL

for k in ["lalt", "lmenu", "left alt", "left menu"]:
    name_to_code[k] = constants.VK_LALT

for k in ["ralt", "rmenu", "right alt", "right menu"]:
    name_to_code[k] = constants.VK_RALT

for k in ["left", "right", "up", "down"]:
    name_to_code[k] = getattr(constants, f"VK_{k.upper()}")



class MouseSender(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @WaveSynScriptAPI
    def click_repeatedly(self, 
            times, 
            absolute = None, 
            dx = 0, dy = 0, 
            delay = 0, interval = 0):
        """\
Left click several times.

times:       how many times to click.
absolute:    the given coordinate is absolute or not.
dx:          x-coordinate.
dy:          y-coordinate.
delay(s):    the click will wait (delay) seconds.
interval(s): the interval between clicks."""
        sleep(delay)
        
        for k in range(times):
            utils.send_mouse_input(dx, dy, "left", absolute)
            sleep(interval)



class KeySender(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, key, modifiers=None, press=None, release=None, interval=0):
        if not (press or release):
            self.send(key, modifiers, press=True)
            if interval > 0: sleep(interval)
            self.send(key, modifiers, release=True)
            return

        key = key.lower()
        code = name_to_code[key]
        if modifiers:
            mod_codes = [name_to_code[m] for m in modifiers]
        else:
            mod_codes = []

        def key_act():
            utils.send_key_input(code, press=press, release=release)

        def modifier_act():
            for modifier in mod_codes:
                utils.send_key_input(modifier, press=press, release=release)

        if press:
            modifier_act()
            key_act()
        else:
            key_act()
            modifier_act()


class _Condition:
    pass


class _DefaultCondition(_Condition):
    pass


class _ExecPathCondition(_Condition):
    def __init__(self, exec_path):
        self.__exec_path = exec_path

    @property
    def exec_path(self):
        return self.__exec_path


class _Setting:
    def __init__(self):
        pass


class _Profile:
    def __init__(self, condition):
        self.__condition = condition
        self.__settings = []

    @property
    def condition(self):
        return self.__condition

    def add_setting(self, setting):
        return self.__settings.append(setting)


class MacroManager(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__profiles = {}
        self.__current_profile = None
        self.__current_setting = None

    def add_profile(self, profile):
        self.__profiles[profile.condition] = profile

    @property
    def _current_profile(self):
        with code_printer(print_=False):
            exec_path = self.root_node.interfaces.os.windows.processes.utils.get_execpath_from_foreground()
        condition = _ExecPathCondition(exec_path)
        return self.__profiles.get(None)

    @property
    def _current_setting(self):
        return None

    def set_trigger(self, slot, hotkey=None):
        pass


class InputSenders(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_sender = KeySender()
        self.mouse_sender = MouseSender()
        self.macro_manager = ModelNode(is_lazy=True, class_object=MacroManager)
