import tkinter as tk
from tkinter import ttk

import quantities as pq

from .labeledentry import LabeledEntry

# Predefined unit dictionaries for frequency and time quantities
FREQ_UNIT_INFO = {
    "Hz": pq.Hz,
    "kHz": pq.kHz,
    "MHz": pq.MHz,
    "GHz": pq.GHz
}

TIME_UNIT_INFO = {
    "s": pq.s,
    "ms": pq.ms,
    "μs": pq.us,
    "ns": pq.ns,
    "ps": pq.ps
}

LENGTH_UNIT_INFO = {
    "km": pq.km,
    "m": pq.m, 
    "cm": pq.cm,
    "mm": pq.mm,
    "μm": pq.um,
    "nm": pq.nm
}

# A dictionary to associate unit types with their corresponding unit dictionaries
UNIT_TYPE_DICT = {
    "frequency": FREQ_UNIT_INFO,
    "time": TIME_UNIT_INFO,
    "length": LENGTH_UNIT_INFO
}

class PhysicalQuantityEntry(LabeledEntry):
    """
    A widget for entering physical quantities with selectable units.

    This class extends LabeledEntry to include a combobox for selecting units,
    allowing the user to input a value in one unit and convert it to another.

    Attributes:
    - quantity: The current value as a physical quantity with the selected unit.
    - unit_combobox_variable: The StringVar object used by the unit combobox.
    - unit_combobox_width: The width of the unit combobox.

    Methods:
    - fill_unit_combobox(unit_info): Populate the combobox with available units.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a PhysicalQuantityEntry widget.

        Parameters:
        - *args: Positional arguments to pass to the parent class.
        - **kwargs: Keyword arguments including:
            - unit_type (str, optional): Type of units (e.g., 'frequency', 'time').
            - unit_info (dict, optional): Custom dictionary of unit names to quantities.
            - default_unit_name (str): Name of the default unit to display.
        """
        # Retrieve the unit type or custom unit dictionary from keyword arguments
        unit_type = kwargs.pop('unit_type', None)
        if unit_type:
            unit_info = UNIT_TYPE_DICT[unit_type.lower()]
        else:
            unit_info = kwargs.pop("unit_info", None)
        
        # Set the default unit and initialize internal state
        default_unit_name = kwargs.pop("default_unit_name")
        self.__previous_unit_name = default_unit_name
        
        # Initialize the parent class
        super().__init__(*args, **kwargs)

        # Create and configure a combobox for unit selection
        self.__unit_combobox = cmb = ttk.Combobox(self)
        self.__unit_var = unit_var = tk.StringVar()
        unit_var.set(default_unit_name)
        cmb["textvariable"] = unit_var
        cmb["state"] = "readonly"
        cmb.bind("<<ComboboxSelected>>", self.__on_unit_change)  # Bind selection change event
        
        # Populate the combobox with available units
        self.fill_unit_combobox(unit_info)
        cmb.pack(side=tk.LEFT)

    @property
    def quantity(self):
        """Return the current value as a physical quantity with the selected unit."""
        unit_name = self.__unit_combobox.get()
        unit_obj  = self.__unit_info[unit_name]
        value_str = self.entry_text
        value_num = float(value_str)  # Convert text input to a float
        return value_num * unit_obj

    @property
    def unit_combobox_variable(self):
        """Return the StringVar object used by the unit combobox."""
        return self.__unit_var

    @property
    def unit_combobox_width(self):
        """Return the width of the unit combobox."""
        return self.__unit_combobox["width"]

    @unit_combobox_width.setter
    def unit_combobox_width(self, width):
        """Set the width of the unit combobox."""
        self.__unit_combobox["width"] = width

    def fill_unit_combobox(self, unit_info):
        """Populate the unit combobox with the keys from the provided unit dictionary."""
        if unit_info:
            self.__unit_combobox["value"] = list(unit_info.keys())
            self.__unit_info = unit_info

    def __on_unit_change(self, *args):
        """Handle changes in the selected unit and rescale the value accordingly."""
        previous_unit_name = self.__previous_unit_name
        previous_unit_obj = self.__unit_info[previous_unit_name]
        try:
            value_float = float(self.entry_text)  # Parse the current value as a float
            new_unit_name = self.__unit_var.get()
            new_unit_obj = self.__unit_info[new_unit_name]
            
            # Rescale the value to the new unit and update the entry
            new_value = (value_float * previous_unit_obj).rescale(new_unit_obj).magnitude
            self.__previous_unit_name = new_unit_name
            self.entry_text = str(new_value)
        except ValueError:
            # Clear the entry if the value is invalid
            self.entry_text = ""

# Test the widget if the script is run directly
if __name__ == "__main__":
    import quantities as pq

    root = tk.Tk()

    # Create a PhysicalQuantityEntry widget with custom units
    pqent = PhysicalQuantityEntry(root, 
        unit_info={
            "km": pq.kilometer, 
            "m":  pq.meter, 
            "cm": pq.centimeter, 
            "mm": pq.millimeter
        }, 
        default_unit_name="m")

    pqent.label_text = "Wavelength"  # Set the label text
    pqent.pack(expand=tk.YES, fill=tk.X)  # Add the widget to the window

    root.mainloop()  # Start the Tkinter event loop