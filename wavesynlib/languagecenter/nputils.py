import numpy as np



class NamedAxisArray:
    def __init__(self, array, axis_names):
        assert(len(array.shape) == len(axis_names))
        self.__arr = array
        self.__axis_names = tuple(axis_names)


    def indexing(self, **kwargs):
        axes = sorted((self.__axis_names.index(item[0]), item[1]) for item in kwargs.items())
        indexing = tuple(i[1] for i in axes)
        new_names = [] 
        for idx, name in enumerate(self.__axis_names):
            if not isinstance(indexing[idx], int):
                new_names.append(name)
        new_array = self.__arr[indexing]
        return type(self)(new_array, new_names)


    def permute(self, *args):
        new_order = tuple(self.__axis_names.index(name) for name in args)
        new_array = self.__arr.transpose(new_order)
        return type(self)(new_array, args)


    @classmethod
    def concat(cls, *args, **kwargs):
        for arr in args:
            assert(isinstance(arr, cls))
            assert(arr.axis_names == args[0].axis_names)
        axis_name = kwargs["axis"]
        axis = args[0].axis_names.index(axis_name)
        return cls(np.concatenate(tuple(arg.array for arg in args), axis=axis), args[0].axis_names)


    @property
    def axis_names(self):
        return self.__axis_names


    @property
    def array(self):
        return self.__arr




if __name__ == "__main__":
    # Test 
    echo = np.array([[1, 2, 3], [4, 5, 6]])
    echo = NamedAxisArray(echo, ("slow_time", "fast_time"))

    echo2 = echo.permute("fast_time", "slow_time")

    echo3 = NamedAxisArray.concat(echo2, echo2, axis="slow_time")
    echo4 = NamedAxisArray.concat(echo2, echo2, axis="fast_time")

    echo5 = echo3.indexing(slow_time=1, fast_time=np.s_[:])
    echo6 = echo3.indexing(slow_time=[1], fast_time=np.s_[:3])

    print(echo3)
