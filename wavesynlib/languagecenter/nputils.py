import operator

import numpy as np

from wavesynlib.languagecenter.datatypes.physicalquantities.functions import expj



class NamedAxesArray:
    def __init__(self, array, axis_names):
        assert(len(array.shape) == len(axis_names))
        self.__arr = array
        self.__axis_names = tuple(axis_names)
        self.__scale = {}


    def __add__(self, other):
        return self.__binop(other, op=operator.add)


    def __iadd__(self, other):
        return self.__inplaceop(other, op=operator.iadd)


    def __sub__(self, other):
        return self.__binop(other, op=operator.sub)


    def __isub__(self, other):
        return self.__inplaceop(other, op=operator.isub)


    def __mul__(self, other):
        return self.__binop(other, op=operator.mul)


    def __imul__(self, other):
        return self.__inplaceop(other, op=operator.imul)


    def add1d(self, other, axis):
        return self.__binop1d(other, op=operator.add, axis=axis)


    def iadd1d(self, other, axis):
        return self.__inplace1dop(other, op=operator.iadd, axis=axis)


    def sub1d(self, other, axis):
        return self.__binop1d(other, op=operator.sub, axis=axis)


    def isub1d(self, other, axis):
        return self.__inplace1dop(other, op=operator.isub, axis=axis)


    def mul1d(self, other, axis):
        return self.__binop1d(other, op=operator.mul, axis=axis)


    def imul1d(self, other, axis):
        return self.__inplace1dop(other, op=operator.imul, axis=axis)


    def conj(self):
        return self.__unaryop(op=np.conj)


    def expj(self):
        return self.__unaryop(op=expj)


    def fft(self, **kwargs):
        axis = kwargs.pop("axis", -1)
        if axis != -1:
            assert(isinstance(axis, str))
            axis = self.name_to_axis_indices(axis)
        kwargs["axis"] = axis
        result_arr = np.fft.fft(self.__arr, **kwargs)
        result = type(self)(result_arr, axis_names=self.__axis_names)
        return result


    def sum(self, axis):
        if isinstance(axis, str):
            axis = (axis,)
        assert(isinstance(axis, tuple))
        axes = self.name_to_axis_indices(*axis)
        if not isinstance(axes, tuple):
            axes = (axes,)
        result_arr = self.array.sum(axis=axes)
        axis_names = list(self.__axis_names)
        for name in axis:
            axis_names.remove(name)
        result = type(self)(result_arr, axis_names=axis_names)
        return result


    def apply_along_axis(self, func1d, axis):
        assert(isinstance(axis, str))
        assert(axis in self.axis_names)
        ai = self.name_to_axis_indices(axis)
        result_arr = np.apply_along_axis(func1d, ai, self.array)
        len_old_shape = len(self.array.shape)
        len_new_shape = len(result_arr.shape)
        if len_old_shape == len_new_shape:
            result = type(self)(result_arr, axis_names=self.axis_names)
        elif len_old_shape < len_new_shape:
            name_list = list(self.axis_names)
            for k in range(len_new_shape-len_old_shape):
                name_list.insert(ai, f"unnamed_axis{k}")
            result = type(self)(result_arr, axis_names=name_list)
        else:
            name_list = list(self.axis_names)
            name_list.remove(axis)
            result = type(self)(result_arr, axis_names=name_list)
        return result


    def cdot1d(self, other, axis):
        """\
Consider self as a collection of vectors along the given axis,
calculating the dot product (with complex conjugate) of 
self vectors and 'other' (which is a vector).

For example: 
A = NamedAxesArray(np.array([1,2,3], [4,5,6]), axis_names=('slow_time', 'fast_time'))
A.cdot1d(np.array([10, 100]), axis='slow_time') 
is equivalent to 
A@np.array([[10], [100]])"""
        assert(len(other.shape)==1)
        temp = self.mul1d(other.conj(), axis=axis)
        return temp.sum(axis=axis)


    def indexing(self, **kwargs):
        axes = sorted((self.name_to_axis_indices(item[0]), item[1]) for item in kwargs.items())
        indexing = tuple(i[1] for i in axes)
        new_names = [] 
        for idx, name in enumerate(self.__axis_names):
            if not isinstance(indexing[idx], int):
                new_names.append(name)
        new_array = self.__arr[indexing]
        return type(self)(new_array, new_names)


    def permute(self, *args):
        new_order = self.name_to_axis_indices(*args)
        new_array = self.__arr.transpose(new_order)
        return type(self)(new_array, args)


    @classmethod
    def concat(cls, *args, **kwargs):
        for arr in args:
            assert(isinstance(arr, cls))
            assert(arr.axis_names == args[0].axis_names)
        axis_name = kwargs["axis"]
        axis = args[0].name_to_axis_indices(axis_name)
        return cls(np.concatenate(tuple(arg.array for arg in args), axis=axis), args[0].axis_names)


    def expand_dims_as(self, target):
        assert(set(self.__axis_names).issubset(target.axis_names))
        new_shape = [1] * (len(target.axis_names) - len(self.axis_names))
        new_shape.extend(self.array.shape)
        new_array = np.reshape(self.array, new_shape)
        new_axis_names = (*(set(target.axis_names)-set(self.__axis_names)), *self.__axis_names)
        result = type(self)(new_array, new_axis_names)
        result = result.permute(*target.axis_names)
        return result


    def set_scale(self, scale, axis):
        assert(len(scale) == self.shape[axis])
        self.__scale[axis] = scale


    def get_scale(self, axis):
        return self.__scale[axis]


    def del_scale(self, axis):
        del self.__scale[axis]


    def rename_axes(self, **kwargs):
        name_list = list(self.__axis_names)
        for old_name, new_name in kwargs.items():
            name_list[name_list.index(old_name)] = new_name
        self.__axis_names = tuple(name_list)


    def name_to_axis_indices(self, *args):
        result = tuple(self.__axis_names.index(name) for name in args)
        return result[0] if len(result)==1 else result


    @property
    def axis_names(self):
        return self.__axis_names


    @property
    def array(self):
        return self.__arr


    @property
    def shape(self):
        arr_shape = self.__arr.shape
        result = {}
        for index, name in enumerate(self.__axis_names):
            result[name] = arr_shape[index]
        return result


    def __binop(self, other, op):
        assert(isinstance(other, type(self)))
        my_dim = len(self.__axis_names)
        other_dim = len(other.axis_names)
        if my_dim >= other_dim:
            A, B = self, other
        else:
            A, B = other, self
        B = B.expand_dims_as(A)
        Carr = op(A.array, B.array)
        C = type(self)(Carr, A.axis_names)
        return C


    def __binop1d(self, other, op, axis):
        assert(len(other.shape)==1)
        other = type(self)(other, axis_names=(axis,))
        other = other.expand_dims_as(self)
        return op(self, other)


    def __unaryop(self, op):
        result_arr = op(self.__arr)
        result = type(self)(result_arr, axis_names=self.__axis_names)
        return result


    def __inplaceop(self, other, op):
        other = other.expand_dims_as(self)
        op(self.__arr, other.array)
        return self


    def __inplace1dop(self, other, op, axis):
        assert(len(other.shape)==1)
        other = type(self)(other, axis_names=(axis,))
        other = other.expand_dims_as(self)
        op(self.__arr, other.array)
        return self



if __name__ == "__main__":
    # Test 
    echo = np.array([[1, 2, 3], [4, 5, 6]])
    echo = NamedAxesArray(echo, ("slow_time", "fast_time"))

    echo2 = echo.permute("fast_time", "slow_time")

    echo3 = NamedAxesArray.concat(echo2, echo2, axis="slow_time")
    echo4 = NamedAxesArray.concat(echo2, echo2, axis="fast_time")

    echo5 = echo3.indexing(slow_time=1, fast_time=np.s_[:])
    echo6 = echo3.indexing(slow_time=[1], fast_time=np.s_[:3])

    print(echo3)

    window = NamedAxesArray(np.array([100, 200, 300]), axis_names=("fast_time",))
    # window = window.expand_dims_as(echo3)
    windowed_echo = window - echo3
    print(window)

    echo3 += window
    echo3.imul1d(window.array, axis="fast_time")
    echo3.mul1d(window.array, axis="fast_time")
    print(echo3)