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


@xw.func
@xw.arg("arr_in", np.array, ndim=2)
def elementwise_eval(func_str, arr_in):
    arr_out = np.empty(shape=arr_in.shape, dtype=object)
    for idx, elem in enumerate(arr_in.flat):
        _ = elem
        arr_out.flat[idx] = eval(func_str)
    return arr_out


@xw.func
@xw.arg("args", np.array, ndim=2)
def hstack(*args):
    """\
Stack arrays in sequence horizontally (column wise)."""
    return np.hstack(args)


@xw.func
@xw.arg("args", np.array, ndim=2)
def vstack(*args):
    """\
Stack arrays in sequence vertically (row wise)."""
    return np.vstack(args)
