import hy
from .labeledentry import LabeledEntry

import tkinter as tk
from tkinter import ttk



class PhysicalQuantityEntry(LabeledEntry):
    def __init__(self, *args, **kwargs):
        unit_info = kwargs.pop("unit_info", None)
        default_unit_name = kwargs.pop("default_unit_name", "")
        self.__previous_unit_name = default_unit_name
        super().__init__(*args, **kwargs)
        self.__unit_combobox = cmb = ttk.Combobox(self)
        self.__unit_var = unit_var = tk.StringVar()
        unit_var.set(default_unit_name)
        cmb["textvariable"] = unit_var
        cmb["stat"] = "readonly"
        cmb.bind("<<ComboboxSelected>>", self.__on_unit_change)
        self.fill_unit_combobox(unit_info)
        cmb.pack(side=tk.LEFT)


    @property
    def unit_combobox_width(self):
        return self.__unit_combobox["width"]


    @unit_combobox_width.setter
    def unit_combobox_width(self, width):
        self.__unit_combobox["width"] = width


    def fill_unit_combobox(self, unit_info):
        if unit_info:
            self.__unit_combobox["value"] = list(unit_info.keys())
            self.__unit_info = unit_info


    def __on_unit_change(self, *args):
        previous_unit_name = self.__previous_unit_name
        previous_unit_obj = self.__unit_info[previous_unit_name]
        try:
            value_float = float(self.entry_text)
            new_unit_name = self.__unit_var.get()
            new_unit_obj = self.__unit_info[new_unit_name]
            new_value = (value_float*previous_unit_obj).rescale(new_unit_obj).magnitude
            self.__previous_unit_name = new_unit_name
            self.entry_text = str(new_value)
        except ValueError:
            self.entry_text = ""




if __name__ == "__main__":
    import quantities as pq
    root = tk.Tk()
    pqent = PhysicalQuantityEntry(root, 
        unit_info={
            "km": pq.kilometer, 
            "m":  pq.meter, 
            "cm": pq.centimeter, 
            "mm": pq.millimeter}, 
        default_unit_name="m")
    pqent.label_text = "Wavelength"
    pqent.pack(expand=tk.YES, fill=tk.X)
    root.mainloop()
