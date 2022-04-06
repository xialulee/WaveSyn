from array import array


class MDArrayAccessor:
    def __init__(self):
        self.__accessors = []

    def define(self, accessor_name, array_name, size):
        dim = len(size)
        code_list = []
        axis_size_template = f"__wspp_cpp_mdarray_accessor_{array_name}_axis_size_m"
        if dim > 2:
            code_list.append(f"int {axis_size_template}3 = ({size[-1]})*({size[-2]});")
        for cnt in range(4, dim+1):
            code_list.append(f"int {axis_size_template}{cnt} = ({size[-cnt+1]})*({axis_size_template}{cnt-1});")
        self.__accessors.append(accessor_name)
        var_list = [f"var{i}" for i in range(dim)]
        expr_list = []
        for cnt in range(2, dim):
            expr_list.append(f"({var_list[cnt-2]})*({axis_size_template}{dim-cnt+2})")
        expr_list.append(f"({var_list[-2]})*({size[-1]})")
        expr_list.append(f"({var_list[-1]})")
        expr = "+".join(expr_list)
        code_list.append(f"#define {accessor_name}({','.join(var_list)}) {array_name}[{expr}]")
        return "\n".join(code_list)

    def undef_all(self):
        undef_list = []
        for accessor in self.__accessors:
            undef_list.append(f"#undef {accessor}")
        return "\n".join(undef_list)