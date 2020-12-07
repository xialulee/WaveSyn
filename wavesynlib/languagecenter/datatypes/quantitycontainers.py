from pandas import DataFrame
import quantities as pq



class _QCol:
    def __init__(self, frame):
        self.__frame = frame


    def __getitem__(self, key):
        frame = self.__frame
        key_ = key + "/"

        for name in frame.columns:
            if name.startswith(key_):
                unit_name = name.split("/", 1)[1]
                unit_obj = frame.unit_dict.get(unit_name, None)
                if unit_obj is None:
                    unit_obj = getattr(pq, unit_name)
                raw_col = frame[name]
                result = raw_col.to_numpy()*unit_obj
                result.index = raw_col.index
                result.name = raw_col.name
                break
        else:
            raise KeyError(key)

        return result




class QuantityFrame:
    def __init__(self, *args, **kwargs):
        self.__unit_dict = kwargs.pop("unit_dict", {})
        self.__dataframe = DataFrame(*args, **kwargs)
        self.qcol = _QCol(self)


    @property
    def dataframe(self):
        return self.__dataframe


    @property
    def unit_dict(self):
        return self.__unit_dict


    def __getattr__(self, attr):
        return getattr(self.__dataframe, attr)


    def __getitem__(self, key):
        return self.__dataframe[key]



if __name__ == "__main__":
    qf = QuantityFrame([
        {"velocity/(m/s)": 10},
        {"velocity/(m/s)": 11},
        {"velocity/(m/s)": 12},
        {"velocity/(m/s)": 13},
        {"velocity/(m/s)": 14},
        {"velocity/(m/s)": 15}],
        unit_dict={"(m/s)":pq.CompoundUnit("m/s")})
    print(qf.qcol["velocity"])
