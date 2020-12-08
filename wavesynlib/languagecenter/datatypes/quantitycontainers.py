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


    @property
    def quantities(self):
        unit_dict = self.unit_dict
        name = self.name
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
        return self.to_numpy() * unit_obj



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




if __name__ == "__main__":
    unit_dict = {"(m/s)":pq.CompoundUnit("m/s")}
    qf = QuantityFrame({
        "velocity/(m/s)": [10, 20, 30],
        "distance/km": [1000, 2000, 3000], 
        "time/s": [0.1, 0.2, 0.3]}, unit_dict=unit_dict)
    print(qf[["distance/km", "time/s"]], type(qf[["distance/km", "time/s"]]))
    print(qf["velocity/(m/s)"].quantities.rescale(pq.km / pq.hour))
    print(qf.unit_dict is qf["time/s"].unit_dict)
    print(qf.unit_dict is qf[["velocity/(m/s)", "time/s"]].unit_dict)