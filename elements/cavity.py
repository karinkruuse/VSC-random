import numpy as np
from scipy.constants import c

class OpticalCavity:
    
    def __init__(self, wavelength=1064e-9, R=0.99, n=1, m=1):

        self.wavelength = wavelength 
        self.R = R                      # Reflectance of both mirrors
        self.T = 1 - R 
        self.r = np.sqrt(R)             # the other reflection coefficient
        self.n = n                      # index of refraction
        self.m = m                      # This is for the order of the cavity reflection inverse peak; im unsure about this
        self.L = 2 * wavelength / n * m
        self.fsr = c / (2 * self.L)
        self.const = 2 * n * self.L
        self.finesse = np.pi*np.sqrt(self.R)/(1-self.R)

    def reflection_coef(self, freq):
        temp = np.exp(-1j * self.const * 2 * np.pi / c * freq)
        return -self.r * (temp - 1) / (1 - self.R * temp)

    def forwarded_power(self, freq):
        # TODO
        return
    

