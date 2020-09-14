# -*- coding: utf-8 -*-
"""
Created on Fri April 3 2015

@author: Feng-cong Li
"""

# tk.py backup
## -*- coding: utf-8 -*-
#"""
#Created on Fri Apr 03 15:46:05 2015

#@author: Feng-cong Li
#"""
#import os
#import sys
#import platform
#from importlib import import_module

#import math
#import cmath

#import json
#import random

#from tkinter import Text, Listbox, IntVar, Tk, Toplevel, Canvas
#from tkinter.ttk import Label, Scale, Entry, Button, Scrollbar, Treeview, Combobox
#from tkinter import tix
#from tkinter import Frame
#from tkinter.filedialog import askdirectory, asksaveasfilename

#import PIL
#from PIL import ImageTk
#from PIL import Image

#from functools import partial

#from wavesynlib.languagecenter.utils import (
        #MethodDelegator, FunctionChain, get_caller_dir)
#from wavesynlib.languagecenter.designpatterns import Observable

#__DEBUG__ = False
    


##class FontFrame(Frame, object):
##    def __init__(self, master=None, **kw):
##        Frame.__init__(self, master, **kw)
##        
##        # Font selector
##        selector_frame = LabelFrame(self, text='Font Selector')
##        selector_frame.pack(side=LEFT)
##        # Font face
##        face_frame = LabelFrame(selector_frame, text='Font Face')
##        face_frame.pack()
##        face_list = ScrolledList(face_frame)
##        face_list.pack()
##        fonts = list(tkFont.families(self))
##        fonts.sort()
##        for font in fonts:
##            face_list.insert('end', font)
##        face_list.list_click_callback = self._on_face_select
##        self.face_list = face_list
##            
##        # Font size
##        size_frame = LabelFrame(selector_frame, text='Font Size')
##        size_frame.pack()
##        size_combo = Combobox(size_frame, takefocus=1, stat='readonly')
##        size_combo.pack()
##        size_combo['value'] = range(7, 23)
##        size_combo.current(0)
##        size_combo.bind('<<ComboboxSelected>>', self._on_size_select)
##        self.size_combo = size_combo
##        
##        # Font Sample
##        default_font = ('Courier', 10, tkFont.NORMAL)
##        sample_frame = LabelFrame(self, text='Samples')
##        sample_frame.pack(side=RIGHT, expand=YES, fill=Y)
##        sample_label = Label(sample_frame, 
##                             text='\tabcdefghij\t\n\tABCDEFGHIJ\t\n\t0123456789\t', 
##                             font=default_font)
##        sample_label.pack(expand=YES)
##        self.sample_label = sample_label
##        
##        self.face = default_font[0]
##        self.size = default_font[1]
##        size_combo.current(self.size - 7)
##        
##    def _on_face_select(self, index, face):
##        size = self.size_combo.get()
##        self._set_sample(face, size)
##        
##    def _on_size_select(self, event):
##        self._set_sample(self.face, self.size_combo.get())
##        
##    def _set_sample(self, face, size):
##        self.face = face
##        self.size = size
##        self.sample_label.config(font=(self.face, self.size, tkFont.NORMAL))                            
##            
##def ask_font():
##    win = Toplevel()
##    win.title('Font Dialog')
##
##    buttonFrame = Frame(win)
##    retval = [None]
##    def onClick(ret=None):
##        win.destroy()
##        retval[0] = ret
##    
##    buttonFrame.pack(side='bottom')
##    btnCancel = Button(buttonFrame, text='Cancel', command=lambda: onClick())
##    btnCancel.pack(side=RIGHT)
##    btnOk = Button(buttonFrame, text='OK', command=lambda: onClick((fontFrame.face, fontFrame.size)))
##    btnOk.pack(side=RIGHT)    
##            
##    fontFrame = FontFrame(win)
##    fontFrame.pack()
##    
##    win.focus_set()
##    win.grab_set()
##    win.wait_window()
##    return retval[0]
    
    

##class GUIConsumer(object):                    
##    def __init__(self, producer, timer):
##        if not callable(producer):
##            raise TypeError('producer should be a callable object.')
##        self.__producer = producer           
##        
##        if not isinstance(timer, BaseObservableTimer):
##            raise TypeError('timer should be an instance of a derived class of BaseObservableTimer')
##        self.__active = False
##        self.__timer = timer
##        self.__timer.add_observer(SimpleObserver(self._on_tick))
##        self.__queue = Queue.Queue()
##        self.__producerThread = None        
##        
##    def _on_tick(self):
##        try:
##            while True:
##                data = self.__queue.get_nowait()
##                if self.__active is True:
##                    self.consume(data)
##        except Queue.Empty:
##            pass
##        
##    def _run_producer(self):
##        producer = self.__producer
##        while True:
##            self.__queue.put(producer())
##        
##    def consume(self, data):
##        return NotImplemented
##        
##    @property
##    def active(self):
##        return self.__active
##        
##    @active.setter
##    def active(self, val):
##        self.__active = val
##        if self.__active is True and self.__producerThread is None:
##            self.__producerThread = thread.start_new_thread(self._run_producer)
            

            


            
            
        
        



        
#if __name__ == '__main__':
##    window  = Tk()
##    tree    = ScrolledTree(window)
##    root    = tree.insert('', 'end', text='root')
##    node    = tree.insert(root, END, text='node')
##    window.mainloop()

    ##    window = Tk()
    ##    print (ask_font())
    ##    window.mainloop()


    #root = Tk()
    #json_code = '''[
    #{"name":"alert_button", "class":"Button", "init":{"text":"Alert!"}, "pack":{"fill":"x"}}
#]
    #'''
    #widgets = json_to_tk(root, json_code)
    #widgets['alert_button']['command'] = lambda: print('Alert!')
    #root.mainloop()
    
##    root = tix.Tk()
##    cl = CheckTree(root)
##    cl.pack(expand='yes', fill='both')
##    n1 = cl.add(text='root node')
##    for k in range(32):
##        child = cl.add(parent_node=n1, text='child'+str(k))
##    print(cl.tree_model)
##    root.mainloop()

