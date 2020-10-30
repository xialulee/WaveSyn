import tkinter as tk
from tkinter import ttk
from math import nan

import quantities as pq

from .algorithms import frequency_wavelength_period



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
    "ms": pq.millisecond, 
    "us": pq.microsecond,
    "ns": pq.nanosecond}


unit_map = {
    "f": freq_units, 
    "λ": lambda_units, 
    "T": T_units}



class QuantityItem(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name_lbl = ttk.Label(self)
        self.name_lbl.pack(side=tk.LEFT)
        self.value_ent = ttk.Entry(self)
        self.value_ent.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        self.unit_cmb = ttk.Combobox(self)
        self.unit_cmb.pack(side=tk.LEFT)



class WavelengthPanel(tk.Frame):
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
            textvar = tk.DoubleVar()
            textvar.set(nan)
            item.value_ent["textvariable"] = textvar
            item.value_ent.bind("<KeyRelease>", lambda *args, name=name: self._on_parameter_input(name))
            value_vars[name] = textvar

            item.unit_cmb["value"] = list(unit_map[name].keys())
            item.unit_cmb["width"] = 5
            unitvar = tk.StringVar()
            unitvar.set("")
            item.unit_cmb["textvariable"] = unitvar
            unit_vars[name] = unitvar
            item.unit_cmb["stat"] = "readonly"
            item.unit_cmb.bind("<<ComboboxSelected>>", lambda *args, name=name: self._on_unit_change(name))
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


    @property
    def arg_values(self):
        result = {
            name: self._get_float(name)*self._get_unit_obj(name) 
                for name in arg_names}
        return result


    def _get_float(self, arg_name):
        try:
            value = self.value_vars[arg_name].get()
        except tk.TclError:
            raise ValueError()
        if value <= 0.0:
            raise ValueError()
        return value


    def _get_unit_obj(self, arg_name):
        unit_name = self.unit_vars[arg_name].get()
        unit_obj = unit_map[arg_name][unit_name]
        return unit_obj


    def _on_parameter_input(self, arg_name):
        try:
            value_float = self._get_float(arg_name)
            unit_obj = self._get_unit_obj(arg_name)
            value_quantity = value_float * unit_obj
        except ValueError:
            for n in arg_names:
                if n != arg_name:
                    self.value_vars[n].set(nan)
            return

        kwargs = {arg_ascii_name_map[arg_name]:value_quantity}

        calc_result = frequency_wavelength_period(**kwargs)

        for n in arg_names:
            if n != arg_name:
                unit_obj = self._get_unit_obj(n)
                arg_value = calc_result[n].rescale(unit_obj).magnitude
                self.value_vars[n].set(arg_value)


    def _on_unit_change(self, arg_name):
        previous_unit_name = self.previous_unit_names[arg_name]
        self.previous_unit_names[arg_name] = self.unit_vars[arg_name].get()
        try:
            value_float = self._get_float(arg_name)
            unit_obj = self._get_unit_obj(arg_name)
            previous_unit_obj = unit_map[arg_name][previous_unit_name]
            value = (value_float*previous_unit_obj).rescale(unit_obj).magnitude
            self.value_vars[arg_name].set(value)
        except ValueError:
            for n in arg_names:
                if n != arg_name:
                    self.value_vars[n].set(nan)
            return
    

