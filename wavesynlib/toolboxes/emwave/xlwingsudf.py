from pathlib import Path
import numpy as np

import xlwings as xw
import quantities as pq

from ..basetoolboxnode import BaseXLWingsUDFNode
from . import algorithms 


class XLWingsUDFNode(BaseXLWingsUDFNode):
    def get_module_path(self) -> str:
        return f"{self.parent_node.toolbox_package_path}.{Path(__file__).stem}"


@xw.func
@xw.arg("frequency", np.array, ndim=2)
def frequency_to_wavelength(
    frequency,
    frequency_unit="Hz",
    wavelength_unit="m"):
    """\
Calculate the wavelength corresponding to the given frequency.
frequency:       the given frequency;
frequency_unit:  the unit of the frequency (Hz by default);
wavelength_unit: the unit of the wavelength (m by default).
"""
    freq1d = frequency.ravel() * pq.CompoundUnit(frequency_unit)
    result = algorithms.λfT_eq(f=freq1d)
    return np.array(result['λ/m'].convert_unit(wavelength_unit)).reshape(frequency.shape)
