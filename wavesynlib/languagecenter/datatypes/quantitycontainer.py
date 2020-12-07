from pandas import DataFrame
import quantities as pq



class _PQCol:
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
                result = {
                    "name": raw_col.name,
                    "index": raw_col.index,
                    "quantities": raw_col.to_numpy()*unit_obj}
                break
        else:
            raise KeyError(key)

        return result



class QuantityFrame(DataFrame):
    def __init__(self, *args, **kwargs):
        unit_dict = kwargs.pop("unit_dict", {})
        super().__init__(*args, **kwargs)
        self.pqcol = _PQCol(self)
        self.unit_dict = unit_dict



if __name__ == "__main__":
    qf = QuantityFrame([
        {"velocity/(m/s)": 10},
        {"velocity/(m/s)": 11},
        {"velocity/(m/s)": 12},
        {"velocity/(m/s)": 13},
        {"velocity/(m/s)": 14},
        {"velocity/(m/s)": 15}],
        unit_dict={"(m/s)":pq.CompoundUnit("m/s")})
    print(qf.pqcol["velocity"])