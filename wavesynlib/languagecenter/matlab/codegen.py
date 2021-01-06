import numpy as np



_array_types = (np.ndarray, list, tuple)



def _numpy_arr_to_matlab_arr(arr):
    marr = ",".join((str(i) for i in arr))
    return f"[{marr}]"


def _args_y(y):
    return _numpy_arr_to_matlab_arr(y)


def _args_y_linespec(y, linespec):
    return f"{_args_y(y)}, '{linespec}'"


def _args_x_y(x, y):
    x = _numpy_arr_to_matlab_arr(x)
    y = _numpy_arr_to_matlab_arr(y)
    return f"{x}, {y}"


def _args_x_y_linespec(x, y, linespec):
    return f"{_args_x_y(x, y)}, '{linespec}'"



def commonplot(*args, func="plot"):
    len_args = len(args)
    
    def y():
        return f"{func}({_args_y(args[0])});"

    def yls():
        return f"{func}({_args_y_linespec(*args)});"

    def xy():
        return f"{func}({_args_x_y(*args)});"

    def xyls():
        return f"{func}({_args_x_y_linespec(*args)});"

    def multiple():
        nonlocal args
        arglist = []
        templist = []
        args = [*args, None]
        for arg in args:
            if isinstance(arg, _array_types) or arg is None:
                if len(templist) == 2:
                    arglist.append(_args_x_y(*templist))
                    del templist[:]
                templist.append(arg)
            elif isinstance(arg, str):
                templist.append(arg)
                lentl = len(templist)
                if lentl == 2:
                    arglist.append(_args_y_linespec(*templist))
                elif lentl == 3:
                    arglist.append(_args_x_y_linespec(*templist))
                else:
                    raise ValueError("Matlab Syntax Error.")
                del templist[:]
        return f'{func}({", ".join(arglist)});'

    if len_args == 1:
        return y()
    elif len_args == 2:
        if isinstance(args[1], str):
            return yls()
        elif isinstance(args[1], _array_types):
            return xy()
        else:
            raise TypeError("Type not supported.")
    elif len_args == 3:
        return xyls()
    else:
        return multiple()



def plot(*args):
    return commonplot(*args)



def polarplot(*args):
    return commonplot(*args, func="polarplot")



if __name__ == "__main__":
    print(polarplot([1,2,3]))
    print(polarplot([1,2,3], "r"))
    print(polarplot([1,2,3], [4,5,6]))
    print(polarplot([1,2,3], [4,5,6], "r"))
    print(polarplot([1,2,3], [4,5,6], [7,8,9], [10,11,12]))
    print(polarplot([1,2,3], [4,5,6], "r", [7,8,9], [10,11,12]))
