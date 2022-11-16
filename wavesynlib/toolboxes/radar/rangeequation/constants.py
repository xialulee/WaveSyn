from typing import Final
from numpy import pi as π
import quantities as pq



# Boltzmann's constant
k_b: Final[float] = 1.38e-23

# Earth's radius in km
A_e: Final[pq.Quantity] = 6.5e3 * pq.km

# Effective radius factor
# The so called four-thirds earth model.
# See https://en.wikipedia.org/wiki/Radar_horizon.
k_e: Final[float] = 4/3

# Standard temperature 
T_0: Final[pq.Quantity] = 290 * pq.kelvin

# Range equation constant (for range in km)
K_r: Final[pq.Quantity] = 1 / ((4*π)**3 * k_b * 1e12)
