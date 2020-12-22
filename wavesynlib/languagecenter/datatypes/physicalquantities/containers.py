import numpy as np
from pandas import Series, DataFrame
import quantities as pq



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


    def __search_unit(self, unit_name:str):
        unit_dict = self.unit_dict
        if unit_dict and unit_name in unit_dict:
            unit_obj = unit_dict[unit_name]
        elif hasattr(pq, unit_name):
            unit_obj = getattr(pq, unit_name)
        else:
            unit_obj = pq.CompoundUnit(unit_name)
        return unit_obj


    @property
    def unit_object(self):
        name = self.name
        parts = name.split("/", 1)
        if len(parts) < 2:
            unit_obj = pq.dimensionless
        else:
            unit_name = parts[1]
            unit_obj = self.__search_unit(unit_name)
        return unit_obj


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
                raise KeyError("{name} not exists in this frame.")
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
