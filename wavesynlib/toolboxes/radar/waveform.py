import quantities as pq
from wavesynlib.toolboxes.emwave import constants
from wavesynlib.toolboxes.emwave.algorithms import λfT_eq



class PhaseCoded:
    def __init__(self, chipwidth: pq.Quantity, PRF:pq.Quantity=None):
        if not isinstance(chipwidth, pq.Quantity):
            # Not use *= because not supported if chipwidth is a numpy array. 
            chipwidth = chipwidth * pq.s
        self.__chipwidth = chipwidth

        if not isinstance(PRF, pq.Quantity):
            PRF *= pq.Hz
        self.__PRF = PRF


    @classmethod
    def bandwidth_to_chipwidth(cls, bandwidth):
        if not isinstance(bandwidth, pq.Quantity):
            bandwidth = bandwidth * pq.Hz
        return (1/bandwidth).rescale(pq.s)


    @classmethod
    def chipwidth_to_bandwidth(cls, chipwidth):
        if not isinstance(chipwidth, pq.Quantity):
            chipwidth = chipwidth * pq.s
        return (1/chipwidth).rescale(pq.Hz)


    @classmethod
    def range_resolution_to_bandwidth(cls, range_resolution):
        if not isinstance(range_resolution, pq.Quantity):
            range_resolution = range_resolution *pq.m
        return (constants.c / 2 / range_resolution).rescale(pq.Hz)


    @classmethod
    def bandwidth_to_range_resolution(cls, bandwidth):
        if not isinstance(bandwidth, pq.Quantity):
            bandwidth = bandwidth * pq.Hz
        return (constants.c / 2 / bandwidth).rescale(pq.m)


    @classmethod
    def range_resolution_to_chipwidth(cls, range_resolution):
        bandwidth = cls.range_resolution_to_bandwidth(range_resolution)
        return cls.bandwidth_to_chipwidth(bandwidth)


    @classmethod
    def chipwidth_to_range_resolution(cls, chipwidth):
        bandwidth = cls.chipwidth_to_bandwidth(chipwidth)
        return cls.bandwidth_to_range_resolution(bandwidth)


    @classmethod
    def PRF_to_max_unambiguous_range(cls, PRF):
        if not isinstance(PRF, pq.Quantity):
            PRF = PRF * pq.Hz
        return (constants.c / 2 / PRF).rescale(pq.m)


    @classmethod
    def max_unambiguous_range_to_PRF(cls, max_unambiguous_range):
        if not isinstance(max_unambiguous_range, pq.Quantity):
            max_unambiguous_range = max_unambiguous_range * pq.m
        return (constants.c / 2 / max_unambiguous_range).rescale(pq.Hz)


    @classmethod
    def velocity_to_Doppler(cls, velocity, λ=None, f=None, T=None):
        if not isinstance(velocity, pq.Quantity):
            velocity = velocity * pq.m/pq.s
        result = λfT_eq(λ=λ, f=f, T=T)
        λ = result.qcol("λ")[0]
        return (2*velocity / λ).rescale(pq.Hz)


    @classmethod
    def Doppler_to_velocity(cls, Doppler, λ=None, f=None, T=None):
        if not isinstance(Dopper, pq.Quantity):
            Dopper = Dopper * pq.Hz
        result = λfT_eq(λ=λ, f=f, T=T)
        λ = result.qcol("λ")[0]
        return (Doppler * λ / 2).rescale(pq.m/pq.s)


    @classmethod
    def CPI_to_velocity_resolution(cls, CPI, λ=None, f=None, T=None):
        if not isinstance(CPI, pq.Quantity):
            CPI = CPI * pq.s
        result = λfT_eq(λ=λ, f=f, T=T)
        λ = result.qcol("λ")[0]
        return (λ / 2 / CPI).rescale(pq.m/pq.s)


    @classmethod
    def velocity_resolution_to_CPI(cls, velocity_resolution, λ=None, f=None, T=None):
        if not isinstance(velocity_resolution, pq.Quantity):
            velocity_resolution = velocity_resolution * pq.m / pq.s
        result = λfT_eq(λ=λ, f=f, T=T)
        λ = result.qcol("λ")[0]
        return (λ / 2 / velocity_resolution).rescale(pq.s)


    @property
    def chipwidth(self):
        return self.__chipwidth


    @property
    def bandwidth(self):
        return (1/self.__chipwidth).rescale(pq.Hz)


    @property
    def range_resolution(self):
        return constants.c / 2 / self.bandwidth


    @property
    def max_unambiguous_range(self):
        return (constants.c / 2 / self.__PRF).rescale(pq.m)
