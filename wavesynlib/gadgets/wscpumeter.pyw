# -*- coding: utf-8 -*-
"""
Created on Sat Mar 04 16:08:52 2017

@author: Feng-cong Li
"""
from pathlib import Path
from tkinter import Tk, Frame, Label, StringVar
from tkinter.ttk import Combobox
import ctypes as ct

import psutil

from wavesynlib.widgets import tk as tktools
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from wavesynlib.interfaces.os.windows.processes.utils import singleton
from wavesynlib.widgets.gaugethreshold import GaugeThreshold
from wavesynlib.widgets.taskbaricon import TaskbarIcon

    
    
def get_cpu_usage(mode):
    if mode == "Average":
        return psutil.cpu_percent()
    percent = psutil.cpu_percent(percpu=True)
    func_dict = {"Max":max, "Min":min}
    return func_dict[mode](percent)



APPID = '02519AC0-8DF8-4BE7-9A3E-56BFF162C7F7'

def main():
    if not singleton(APPID):
        return
    
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root = Tk()
    root.iconbitmap(default=Path(__file__).parent / 'cpumeter.ico')

    label = Label()
    label.pack()

    mode_frame = Frame(root)
    mode_frame.pack()
    Label(mode_frame, text="Mode:").pack(side="left")
    mode = StringVar()
    mode.set("Average")
    Combobox(
        mode_frame, 
        textvariable=mode, 
        value=["Average", "Max", "Min"], 
        takefocus=1, 
        stat="readonly").pack(side="left")
    gauge_threshold = GaugeThreshold(
        root,
        default_range=(60, 80))
    gauge_threshold.pack(expand="yes", fill="x")
    tb_icon  = TaskbarIcon(root) 
    
    timer = TkTimer(widget=root, interval=2000) # No Config Dialog
    
    @timer.add_observer   
    def show_cpu_usage():
        cpu_usage = get_cpu_usage(mode=mode.get())
        label['text']   = f'CPU Usage: {cpu_usage}%'
        root.title(f'CPU {cpu_usage}%')
        tb_icon.progress = cpu_usage
        threshold_list = gauge_threshold.threshold_list        
        if cpu_usage <= threshold_list[0]:
            state = TBPFLAG.TBPF_NORMAL
        elif cpu_usage <= threshold_list[1]:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tb_icon.state = state

    timer.active = True
    root.mainloop()


if __name__ == '__main__':
    main()
