from tkinter import Frame
from tkinter.ttk import Label, Entry
from .utils.loadicon import load_icon


class LabeledEntry(Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        (label := Label(self)).pack(side="left")
        self.__label = label
        (entry := Entry(self)).pack(side="left", fill="x", expand="yes")
        self.__entry = entry
        self.__checker_function = None
        self.__image = None

    @property
    def label(self) -> Label:
        return self.__label

    @property
    def entry(self) -> Entry:
        return self.__entry
        
    @property
    def label_text(self) -> str:
        return self.__label["text"]
    
    @label_text.setter
    def label_text(self, text: str) -> None:
        self.__label["text"] = text
        
    @property
    def label_common_icon(self):
        return self.__image
    
    @label_common_icon.setter
    def label_common_icon(self, icon):
        tkicon = load_icon(icon, common=True)
        self.__image = tkicon
        self.__label["image"] = tkicon
        
    @property
    def entry_text(self) -> str:
        return self.__entry.get()
    
    @entry_text.setter
    def entry_text(self, text: str) -> None:
        self.__entry.delete(0, "end")
        self.__entry.insert(0, text)
        
    @property
    def entry_variable(self):
        return self.__entry["textvariable"]
    
    @entry_variable.setter
    def entry_variable(self, val) -> None:
        self.__entry.config(textvariable=val)
        
    @property
    def label_width(self):
        return self.__label["width"]
    
    @label_width.setter
    def label_width(self, width) -> None:
        self.__label["width"] = width

    @property
    def label_compound(self):
        return self.__label["compound"]
    
    @label_compound.setter
    def label_compound(self, val) -> None:
        self.__label["compound"] = val

    @property
    def entry_width(self):
        return self.__entry["width"]
    
    @entry_width.setter
    def entry_width(self, width) -> None:
        self.__entry["width"] = width

    @property
    def checker_function(self):
        return self.__checker_function
    
    @checker_function.setter
    def checker_function(self, func) -> None:
        self.__checker_function = func
        self.__entry.config(validate="key", validatecommand=func)

    def get_int(self) -> int:
        i = self.__entry.get()
        return 0 if not i else int(self.__entry.get())

    def get_float(self) -> float:
        return float(self.__entry.get())
