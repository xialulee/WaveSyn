import hy

import tkinter as tk

import quantities as pq

from wavesynlib.widgets.tk.physicalquantityentry import PhysicalQuantityEntry
from wavesynlib.widgets.tk.labeledentry import LabeledEntry



_length_units = {
    "km": pq.kilometer,
    "m":  pq.meter,
    "cm": pq.centimeter,
    "mm": pq.millimeter }


_angle_units = {
    "rad": pq.rad,
    "deg": pq.deg }




class BeamwidthCalcPanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        label_width = 5
        unit_combobox_width = 4

        lambda_ent = PhysicalQuantityEntry(self, 
            unit_info=_length_units,
            default_unit_name="m")
        lambda_ent.label_text = "λ"
        lambda_ent.label_width = label_width
        lambda_ent.unit_combobox_width = unit_combobox_width
        lambda_ent.pack(expand=tk.YES, fill=tk.X)

        d_ent = PhysicalQuantityEntry(self,
            unit_info=_length_units,
            default_unit_name="m")
        d_ent.label_text = "d"
        d_ent.label_width = label_width
        d_ent.unit_combobox_width = unit_combobox_width
        d_ent.pack(expand=tk.YES, fill=tk.X)

        N_ent = LabeledEntry(self)
        N_ent.label_text = "N"
        N_ent.label_width = label_width
        N_ent.pack(expand=tk.YES, fill=tk.X)

        theta_ent = PhysicalQuantityEntry(self,
            unit_info=_angle_units,
            default_unit_name="deg")
        theta_ent.label_text = "θ"
        theta_ent.label_width = label_width
        theta_ent.unit_combobox_width = unit_combobox_width
        theta_ent.pack(expand=tk.YES, fill=tk.X)

        k_ent = LabeledEntry(self)
        k_ent.label_text = "k"
        k_ent.label_width = label_width
        k_ent.pack(expand=tk.YES, fill=tk.X)




if __name__ == "__main__":
    root = tk.Tk()
    panel = BeamwidthCalcPanel(root)
    panel.pack()
    root.mainloop()