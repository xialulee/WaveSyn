# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 21:44:05 2017

@author: Feng-cong Li
"""
from __future__ import annotations

import atexit
from ctypes import windll, byref
from ctypes.wintypes import DWORD
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
ShellExecuteW            = windll.shell32.ShellExecuteW
CreateMutexW             = windll.kernel32.CreateMutexW
CloseHandle              = windll.kernel32.CloseHandle
GetLastError             = windll.kernel32.GetLastError
ERROR_ALREADY_EXISTS = 183


def singleton(unique_id: str) -> bool:
# From MSDN:
# If the mutex is a named mutex and the object existed before this function call, 
# the return value is a handle to the existing object, 
# and the GetLastError function returns ERROR_ALREADY_EXISTS.
    mutex = CreateMutexW(None, True, unique_id)
    if not mutex:
        raise ValueError('Mutex creation failed.')
    atexit.register(lambda : CloseHandle(mutex) if mutex else None)
    return ERROR_ALREADY_EXISTS != GetLastError()


def get_pid_from_hwnd(hwnd: int) -> int:
    pid = DWORD()
    GetWindowThreadProcessId(hwnd, byref(pid))
    return pid.value


def run_as_admin(executable, parameters):
    return ShellExecuteW(None, 'runas', executable, parameters, None, 1)
