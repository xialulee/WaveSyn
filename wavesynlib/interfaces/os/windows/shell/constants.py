# -*- coding: utf-8 -*-
"""
Created on Thu Jan 07 15:28:02 2016

@author: Feng-cong Li
"""

PROGDLG_NORMAL          = 0
PROGDLG_MODAL           = 1
PROGDLG_AUTOTIME        = 2
PROGDLG_NOTIME          = 4
PROGDLG_NOMINIMIZE      = 8
PROGDLG_NOPROGRESSBAR   = 0x10
PROGDLG_MARQUEEPROGRESS = 0x20
PROGDLG_NOCANCEL        = 0x40

PDTIMER_RESET           = 1
PDTIMER_PAUSE           = 2
PDTIMER_RESUME          = 3


class TBPFLAG:
    __slots__   = ('TBPF_NOPROGRESS',
                   'TBPF_INDETERMINATE',
                   'TBPF_NORMAL',
                   'TBPF_ERROR',
                   'TBPF_PAUSED'
    )

    TBPF_NOPROGRESS     = 0
    TBPF_INDETERMINATE  = 1
    TBPF_NORMAL         = 2
    TBPF_ERROR          = 4
    TBPF_PAUSED         = 8