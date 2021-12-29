import sys
import hy

from jinja2.filters import FILTERS, environmentfilter


def hyeval(expr:str):
    expr = hy.read_str(expr)
    return hy.eval(expr)


@environmentfilter
def efhyeval(environment, value, attribute=None):
    expr = hy.read_str(value)
    return hy.eval(expr, locals=sys._getframe(1).f_locals)

FILTERS["efhyeval"] = efhyeval



class MDArray:
    def __init__(self, name, size):
        self.__name = name
        self.__size = size
        self.__aux_size = aux_size = ['1', size[-1]]
        for i in range(len(size)-2, 0, -1):
            aux_size.append(f"{aux_size[-1]}*({size[i]})")
        aux_size.reverse()

    def __getitem__(self, key):
        if isinstance(key, tuple):
            result = []
            for idx, expr in enumerate(key):
                result.append(f"({self.__aux_size[idx]}*({expr}))")
            if len(key) == len(self.__aux_size):
                result[-1] = f"({key[-1]})"
            return f"{self.__name}[{' + '.join(result)}]"
        return f"{self.__name}[{key}]"


class ComplexScalar:
    def __init__(self, 
            var_type:str=None, 
            var_name:str=None, 
            init_value:str=None, 
            real_name:str="x", 
            imag_name:str="y",
            real:str="",
            imag:str=""):
        self.__var_type = var_type
        self.__var_name = var_name
        self.__init_value = init_value
        self.__real_name = real_name
        self.__imag_name = imag_name
        self.__real = real
        self.__imag = imag

    @classmethod
    def to_list(cls, *args):
        fields = []
        for obj in args:
            assert isinstance(obj, ComplexScalar)
            if obj.var_name is not None:
                for field_name in ("real_name", "imag_name"):
                    fields.append(f"{obj.var_name}.{getattr(obj, field_name)}")
            else:
                for field in ("real", "imag"):
                    fields.append(getattr(obj, field))
        return fields

    @property
    def var_type(self):
        return self.__var_type

    @property
    def var_name(self):
        return self.__var_name

    @property
    def real_name(self):
        return self.__real_name

    @property
    def imag_name(self):
        return self.__imag_name

    @property
    def real(self):
        return self.__real

    @property
    def imag(self):
        return self.__imag

    def declare(self):
        result = f"{self.__var_type} {self.__var_name}"
        if self.__init_value:
            result = f"{result} = {self.__init_value}"
        return f"{result}"

    def __return_aux(self, real, imag):
        return ComplexScalar(
            var_type=self.var_type,
            real_name=self.real_name,
            imag_name=self.imag_name,
            real=real,
            imag=imag)

    def __add__(self, other):
        r1, i1, r2, i2 = self.to_list(self, other)
        return self.__return_aux(
            real=f"({r1} + {r2})", 
            imag=f"({i1} + {i2})")

    def iadd(self, other):
        assert self.var_name
        r1, i1 = self.to_list(other)
        return f"{self.var_name}.{self.real_name} += {r1}; {self.var_name}.{self.imag_name} += {i1};"

    def __sub__(self, other):
        r1, i1, r2, i2 = self.to_list(self, other)
        return self.__return_aux(
            real=f"({r1} - {r2})", 
            imag=f"({i1} - {i2})")

    def __mul__(self, other):
        r1, i1, r2, i2 = self.to_list(self, other)
        return self.__return_aux(
            real=f"({r1}*{r2} - {i1}*{i2})",
            imag=f"({r1}*{i2} + {r2}*{i1})")

    def __div__(self, other):
        r1, i1, r2, i2 = self.to_list(self, other)
        return self.__return_aux(
            real=f"(({r1}*{r2}+{i1}*{i2})/({r2}*{r2}+{i2}*{i2}))",
            imag=f"(({r2}*{i1}-{r1}*{i2})/({r2}*{r2}+{i2}*{i2}))")

    def conj(self):
        r1, i1 = self.to_list(self)
        return self.__return_aux(
            real=f"{r1}", 
            imag=f"-{i1}")
