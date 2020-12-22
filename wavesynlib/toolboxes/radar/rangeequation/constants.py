
from numpy import pi as π
import quantities as pq



# Boltzmann's constant
k_b = 1.38e-23

# Standard temperature in kelvins
T_0 = 290

# Earth's radius in km
A_e = 6.5e3 * pq.km

# Effective radius factor
k_e = 1.333

# Standard temperature in kelvins
T_0 = 290 * pq.kelvin

# Range equation constant (for range in km)
K_r  = 1 / ((4*π)**3 * k_b * 1e12)