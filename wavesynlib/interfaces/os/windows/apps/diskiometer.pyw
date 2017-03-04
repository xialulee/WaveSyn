# -*- coding: utf-8 -*-
"""
Created on Sat Mar 04 17:05:02 2017

@author: Feng-cong Li
"""
from __future__ import division, print_function, unicode_literals

import os

from six.moves.tkinter import *
import ctypes as ct

from wavesynlib.guicomponents import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.wmi import WQL
from wavesynlib.languagecenter.utils import get_caller_dir

    
    
def get_io_time_percent():
    
    return delta_io / delta_t * 100
    
class DiskTime(object):
    def __init__(self):
        self.__wql = WQL()
        
    
    @property
    def percent(self):
        items = self.__wql.query("SELECT PercentDiskTime FROM Win32_PerfFormattedData_PerfDisk_PhysicalDisk WHERE Name='_Total'")
        val = 0
        for item in items:
            val = item.Properties_['PercentDiskTime'].Value
        return int(val)
        


APPID = 'wavesyn/windows_apps/diskiometer'

def main():
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    root.iconbitmap(default=os.path.join(get_caller_dir(), 'disktimemeter.ico'))
    label   = Label()
    label.pack()
    tb_icon  = tktools.TaskbarIcon(root) 
    disk_time = DiskTime()
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_disk_io():
        percent = disk_time.percent
        label['text']   = 'Disk IO time percent: {}%'.format(percent)
        tb_icon.progress = percent        
        if percent <= 60:
            state = TBPFLAG.TBPF_NORMAL
        elif 60 <= percent < 80:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tb_icon.state = state

    timer.active = True
    root.mainloop()


if __name__ == '__main__':
    main()
