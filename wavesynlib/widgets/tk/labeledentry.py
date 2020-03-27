from tkinter import Frame
from tkinter.ttk import Label, Entry



class LabeledEntry(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__label = Label(self)
        self.__label.pack(side='left')
        self.__entry = Entry(self)
        self.__entry.pack(fill='x', expand='yes')
        self.__checker_function = None
        self.__image = None

    @property
    def label(self):
        return self.__label

    @property
    def entry(self):
        return self.__entry

    @property
    def label_text(self):
        return self.__label['text']

    @label_text.setter
    def label_text(self, text):
        self.__label['text']    = text
        
    @property
    def label_image(self):
        return self.__label['image']
        
    @label_image.setter
    def label_image(self, image):
        self.__image = image
        self.__label['image'] = image

    @property
    def entry_text(self):
        return self.__entry.get()

    @entry_text.setter
    def entry_text(self, text):
        self.__entry.delete(0, 'end')
        self.__entry.insert(0, text)
        
    @property
    def entry_variable(self):
        return self.__entry['textvariable']
        
    @entry_variable.setter
    def entry_variable(self, val):
        self.__entry.config(textvariable=val)

    def get_int(self):
        i = self.__entry.get()
        return 0 if not i else int(self.__entry.get())

    def get_float(self):
        return float(self.__entry.get())

    @property
    def label_width(self):
        return self.__label['width']

    @label_width.setter
    def label_width(self, width):
        self.__label['width']   = width

    @property
    def entry_width(self):
        return self.__entry['width']

    @entry_width.setter
    def entry_width(self, width):
        self.__entry['width']   = width

    @property
    def checker_function(self):
        return self.__checker_function

    @checker_function.setter
    def checker_function(self, func):
        self.__checker_function    = func
        self.__entry.config(validate='key', validatecommand=func)
