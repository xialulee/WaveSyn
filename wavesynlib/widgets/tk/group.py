from tkinter import Frame
from tkinter.ttk import Label


class Group(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'relief' not in kwargs:
            self['relief'] = 'groove'
        if 'bd' not in kwargs:
            self['bd'] = 2
        label_name = Label(self)
        label_name.pack(side='bottom')
        self.__label_name = label_name

    @property
    def name(self):
        return self.__label_name["text"]

    @name.setter
    def name(self, name):
        self.__label_name['text'] = name
