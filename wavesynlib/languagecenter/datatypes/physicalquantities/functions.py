from typing import Tuple, Union
import numpy as np
from numpy import pi as π
import quantities as pq



def expj(
    x:Union[float, np.ndarray, pq.Quantity]
) -> Union[float, np.ndarray]:
    if isinstance(x, pq.Quantity):
        x = x.rescale(pq.rad).magnitude
    return np.exp(1j*x)



def expj2π(x:Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    if isinstance(x, pq.Quantity):
        raise ValueError('Parameter "x" should be a normalized value rather than a quantity.')
    return np.exp(1j*2*π*x)



def modf(
    x:Union[float, np.ndarray, pq.Quantity] 
) -> Tuple[
        Union[float, np.ndarray, pq.Quantity], 
        Union[float, np.ndarray, pq.Quantity]]:

    if isinstance(x, pq.Quantity):
        x_value = x.magnitude
        x_unit  = x.units
    else:
        x_value = x
        x_unit  = 1
    results = np.modf(x_value)
    return tuple(result*x_unit for result in results)



if __name__ == "__main__":
    pass
