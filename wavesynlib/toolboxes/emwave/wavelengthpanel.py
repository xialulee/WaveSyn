import tkinter as tk
from tkinter import ttk
from math import nan

import quantities as pq

from .algorithms import λfT_eq

from wavesynlib.widgets.tk.physicalquantityentry import PhysicalQuantityEntry



arg_names = ("f", "λ", "T")
arg_ascii_name_map = {"f":"f", "λ": "lambda_", "T": "T"}


THz = pq.UnitQuantity("terahertz", 1000.0*pq.GHz, "THz")

f_units = {
    "THz": THz,
    "GHz": pq.GHz,
    "MHz": pq.MHz,
    "kHz": pq.kHz,
    "Hz":  pq.Hz }

dm = pq.UnitQuantity("decimeter", 100*pq.millimeter, "dm")

λ_units = {
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
    "f": f_units, 
    "λ": λ_units, 
    "T": T_units}


default_units = {
    "f": "MHz",
    "λ": "m",
    "T": "ms"}




class WavelengthPanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("real test")
        items = {}
        value_vars = {}
        unit_vars = {}

        for name in ("f", "λ", "T"):
            item = PhysicalQuantityEntry(self, default_unit_name=default_units[name])
            item.pack(fill=tk.X, expand=tk.YES, padx=3, pady=5)

            item.label_text = name
            item.label_width = 3

            item.entry_width = 20
            textvar = tk.DoubleVar()
            textvar.set(nan)
            item.entry_variable = textvar
            item.entry.bind("<KeyRelease>", lambda *args, name=name: self._on_parameter_input(name))
            value_vars[name] = textvar

            item.fill_unit_combobox(unit_map[name])
            item.unit_combobox_width = 5
            unitvar = item.unit_combobox_variable
            unit_vars[name] = unitvar
            items[name] = item

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

        calc_result = λfT_eq(**kwargs)

        for n in arg_names:
            if n != arg_name:
                unit_obj = self._get_unit_obj(n)
                arg_value = calc_result.qcol(n).rescale(unit_obj).magnitude[0]
                self.value_vars[n].set(arg_value)

