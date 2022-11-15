from functools import partial


def check_value(d, i, P, s, S, v, V, W, func):
    try:
        func(P)
        return True
    except ValueError:
        return False


class ValueChecker:
    def __init__(self, root):
        self.__root = root

        def check_int(v):
            if v == "" or v == "-":
                return
            return int(v)
        self.check_int = ( # A tuple
            root.register(
                partial(
                    check_value, 
                    func = check_int
                )
            ), 
            "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"
        )

        def check_float(v):
            if v in ("", "-", "-."):
                return
            return float(v)
        self.check_float = (
            root.register(
                partial(
                    check_value, 
                    func = check_float
                )
            ), 
            "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"
        )

        def check_positive_float(v):
            if v in ("", "+", ".", "+."):
                return
            if float(v) <= 0:
                raise ValueError
        self.check_positive_float = ( 
            root.register(
                partial(
                    check_value, 
                    func = check_positive_float
                )
            ), 
            "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"
        )

        def check_nonnegative_float(v):
            if v in ("", "+", ".", ".+"):
                return
            if float(v) < 0:
                raise ValueError
        self.check_nonnegative_float = (
            root.register(
                partial(
                    check_value,
                    func=check_nonnegative_float
                ) 
            ), 
            "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"
        )
