# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 15:44:38 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division

from six.moves.tkinter import Tk, Frame
from six.moves.tkinter_ttk import Combobox
from six import iterkeys

from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.guicomponents.tk import Group


class USBSPIPanel(Frame, Observable):
    '''A control panel for USB to SPI converter.'''
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        
        open_group = Group(self)
        open_group.name = 'Open Device'
        open_group.pack(side='left')
        self.__dev_combo = dev_combo = Combobox(open_group, value=[], takefocus=1, stat='readonly', width=12)
        self.__current_serialno = None
        dev_combo.pack()
                
    def _on_dev_change(self): # User selects another device via dev_combo.
        '''Called when user selects another device via dev_combo.'''
        dev_combo = self.__dev_combo
        self.__current_serialno = dev_combo.get()
        
    def _on_open_click(self):
        pass
            
    def update(self, serialmap):
        '''Called when the underlying USBSPI class catches an USB change event.'''
        dev_combo = self.__dev_combo
        current_text = dev_combo.get()
        current_index = serialmap.get(current_text, -1)
        dev_combo['values'] = list(iterkeys(serialmap))
        
        if current_index == -1: # which means the current selected device has been plugged out. 
            dev_combo.set('')
        else:
            dev_combo.current(current_index)
                                                            

if __name__ == '__main__':
    root = Tk()
#    combo = Combobox(root, value=[], takefocus=1, stat='readonly', width=12)
#    combo['values'] = ['ABCD', 'EFGH']
#    combo.current(0)
#
#    def combo_change(event):
#        print(event.widget.get(), event.widget.current())
#        
#    combo.bind('<<ComboboxSelected>>', combo_change)
#    
#    combo.pack()
    from wavesynlib.interfaces.devcomm.oneasyb.spi import USBSPIConverter
    converter = USBSPIConverter()
    panel = USBSPIPanel(root)
    panel.pack()
    converter.add_observer(panel)
    root.mainloop()
    