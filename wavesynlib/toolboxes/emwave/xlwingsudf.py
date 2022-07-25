from pathlib import Path
import numpy as np
import xlwings as xw

from ..basetoolboxnode import BaseXLWingsUDFNode
from . import algorithms 


class XLWingsUDFNode(BaseXLWingsUDFNode):
    def get_module_path(self) -> str:
        return f"{self.parent_node.toolbox_package_path}.{Path(__file__).stem}"


@xw.func
def frequency_to_wavelength(frequency):
    result = algorithms.λfT_eq(f=frequency)
    return np.array(result['λ/m'])[0]
