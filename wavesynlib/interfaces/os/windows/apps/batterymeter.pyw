# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:34:07 2017

@author: Feng-cong Li
"""
import os

from tkinter import Tk, Label
import ctypes as ct
from comtypes import client

from wavesynlib.guicomponents import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.wmi import WQL
from wavesynlib.interfaces.os.windows.process import singleton
from wavesynlib.languagecenter.utils import get_caller_dir

    
    
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
        


APPID = u'BCE44D5F-8274-432F-9164-3406EDFF8900'

def main(): 
    if not singleton(APPID):
        return
    
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    root.iconbitmap(default=get_caller_dir()/'batterymeter.ico')
    label   = Label()
    label.pack()
    tb_icon  = tktools.TaskbarIcon(root) 
    battery = Battery()
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_percent():
        percent = battery.percent
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
