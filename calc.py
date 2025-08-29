import numpy as np
from scipy.constants import c
import matplotlib.pyplot as plt


L = 0.25

FSR = c/2/L
print(f"FSR = {FSR/1e6} MHz")

R = 0.4
g = 1 - L/R
print(f"g = {g}")

wl = 1064*1e-9  # wavelength in meters
waist = np.sqrt(L*wl/np.pi * np.sqrt(g/(1-g)))
print(f"waist size = {waist*1e6} um")

spot = np.sqrt(L*wl/np.pi * np.sqrt(1/g/(1-g)))
print(f"spot size = {spot*1e6} um")

delta_f = np.arccos(np.sqrt(g))/np.pi * FSR
print(f"delta_f = {delta_f/1e6} MHz")  

ratio = np.arccos(np.sqrt(g))/np.pi
print(f"ratio = {ratio}")
