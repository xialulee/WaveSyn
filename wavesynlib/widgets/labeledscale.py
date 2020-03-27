from tkinter import Frame
from tkinter.ttk import Label, Scale



class LabeledScale(Frame):
    def __init__(self, *args, **kwargs):
        from_ = kwargs.pop('from_')
        to = kwargs.pop('to')
        name = kwargs.pop('name')
        formatter = kwargs.pop('formatter', str)
        self.__formatter = formatter
        super().__init__(*args, **kwargs)
        
        if name is not None:
            Label(self, text=name).pack(side='left')
        
        self.__scale = Scale(self, from_=from_, to=to, 
                                command=self._on_change)
        self.__scale.pack(side='left', fill='x', expand='yes')
        
        self.__value_label = value_label = Label(self)
        value_label.pack(side='left')
                
    def _on_change(self, val):
        self.__value_label['text']  = self.__formatter(val)
        
    def get(self):
        return self.__scale.get()
        
    def set(self, val):
        return self.__scale.set(val)
