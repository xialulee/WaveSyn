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
                result.append(f"[{self.__aux_size[idx]}*({expr})]")
            if len(key) == len(self.__aux_size):
                result[-1] = f"[{key[-1]}]"
            return f"{self.__name}{''.join(result)}"
        return f"{self.__name}[key]"
