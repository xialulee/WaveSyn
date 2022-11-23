# -*- coding: utf-8 -*-
"""
Created on Wed Dec 26 21:05:55 2018

@author: Feng-cong Li
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, WaveSynScriptAPI, code_printer
from .utils import get_pid_from_hwnd, run_as_admin


class Utils(ModelNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @WaveSynScriptAPI
    def run_as_admin(self, executable, parameters):
        return run_as_admin(executable, parameters)

    @WaveSynScriptAPI
    def get_pid_from_hwnd(self, hwnd: int) -> int:
        return get_pid_from_hwnd(hwnd)

    @WaveSynScriptAPI
    def get_prop_from_pid(self, prop: str, pid: int) -> Any:
        wmi = self.root_node.interfaces.os.windows.wmi
        result = wmi.query(
            f"SELECT {prop} FROM Win32_Process WHERE ProcessID = {pid}",
            output_format="python")
        return result[0][prop]

    @WaveSynScriptAPI
    def get_prop_from_hwnd(self, prop: str, hwnd: int) -> Any:
        pid = get_pid_from_hwnd(hwnd)
        return self.get_prop_from_pid(prop, pid)

    @WaveSynScriptAPI
    def get_prop_from_foreground(self, prop: str) -> Any:
        hwnd = self.root_node.interfaces.os.windows.window_handle_getter.foreground()
        return self.get_prop_from_hwnd(prop, hwnd)

    @WaveSynScriptAPI
    def get_execpath_from_pid(self, pid: int) -> Path:
        """Get the executable path of the process specified by pid.
    pid (int): The PID of the process.

Return Value (Path): The path of the executable."""
        return Path(self.get_prop_from_pid('ExecutablePath', pid))

    @WaveSynScriptAPI
    def get_execpath_from_hwnd(self, hwnd: int) -> Path:
        """Get the executable path of the window specified by hwnd.
    hwnd (int): The handle of the window.

Return Value (Path): The path of the executable."""
        return Path(self.get_prop_from_hwnd('ExecutablePath', hwnd))

    @WaveSynScriptAPI
    def get_execpath_from_foreground(self) -> Path:
        """Get the executable path of the foreground window.

Return Value (Path): The path of the executable."""
        return Path(self.get_prop_from_foreground('ExecutablePath'))


class Processes(ModelNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utils = ModelNode(is_lazy=True, class_object=Utils) 
