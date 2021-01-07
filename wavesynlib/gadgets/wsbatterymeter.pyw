# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:34:07 2017

@author: Feng-cong Li
"""
import os
from pathlib import Path

from tkinter import Tk, Label
import ctypes as ct
from comtypes import client

from wavesynlib.widgets.tk.taskbaricon import TaskbarIcon
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.wmi import WQL
from wavesynlib.interfaces.os.windows.processes.utils import singleton

    
    
class Battery:
    def __init__(self):
        loc = client.CreateObject('WbemScripting.SWbemLocator')
        service = loc.ConnectServer('.')
        self.__wql = WQL(service)
        
    
    @property
    def percent(self):
        items = self.__wql.query("SELECT EstimatedChargeRemaining FROM Win32_Battery")
        val = 0
        for item in items:
            val = item.Properties_['EstimatedChargeRemaining'].Value
        return int(val)
    
    
    @property
    def status(self):
        items = self.__wql.query('SELECT BatteryStatus FROM Win32_Battery')
        val = 10
        for item in items:
            val = item.Properties_['BatteryStatus'].Value
        return int(val)
        
        


APPID = u'BCE44D5F-8274-432F-9164-3406EDFF8900'

def main(): 
    if not singleton(APPID):
        return
    
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    my_dir = Path(__file__).parent
    icon_charge = my_dir/'batterymeter_charge.ico'
    icon_discharge = my_dir/'batterymeter_discharge.ico'
    root    = Tk()
    root.iconbitmap(default=icon_discharge)
    label   = Label()
    label.pack()
    tb_icon  = TaskbarIcon(root) 
    battery = Battery()
    
    timer = TkTimer(widget=root, interval=5000) # No Config Dialog
    
    @timer.add_observer   
    def show_percent_status(event):
        percent = battery.percent
        status = battery.status
        if status in (1, 3, 4, 5, 10, 11):
            root.iconbitmap(default=icon_discharge)
        else:
            root.iconbitmap(default=icon_charge)
        label['text']   = f'Battery: {percent}%'
        root.title(f'Battery {percent}%')
        tb_icon.progress = percent        
        if 10 <= percent <= 30:
            state = TBPFLAG.TBPF_PAUSED
        elif percent < 10:
            state = TBPFLAG.TBPF_ERROR
        else:
            state = TBPFLAG.TBPF_NORMAL
        tb_icon.state = state

    timer.active = True
    root.mainloop()



if __name__ == '__main__':
    main()
