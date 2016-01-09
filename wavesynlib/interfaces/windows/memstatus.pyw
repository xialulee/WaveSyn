#!/usr/bin/env python

# memstatus.pyw
# 2013.09.21 AM 11:38
# win8 python27
# Feng-cong Li

from Tkinter  import *
from comtypes import *
import ctypes as ct

from wavesynlib.guicomponents                      import tk as tktools
from wavesynlib.interfaces.timer.tk                import TkTimer
from wavesynlib.languagecenter.designpatters       import SimpleObserver
from wavesynlib.interfaces.windows.shell.constants import TBPFLAG


class MEMORYSTATUS(ct.Structure):
    _fields_    = [
        ('dwLength',        ct.wintypes.DWORD),
        ('dwMemoryLoad',    ct.wintypes.DWORD),
        ('dwTotalPhys',     ct.c_size_t),
        ('dwAvailPhys',     ct.c_size_t),
        ('dwTotalPageFile', ct.c_size_t),
        ('dwAvailPageFile', ct.c_size_t),
        ('dwTotalVirtual',  ct.c_size_t),
        ('dwAvailVirtual',  ct.c_size_t)
    ]


APPID = 'wavesyn.interfaces.windows.memstatus'

def main():
    ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    root    = Tk()
    label   = Label()
    label.pack()
    tbIcon  = tktools.TaskbarIcon(root) 
    memstat = MEMORYSTATUS()
    memstat.dwLength    = ct.sizeof(MEMORYSTATUS)

    @SimpleObserver # TkTimer is Observable
    def showMemUsage():
        ct.windll.kernel32.GlobalMemoryStatus(ct.byref(memstat))
        memusage    = memstat.dwMemoryLoad

        label['text']   = 'Memory Usage: {}%'.format(memusage)

        tbIcon.progress = memusage        
        if memusage <= 60:
            state = TBPFLAG.TBPF_NORMAL
        elif 60 <= memusage < 80:
            state = TBPFLAG.TBPF_PAUSED
        else:
            state = TBPFLAG.TBPF_ERROR
        tbIcon.state = state

    timer = TkTimer(widget=root) # No Config Dialog
    timer.add_observer(showMemUsage)
    timer.interval = 2000 #ms
    timer.active = True
    root.mainloop()


if __name__ == '__main__':
    main()
