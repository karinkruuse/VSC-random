import numpy as np
from scipy.constants import c

L = 250e-3  # Length of the cavity in meters
print("Cavity length is", L, "m")
r1 = 0.9999  # Reflectivity of the mirrors
r2 = 0.99  # Reflectivity of the other mirror
wavelength = 1064e-9  # Wavelength of the light in meters
delta_nu_laser = 3e3 # Laser linewidth in Hz

multiplier = 5
cavity_linewidth = multiplier * delta_nu_laser 
print("Cavity linewidth is", cavity_linewidth / 1e3, "kHz")

n = 1.0  
FSR = c / (2 * n * L) 

finesse = FSR / cavity_linewidth
print("Finesse is", finesse)

a = - finesse/np.pi
b = - 1
c = finesse/np.pi
R1 = (-b + np.sqrt(b**2 - 4*a*c))/(2*a) # this one seems to be the "wrong one" ie its always negative
R2 = (-b - np.sqrt(b**2 - 4*a*c))/(2*a)
print("Assuming r1 = r2 = r")
print("r is", R2)

# Whatever
tau = 1 / cavity_linewidth
finesse = 2 * np.pi * tau * FSR