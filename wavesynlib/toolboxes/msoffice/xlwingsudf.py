from pathlib import Path

import numpy as np
import xlwings as xw

from ..basetoolboxnode import BaseXLWingsUDFNode


class XLWingsUDFNode(BaseXLWingsUDFNode):
    def get_module_path(self) -> str:
        return f"{self.parent_node.toolbox_package_path}.{Path(__file__).stem}"


@np.vectorize
def _vec_str_slice(string, slice_obj):
    return str(string)[slice_obj]


@xw.func
@xw.arg("str_in", np.array, ndim=2)
def str_slice(
    str_in, 
    slice_start=None, 
    slice_stop=None, 
    slice_step=None):
    """\
Slice the given string.
string: the given string (could be a scalar or an array);
start, stop and step_: the arguments of the slice object (scalar).
"""
    args = (None if arg is None else int(arg) for arg in (slice_start, slice_stop, slice_step))
    slice_obj = slice(*args)
    return _vec_str_slice(str_in, slice_obj)
