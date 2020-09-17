# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:38:55 2016

@author: Feng-cong Li
"""
import hy
from wavesynlib.widgets.tk.tkbasewindow import TkWindowNode
from wavesynlib.widgets.tk.labeledscale import LabeledScale



class FileSplitDialog(TkWindowNode):
    def __init__(self, *args, **kwargs):
        super(FileSplitDialog, self).__init__(*args, **kwargs)
        mib_scale = LabeledScale(self.tk_object, name=None, 
                                 from_=0, to=100,
                                 formatter=lambda x:'{:d} MiB'.format(int(float(x))))
        mib_scale.pack(expand='yes', fill='both')
        mib_scale.set(0)
        
        
if __name__ == '__main__':
    from Tkinter import Tk
    root = Tk()
    dialog = FileSplitDialog()
    root.mainloop()
