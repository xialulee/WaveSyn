from tkinter import Frame
from tkinter.ttk import Label, Scale


class LabeledScale(Frame):
    def __init__(self, *args, **kwargs):
        from_ = kwargs.pop('from_')
        to = kwargs.pop('to')
        name = kwargs.pop('name', '')
        formatter = kwargs.pop('formatter', str)
        self.__formatter = formatter
        super().__init__(*args, **kwargs)
        self.__name_label = Label(self, text=name)
        self.__name_label.pack(side='left')
        self.__scale = Scale(self, from_=from_, to=to, command=self._on_change)
        self.__scale.pack(side='left', fill='x', expand='yes')
        self.__value_label = Label(self)
        self.__value_label.pack(side='left')

    def _on_change(self, val):
        self.__value_label['text'] = self.__formatter(val)

    def get(self):
        return self.__scale.get()

    def set(self, val):
        return self.__scale.set(val)

    @property
    def scale(self):
        return self.__scale

    @property
    def name(self):
        return self.__name_label["text"]

    @name.setter
    def name(self, val):
        self.__name_label["text"] = val

    @property
    def scale_value(self):
        return self.get()

    @scale_value.setter
    def scale_value(self, val):
        self.set(val)

    @property
    def value_formatter(self):
        return self.__formatter

    @value_formatter.setter
    def value_formatter(self, val):
        self.__formatter = val
