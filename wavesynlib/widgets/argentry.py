from tkinter import Frame
from tkinter.ttk import Label, Entry, Button



class ArgEntry(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__namelabel = Label(self)
        self.__namelabel.pack(expand='yes', fill='x')
        self.__entry = Entry(self)
        self.__entry.pack(side='left', expand='yes', fill='x')
        self.__btn = Button(self)
        self.__btn.pack(side='right')
        self.__btn['state'] = 'disabled'
        
        
    @property
    def entry(self):
        return self.__entry
    
    
    @property
    def entry_text(self):
        return self.__entry.get()
    
    
    @entry_text.setter
    def entry_text(self, value):
        self.__entry.delete(0, 'end')
        self.__entry.insert(0, value)
    
    
    @property
    def button(self):
        return self.__btn
        
        
    @property
    def arg_name(self):
        return self.__namelabel['text']
    
    
    @arg_name.setter
    def arg_name(self, val):
        self.__namelabel['text'] = val
        
        
    @property
    def arg_value(self):
        return self.__entry.get()
    
    
    @arg_value.setter
    def arg_value(self, val):
        self.__entry.delete(0, 'end')
        self.__entry.insert(0, val)
                
