#!/usr/bin/env python

# memstatus.pyw
# 2013.09.21 AM 11:38
# win8 python27
# xialulee

from taskbarmanager import ITaskbarList4, GUID_CTaskbarList, TBPFLAG
from Tkinter import *
from comtypes import *
import ctypes as ct

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


def main():
    root    = Tk()
    label   = Label()
    label.pack()
    tbm     = CoCreateInstance(GUID_CTaskbarList, interface=ITaskbarList4)
    memstat = MEMORYSTATUS()
    memstat.dwLength    = ct.sizeof(MEMORYSTATUS)

    def show_memusage():
        ct.windll.kernel32.GlobalMemoryStatus(ct.byref(memstat))
        memusage    = memstat.dwMemoryLoad
        hwnd    = ct.windll.user32.GetParent(root.winfo_id())

        label['text']   = 'Memory Usage: {}%'.format(memusage)

        tbm.SetProgressValue(\
            hwnd, \
            memusage, 100\
        )
        if memusage <= 60:
            tbm.SetProgressState(\
                hwnd, \
                TBPFLAG.TBPF_NORMAL \
            )
        elif 60 <= memusage < 80:
            tbm.SetProgressState(\
                hwnd, \
                TBPFLAG.TBPF_PAUSED \
            )
        else:
            tbm.SetProgressState(\
                hwnd, \
                TBPFLAG.TBPF_ERROR \
            )
        root.after(2000, show_memusage)

    show_memusage()
    root.mainloop()


if __name__ == '__main__':
    main()