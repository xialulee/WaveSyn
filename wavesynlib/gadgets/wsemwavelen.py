import sys

import tkinter as tk
from tkinter import ttk

import quantities as pq




arg_names = ("f", "λ", "T")
arg_ascii_name_map = {"f":"f", "λ": "lambda_", "T": "T"}


THz = pq.UnitQuantity("terahertz", 1000.0*pq.GHz, "THz")

freq_units = {
    "THz": THz,
    "GHz": pq.GHz,
    "MHz": pq.MHz,
    "kHz": pq.kHz,
    "Hz":  pq.Hz }

dm = pq.UnitQuantity("decimeter", 100*pq.millimeter, "dm")

lambda_units = {
    "km": pq.kilometer,
    "m":  pq.meter,
    "dm": dm,
    "cm": pq.centimeter,
    "mm": pq.millimeter }


T_units = {
    "s":  pq.second,
    "ms": pq.millisecond }


unit_map = {
    "f": freq_units, 
    "λ": lambda_units, 
    "T": T_units}



# Light speed. 
_c = 3e8 * (pq.meter/pq.second) 



def calc(lambda_=None, T=None, f=None):
    if lambda_ is not None and lambda_>0:
        T = lambda_ / _c
        f = 1 / T
    elif T is not None and T>0:
        lambda_ = _c * T
        f = 1 / T
    elif f is not None and f>0:
        T = 1 / f
        lambda_ = _c * T
    else:
        raise ValueError("Given parameters are not valid.")
    return {"f":f, "λ": lambda_, "T":T}



class QuantityItem(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_lbl = ttk.Label(self)
        self.name_lbl.pack(side=tk.LEFT)
        self.value_ent = ttk.Entry(self)
        self.value_ent.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.unit_cmb = ttk.Combobox(self)
        self.unit_cmb.pack(side=tk.LEFT)




class EMWavelenPanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        items = {}
        value_vars = {}
        unit_vars = {}

        for name in ("f", "λ", "T"):
            item = QuantityItem(self)
            item.pack(fill=tk.X, expand=tk.YES, padx=3, pady=5)

            item.name_lbl["text"] = name
            item.name_lbl["width"] = 3

            item.value_ent["width"] = 20
            textvar = tk.StringVar()
            textvar.set("")
            item.value_ent["textvariable"] = textvar
            item.value_ent.bind("<KeyRelease>", lambda *args, name=name: self.on_parameter_input(name))
            value_vars[name] = textvar

            item.unit_cmb["value"] = list(unit_map[name].keys())
            item.unit_cmb["width"] = 5
            unitvar = tk.StringVar()
            unitvar.set("")
            item.unit_cmb["textvariable"] = unitvar
            unit_vars[name] = unitvar
            item.unit_cmb["stat"] = "readonly"
            item.unit_cmb.bind("<<ComboboxSelected>>", lambda *args, name=name: self.on_unit_change(name))
            items[name] = item


        unit_vars["f"].set("MHz")
        unit_vars["λ"].set("m")
        unit_vars["T"].set("ms")

        self.previous_unit_names = {
            "f": unit_vars["f"].get(),
            "λ": unit_vars["λ"].get(),
            "T": unit_vars["T"].get() }

        self.value_vars = value_vars
        self.unit_vars = unit_vars


    def get_float(self, arg_name):
        value_str = self.value_vars[arg_name].get()
        value_float = float(value_str)
        if value_float <= 0:
            raise ValueError()
        return value_float


    def get_unit_obj(self, arg_name):
        unit_name = self.unit_vars[arg_name].get()
        unit_obj = unit_map[arg_name][unit_name]
        return unit_obj


    def on_parameter_input(self, arg_name):
        try:
            value_float = self.get_float(arg_name)
            unit_obj = self.get_unit_obj(arg_name)
            value_quantity = value_float * unit_obj
        except ValueError:
            for n in arg_names:
                if n != arg_name:
                    self.value_vars[arg_name].set("")
            return

        kwargs = {arg_ascii_name_map[arg_name]:value_quantity}

        calc_result = calc(**kwargs)

        for n in arg_names:
            if n != arg_name:
                unit_obj = self.get_unit_obj(n)
                arg_value = calc_result[n].rescale(unit_obj).magnitude
                self.value_vars[n].set(str(arg_value))


    def on_unit_change(self, arg_name):
        previous_unit_name = self.previous_unit_names[arg_name]
        self.previous_unit_names[arg_name] = self.unit_vars[arg_name].get()
        try:
            value_float = self.get_float(arg_name)
            unit_obj = self.get_unit_obj(arg_name)
            previous_unit_obj = unit_map[arg_name][previous_unit_name]
            value = (value_float*previous_unit_obj).rescale(unit_obj).magnitude
            self.value_vars[arg_name].set(str(value))
        except ValueError:
            for n in arg_names:
                if n != arg_name:
                    self.value_vars[arg_name].set("")
            return
    


def main(argv):
    root = tk.Tk()
    root.title("λ")
    panel = EMWavelenPanel(root)
    panel.pack(fill=tk.X, expand=tk.YES)
    root.mainloop()



if __name__ == "__main__":
    main(sys.argv)