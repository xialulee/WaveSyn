import numpy as np
from pandas import Series, DataFrame, read_csv
import quantities as pq



def _field_name_to_unit_obj(name, unit_dict=None):
        parts = name.split("/", 1)
        if len(parts) < 2:
            unit_obj = pq.dimensionless
        else:
            unit_name = parts[1]
            if unit_dict and unit_name in unit_dict:
                unit_obj = unit_dict[unit_name]
            elif hasattr(pq, unit_name):
                unit_obj = getattr(pq, unit_name)
            else:
                unit_obj = pq.CompoundUnit(unit_name)
        return unit_obj



def _get_field_fullname(name_coll, name):
    if name in name_coll:
        return name
    name_ = f"{name}/"
    for n in name_coll:
        if n.startswith(name_):
            return n
    else:
        raise KeyError("Cannot find the corresponding fullname.")



class QuantitySeries(Series):

    _metadata = ["unit_dict"]

    def __init__(self, *args, **kwargs):
        unit_dict = kwargs.pop("unit_dict", None)
        super().__init__(*args, **kwargs)
        self.unit_dict = unit_dict


    @property
    def _constructor(self):
        def constructor(*args, **kwargs):
            if "unit_dict" not in kwargs:
                kwargs["unit_dict"] = self.unit_dict
            return QuantitySeries(*args, **kwargs)
        return constructor


    @property
    def _constructor_expanddim(self):
        def constructor(*args, **kwargs):
            if "unit_dict" not in kwargs:
                kwargs["unit_dict"] = self.unit_dict
            return QuantityFrame(*args, **kwargs)
        return constructor


    def qelem(self, name:str)->pq.Quantity:
        if "/" not in name:
            if name in self.index:
                # Dimensionless field
                return self[name] * pq.dimensionless
            else:
                # Name without unit
                name_ = f"{name}/"
                for index_name in self.index:
                    if index_name.startswith(name_):
                        name = index_name
                        break
                else:
                    raise KeyError(f"{name} not in this Series.")
                unit_obj = _field_name_to_unit_obj(name, self.unit_dict)
                return self[name] * unit_obj
        else:
            unit_obj = _field_name_to_unit_obj(name, self.unit_dict)
            return self[name] * unit_obj


    def get_elem_fullname(self, name):
        return _get_field_fullname(self.index, name)


    @property
    def unit_object(self):
        return _field_name_to_unit_obj(self.name, self.unit_dict)


    @property
    def quantities(self):
        return self.to_numpy() * self.unit_object


    def convert_unit(self, new_unit:str):
        quantity_name = self.name.split("/", 1)[0]
        if set("*/").intersection(set(new_unit)):
            new_postfix = f"({new_unit})"
        else:
            new_postfix = new_unit
        new_name = f"{quantity_name}/{new_postfix}"
        unit_obj = self.__search_unit(new_unit)
        return Series(
            self.quantities.rescale(unit_obj),
            index=self.index,
            name=new_name)



class QuantityFrame(DataFrame):

    _metadata = ["unit_dict"]

    def __init__(self, *args, **kwargs):
        unit_dict = kwargs.pop("unit_dict", None)
        super().__init__(*args, **kwargs)
        self.unit_dict = unit_dict


    @property
    def _constructor(self):
        def constructor(*args, **kwargs):
            if "unit_dict" not in kwargs:
                kwargs["unit_dict"] = self.unit_dict
            return QuantityFrame(*args, **kwargs)
        return constructor


    @property
    def _constructor_sliced(self):
        def constructor(*args, **kwargs):
            if "unit_dict" not in kwargs:
                kwargs["unit_dict"] = self.unit_dict
            return QuantitySeries(*args, **kwargs)
        return constructor


    @classmethod
    def read_csv(cls, filename):
        temp = read_csv(filename)
        return cls(temp)


    def get_column_fullname(self, name):
        return _get_field_fullname(self.columns, name)


    def qcol(self, name:str)->pq.Quantity:
        if name in self.columns:
            result = self[name].quantities
        else:
            name_ = f"{name}/"
            for column in self.columns:
                if column.startswith(name_):
                    result = self[column].quantities
                    break
            else:
                raise KeyError(f"{name} not exists in this frame.")
        return result


    @property 
    def qmatrix(self) -> pq.Quantity:
        result = []
        unit_obj = None
        for index, column in enumerate(self.columns):
            name = column.split("/", 1)[0]
            qcol = self.qcol(name)
            if index==0:
                unit_obj = qcol.units
            else:
                qcol.rescale(unit_obj)
            result.append(qcol.reshape((-1, 1)))
        return np.hstack(result) * unit_obj



class Query:
    def __init__(self):
        self.__select = None
        self.__from = None
        self.__where = None


    def SELECT(self, *args):
        self.__select = args
        return self


    def FROM(self, quantityframe):
        self.__from = quantityframe
        return self


    def WHERE(self, func):
        self.__where = func
        return self


    def FIRST(self):
        qf = self.__from
        fullnames = [qf.get_column_fullname(name) for name in self.__select]
        for idx, row in qf.iterrows():
            if self.__where(row):
                result = {fullname:row[fullname] for fullname in fullnames}
                return idx, QuantitySeries(result)



class Decibel:
    def __init__(self, value):
        self.__value = value
        

    @property
    def pow_ratio(self):
        return 10 ** (self.__value / 10)


    @property
    def mag_ratio(self):
        return np.sqrt(self.pow_ratio)





if __name__ == "__main__":
    unit_dict = {"(m/s)":pq.CompoundUnit("m/s")}
    qf = QuantityFrame({
        "velocity/(m/s)": [10, 20, 30],
        "distance/km": [1000, 2000, 3000], 
        "time/s": [0.1, 0.2, 0.3]}, unit_dict=unit_dict)
    print(qf[["distance/km", "time/s"]], type(qf[["distance/km", "time/s"]]))
    print(qf["velocity/(m/s)"].convert_unit('km/h'))
    print(qf.unit_dict is qf["time/s"].unit_dict)
    print(qf.unit_dict is qf[["velocity/(m/s)", "time/s"]].unit_dict)
    print(qf.qcol("velocity"))
