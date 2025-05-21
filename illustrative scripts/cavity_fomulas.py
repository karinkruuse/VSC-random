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

FSR = c / (2 * L) 
print("FSR is", FSR/1e6, "MHz")

finesse = FSR / cavity_linewidth
print("Finesse is", finesse)

a = - finesse/np.pi
b = - 1
d = finesse/np.pi
R1 = (-b + np.sqrt(b**2 - 4*a*d))/(2*a) # this one seems to be the "wrong one" ie its always negative
R2 = (-b - np.sqrt(b**2 - 4*a*d))/(2*a)
print("Assuming r1 = r2 = r")
print("r is", R2)

print("////////////////////////////////////")
print("Second cavity")
L2 = 200e-3  # Length of the cavity in meters
print("Cavity length is", L2, "m") 


multiplier = 5
cavity_linewidth2 = multiplier * delta_nu_laser 
print("Cavity linewidth is", cavity_linewidth2 / 1e3, "kHz")

FSR2 = c / (2 * L2) 
print("FSR is", FSR2/1e6, "MHz")

finesse2 = FSR2 / cavity_linewidth2
print("Finesse is", finesse2)

a = - finesse2/np.pi
b = - 1
d = finesse2/np.pi
R1 = (-b + np.sqrt(b**2 - 4*a*d))/(2*a) # this one seems to be the "wrong one" ie its always negative
R2 = (-b - np.sqrt(b**2 - 4*a*d))/(2*a)
print("Assuming r1 = r2 = r")
print("r is", R2)
